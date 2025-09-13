# Sportpulse Web App & API

## Overview
**Sportpulse** is a real-time and batch analytics platform for **Football and NBA** data. It leverages a **Lambda architecture** to provide:

- Real-time sentiment analysis on team tweets.
- Batch processing for historical data.
- Insights via a **web dashboard** with live updates.

---

## Architecture

The platform consists of three main layers:

### 1. Streaming Layer (Real-Time)
- Simulated team tweets sent to Kafka topics per team.
- Spark Streaming cleans data and performs sentiment analysis using a pretrained model.
- Results are stored in **MongoDB** and published to Kafka for the web app.
- NBA tweets dataset: [Kaggle NBA Tweets](https://www.kaggle.com/datasets/wjia26/nba-tweets/data)
- Football tweets dataset: [Kaggle EPL Tweets](https://www.kaggle.com/code/eliasdabbas/tweets-of-top-european-football-soccer-clubs)

### 2. Batch Layer
- Historical CSV/JSON data processed with Spark Batch.
- Results are stored in **Postgres** for analytics and reporting.
- NBA stats: [Google Drive Link](https://drive.google.com/file/d/1DQVO-gab-zRC9bGsy_vr12crctgtwCyl/view?usp=sharing)
- Football stats: [Google Drive Link](https://drive.google.com/drive/u/0/folders/1vkghI2vz0u7ID_ZbFdbFrkYwMMNg3sDE)

### 3. Serving Layer / Web App Backend
- Consumes Kafka streams via WebSockets.
- Fetches batch statistics from Postgres.
- Provides a **real-time dashboard** displaying sentiment and team analytics.

---

## Architecture Diagram

```mermaid
flowchart LR
    subgraph Streaming_Layer["Streaming Layer (Real-Time)"]
        direction TB
        A[Simulated Tweets] -->|Team_name| B[Streaming Processing & Sentiment Analysis]
        B --> D[Atlas MongoDB]
    end

    subgraph Batch_Layer["Batch Layer"]
        direction TB
        H[CSV & JSON Batch Data] --> J[Spark Batch Preprocessing]
        J --> K[Postgres DB]
    end

    subgraph Serving_Layer["Web App Backend & Dashboard"]
        direction TB
        B -->|Clean_Team_name| L[Web App Backend]
        K -->|Batch Stats| L
        L --> M[Real-Time Dashboard]
    end

    classDef db fill:#d5f5e3 stroke:#27ae60 stroke-width:2px,stroke-dasharray:5 5;
    classDef compute fill:#d6eaf8 stroke:#2980b9 stroke-width:2px,stroke-dasharray:5 5;
    classDef streaming fill:#fcf3cf stroke:#f1c40f stroke-width:2px,stroke-dasharray:5 5;

    class D,K db;
    class B,J,L compute;
    class A streaming;
