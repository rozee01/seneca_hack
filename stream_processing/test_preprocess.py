"""
test_spark_stream.py
--------------------
This script tests the Spark streaming preprocessing:
1. Consumes messages from the Kafka topic where Spark writes cleaned tweets.
2. Prints them to verify that Spark streaming is working correctly.
"""

from confluent_kafka import Consumer, KafkaError

# ---- Kafka consumer configuration ----
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',   # or 'sportpulse-kafka:9092' if inside Docker
    'group.id': 'spark_test_group',
    'auto.offset.reset': 'earliest'
})

# ---- Topic where Spark writes cleaned tweets ----
output_topic = "cleaned_Liverpool"
consumer.subscribe([output_topic])

print(f"Consuming messages from topic '{output_topic}' ...\nPress Ctrl+C to stop.")

try:
    while True:
        msg = consumer.poll(1.0)  # wait max 1s for a message
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                print(f"Consumer error: {msg.error()}")
            continue
        print(msg.value().decode("utf-8"))  # cleaned tweet as JSON

except KeyboardInterrupt:
    print("\nStopping consumer...")

finally:
    consumer.close()
