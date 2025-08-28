# RedStream: Real-Time Reddit Analytics with Kafka + Flask

RedStream is a **real-time scalable analytics project** that streams Reddit comments into Apache Kafka, performs **word frequency + sentiment analysis**, and visualizes the results in a live Flask dashboard. It also includes a **scalability benchmarking module** that processes multiple datasets of different sizes to evaluate performance.

This project demonstrates **scalable cloud programming concepts** such as:

* **Stream processing**
* **Sliding window analytics**
* **Sentiment classification**
* **Horizontal scaling**
* **Batch scalability benchmarking**

---
<img width="1907" height="1004" alt="Screenshot 2025-06-26 125636" src="https://github.com/user-attachments/assets/24b2b2b7-989e-4a2a-aba7-e3f4d9f2081d" />

##  Features

* **Reddit Producer**: Streams live Reddit comments into Kafka using PRAW.
* **Kafka Consumer**: Processes comments with a **5-minute sliding window** word frequency counter.
* **Sentiment Analysis**: Classifies comments as positive, neutral, or negative using TextBlob.
* **Flask Dashboard**: Real-time charts with Chart.js (bar chart for trending words, pie chart for sentiment distribution).
* **Scalability Benchmarking**: Runs dataset benchmarking on small, medium, and large datasets to measure processing performance.

---
<img width="507" height="258" alt="image" src="https://github.com/user-attachments/assets/6ab85344-aab3-44c7-9c5e-7d5ab1a8ba57" />


##  Tech Stack

* **Python** (Flask, PRAW, NLTK, TextBlob, kafka-python, matplotlib)
* **Apache Kafka** (message broker)
* **AWS EC2** (for deployment)
* **Chart.js** (data visualization)

---

## 📂 Project Structure

```
RedStream/
│
├── data/                          # Datasets (excluded from repo due to size)
│   ├── comments_negative.csv
│   ├── kaggle_RC_2019-05.csv
│   └── Reddit_Data.csv
│
├── scalability/
│   └── scalabilityapp.py          # Script to benchmark dataset scalability
│
├── visualization/
│   └── finallivecountsentimentanalysis.py   # Flask app with Kafka producer+consumer
│
├── requirements.txt               # Python dependencies
├── README.md                      # Project documentation
└── LICENSE                        # MIT License
```

---

## ⚙️ Setup Instructions

### 1️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Download & Install Kafka

1. Download Kafka (Scala 2.13) from [Apache Kafka Downloads](https://kafka.apache.org/downloads).
2. Extract the archive, e.g. `C:\kafka\kafka_2.13-3.7.0` (Windows) or `~/kafka/kafka_2.13-3.7.0` (Linux/Mac).

---

### 3️⃣ Start Zookeeper

In one terminal:

```bash
cd kafka_2.13-3.7.0
bin/zookeeper-server-start.sh config/zookeeper.properties
```

(Windows PowerShell):

```bash
bin\windows\zookeeper-server-start.bat config\zookeeper.properties
```

---

### 4️⃣ Start Kafka Broker

In another terminal:

```bash
cd kafka_2.13-3.7.0
bin/kafka-server-start.sh config/server.properties
```

(Windows PowerShell):

```bash
bin\windows\kafka-server-start.bat config\server.properties
```

---

### 5️⃣ Create Kafka Topic

```bash
bin/kafka-topics.sh --create --topic test-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

(Windows PowerShell):

```bash
bin\windows\kafka-topics.bat --create --topic test-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

---

### 6️⃣ Run Flask App (Producer + Consumer)

```bash
cd visualization
python finallivecountsentimentanalysis.py
```

The app will start on:

```
http://127.0.0.1:5000
```

---

## 📊 Dashboard Preview

* **Bar Chart** → Top words (last 5 minutes)
* **Pie Chart** → Sentiment distribution (Positive / Neutral / Negative)

![architecture](architecture.png)

---

## 📈 Scalability Benchmarking

You can test scalability with the provided datasets by running:

```bash
cd scalability
python scalabilityapp.py
```

This script will:

* Process datasets of increasing sizes (`Reddit_Data.csv`, `kaggle_RC_2019-05.csv`, `comments_negative.csv`)
* Record processing time
* Generate scalability plot for benchmarking

---

##  Datasets

⚠️ **Note**: Large datasets are **not included in this repository** due to GitHub’s file size limits.

To run the scalability tests, please download or prepare the following CSV files and place them in the `data/` directory:

* [Reddit\_Data.csv (small)](https://drive.google.com/)  ← Replace with actual link
* [kaggle\_RC\_2019-05.csv (medium)](https://kaggle.com/) ← Replace with actual link
* [comments\_negative.csv (large)](https://drive.google.com/) ← Replace with actual link

⚠️ You may replace these with your own Reddit datasets if desired.

---

##  Example Use Cases

* Real-time monitoring of social media sentiment
* Tracking trending words in a community
* Benchmarking scalable cloud pipelines with increasing data volumes

---

##  Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to change.

---

## 📜 License

This project is licensed under the MIT License.
