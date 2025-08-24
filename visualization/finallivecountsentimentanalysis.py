from flask import Flask, render_template_string, jsonify
from threading import Thread
from kafka import KafkaConsumer, KafkaProducer
from collections import Counter, deque
from datetime import datetime, timedelta
import time
import json
import praw
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
import nltk

# NLTK setup
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)

# Globals
word_counts = Counter()
sentiment_counts = Counter({"positive": 0, "neutral": 0, "negative": 0})
sliding_window = deque()
window_duration = timedelta(minutes=5)
stop_words = set(stopwords.words('english'))

# ---------- 1. Reddit Producer ----------
def start_reddit_producer():
    reddit = praw.Reddit(
        client_id="3chX336_id0fu6KT0MqUUQ",
        client_secret="1ETukBXZNJaW59Mhuvly3fhsEnzqJQ",
        user_agent="KafkaSentiment by /u/Both-Ad-406"
    )

    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    subreddit = reddit.subreddit("technology")
    print("📰 Reddit producer started...")

    for comment in subreddit.stream.comments(skip_existing=True):
        data = {
            'id': comment.id,
            'author': str(comment.author),
            'body': comment.body,
            'created_utc': comment.created_utc,
            'subreddit': comment.subreddit.display_name
        }
        producer.send("test-topic", value=data)

# ---------- 2. Kafka Consumer with Sliding Window + Sentiment ----------
def consume_messages():
    consumer = KafkaConsumer(
        'test-topic',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    global word_counts, sliding_window, sentiment_counts
    print("📊 Kafka consumer started (sliding window + sentiment)...")

    for msg in consumer:
        text = msg.value.get("body", "").lower()
        tokens = word_tokenize(text, preserve_line=True)
        words = [w for w in tokens if w.isalpha() and w not in stop_words]

        # Add to sliding window
        now = datetime.utcnow()
        sliding_window.append((now, words))
        word_counts.update(words)

        # Expire old entries
        while sliding_window and sliding_window[0][0] < now - window_duration:
            _, old_words = sliding_window.popleft()
            word_counts.subtract(old_words)

        # Limit size
        word_counts = Counter(dict(word_counts.most_common(50)))

        # Sentiment analysis
        polarity = TextBlob(text).sentiment.polarity
        if polarity > 0.1:
            sentiment_counts["positive"] += 1
        elif polarity < -0.1:
            sentiment_counts["negative"] += 1
        else:
            sentiment_counts["neutral"] += 1

# ---------- 3. Flask Web Interface ----------
@app.route('/')
def index():
    return render_template_string('''
    <html>
    <head>
        <title>Kafka Word Frequency + Sentiment</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            async function fetchWordData() {
                const response = await fetch('/data');
                return await response.json();
            }

            async function fetchSentimentData() {
                const response = await fetch('/sentiment');
                return await response.json();
            }

            async function drawCharts() {
                const wordCtx = document.getElementById('wordChart').getContext('2d');
                const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');

                let wordChart = new Chart(wordCtx, {
                    type: 'bar',
                    data: { labels: [], datasets: [{ label: 'Top Words (Last 5 Mins)', data: [], backgroundColor: 'rgba(54, 162, 235, 0.5)' }] }
                });

                let sentimentChart = new Chart(sentimentCtx, {
                    type: 'pie',
                    data: {
                        labels: ['Positive', 'Neutral', 'Negative'],
                        datasets: [{
                            label: 'Sentiment',
                            backgroundColor: ['green', 'gray', 'red'],
                            data: [0, 0, 0]
                        }]
                    }
                });

                async function updateCharts() {
                    const wordData = await fetchWordData();
                    wordChart.data.labels = wordData.words;
                    wordChart.data.datasets[0].data = wordData.counts;
                    wordChart.update();

                    const sentimentData = await fetchSentimentData();
                    sentimentChart.data.datasets[0].data = [
                        sentimentData.positive,
                        sentimentData.neutral,
                        sentimentData.negative
                    ];
                    sentimentChart.update();
                }

                setInterval(updateCharts, 5000);
                updateCharts();
            }

            window.onload = drawCharts;
        </script>
    </head>
    <body>
        <h2 style="text-align:center;">📊 Kafka Real-Time Word Frequency (5-Min Sliding Window)</h2>
        <div style="display: flex; justify-content: center;">
            <canvas id="wordChart" width="800" height="400"></canvas>
        </div>
        <h2 style="text-align:center;">🧠 Sentiment Distribution</h2>
        <div style="display: flex; justify-content: center;">
            <canvas id="sentimentChart" width="300" height="300" style="max-width: 300px; max-height: 300px;"></canvas>
        </div>
    </body>
    </html>
    ''')

@app.route('/data')
def get_data():
    top = word_counts.most_common(10)
    words, counts = zip(*top) if top else ([], [])
    return jsonify({'words': words, 'counts': counts})

@app.route('/sentiment')
def get_sentiment():
    return jsonify(sentiment_counts)

# ---------- 4. Start Everything ----------
if __name__ == '__main__':
    Thread(target=start_reddit_producer, daemon=True).start()
    Thread(target=consume_messages, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)