import csv
import json
import argparse
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from confluent_kafka import Producer


def load_rows(csv_files: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    print(f"Loaded {len(rows)} rows from {len(csv_files)} files.")
    return rows


def delivery_report(err, msg):
    """ Called once for each produced message to indicate delivery result. """
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")


async def emit_rows(rows: List[Dict[str, Any]], rate: float, producer: Producer):
    idx = 0
    total = len(rows)
    while True:
        row = rows[idx % total]
        topic = row["file_name"].replace(" ", "_")  # use team name as topic, replace spaces
        value = json.dumps(row, ensure_ascii=False)

        producer.produce(
            topic=topic,
            value=value.encode("utf-8"),
            callback=delivery_report
        )
        producer.poll(0)  # trigger delivery callbacks

        print(f"Sent tweet to topic={topic}: {row['text'][:50]}...")

        idx += 1
        await asyncio.sleep(1.0 / rate)


def main():
    parser = argparse.ArgumentParser(description="Tweet Flow Simulator -> Kafka")
    parser.add_argument("--csv", nargs='+', required=True, help="Paths to CSV files")
    parser.add_argument("--rate", type=float, default=1.0, help="Tweets per second")
    parser.add_argument("--broker", type=str, default="localhost:9092", help="Kafka broker address")
    args = parser.parse_args()

    for csv_file in args.csv:
        if not Path(csv_file).exists():
            print(f"Error: CSV file '{csv_file}' not found")
            return

    rows = load_rows(args.csv)
    if not rows:
        print("No rows found in provided files.")
        return

    # Kafka producer config
    conf = {"bootstrap.servers": args.broker}
    producer = Producer(conf)

    try:
        asyncio.run(emit_rows(rows, args.rate, producer))
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        producer.flush()  # make sure all messages are sent


if __name__ == "__main__":
    main()
