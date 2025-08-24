# scalability_app.py (Enhanced with Latency Measurement)
import os
import time
import json
import io
import csv
import nltk
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template_string, send_file
from nltk.corpus import stopwords
from nltk.tokenize import TreebankWordTokenizer
from collections import Counter

# ✅ Only lightweight downloads
nltk.download('stopwords')

tokenizer = TreebankWordTokenizer()
stop_words = set(stopwords.words('english'))

app = Flask(__name__)
SCALABILITY_DATA_FILE = 'scalability_data.json'
DATASETS = [
    'Reddit_Data.csv',
    'kaggle_RC_2019-05.csv',
    'comments_negative.csv'
]

def process_file(filename):
    print(f"📁 Processing: {filename}")
    start_time = time.time()
    word_counts = Counter()
    rows_processed = 0

    try:
        df = pd.read_csv(filename, on_bad_lines='skip', low_memory=False)
        text_column = df.columns[0]
        texts = df[text_column].dropna()
        rows_processed = len(texts)

        for text in texts:
            try:
                tokens = tokenizer.tokenize(str(text).lower())
                filtered = [word for word in tokens if word.isalpha() and word not in stop_words]
                word_counts.update(filtered)
            except Exception as e:
                print(f"⚠️ Error processing text: {e}")
    except Exception as e:
        print(f"❌ Error reading file {filename}: {e}")
        return None

    duration = time.time() - start_time
    latency = duration / rows_processed if rows_processed > 0 else 0
    size_mb = os.path.getsize(filename) / (1024 * 1024)

    print(f"✅ Done in {duration:.2f} seconds")
    return {
        'dataset': filename,
        'size_mb': round(size_mb),
        'time_sec': round(duration, 2),
        'rows': rows_processed,
        'latency_ms': round(latency * 1000, 4)  # latency per row in ms
    }

def run_all():
    results = []
    for file in DATASETS:
        result = process_file(file)
        if result:
            results.append(result)
    with open(SCALABILITY_DATA_FILE, 'w') as f:
        json.dump(results, f, indent=2)

@app.route('/')
def index():
    return render_template_string("""
        <h2>📈 Scalability Chart: Dataset Size vs. Processing Time</h2>
        <img src="/plot.png" alt="Scalability Chart">
    """)

@app.route('/plot.png')
def plot_png():
    if not os.path.exists(SCALABILITY_DATA_FILE):
        return "❌ Error: No scalability data found."

    try:
        with open(SCALABILITY_DATA_FILE, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return f"❌ Failed to read scalability data: {str(e)}"

    if not data:
        return "❌ No data to display."

    data.sort(key=lambda x: x['size_mb'])
    datasets = [d['dataset'] for d in data]
    sizes = [d['size_mb'] for d in data]
    times = [d['time_sec'] for d in data]
    latencies = [d['latency_ms'] for d in data]
    rows = [d['rows'] for d in data]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(sizes, times, marker='o', linestyle='-', linewidth=2)

    for size, time_val, latency_val, row_count, label in zip(sizes, times, latencies, rows, datasets):
        ax.annotate(
            f"{label}\n{time_val:.2f}s\n{row_count} rows\n{latency_val:.2f}ms/row",
            (size, time_val), textcoords="offset points", xytext=(0, 10), ha='center'
        )

    ax.set_title('Scalability of Static Visualizer by Dataset Size')
    ax.set_xlabel('Dataset Size (MB)')
    ax.set_ylabel('Processing Time (seconds)')
    ax.grid(True)
    ax.set_xticks(sizes)
    ax.set_yticks(range(0, int(max(times)) + 50, 50))

    buf = io.BytesIO()
    fig.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    print("⚙️ Starting dataset processing...")
    run_all()
    print("🚀 Launching web app...")
    app.run(host='0.0.0.0', port=5050)