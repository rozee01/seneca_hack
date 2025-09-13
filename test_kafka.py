# test_kafka.py
from kafka import KafkaProducer, KafkaConsumer
import time

TOPIC = "test_topic"
BOOTSTRAP_SERVERS = ["localhost:9092"]

# Produce a message
producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)
producer.send(TOPIC, b"hello_kafka")
producer.flush()
print("Message sent to Kafka.")

# Consume the message
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    consumer_timeout_ms=5000
)

print("Waiting for messages...")
for msg in consumer:
    print(f"Received: {msg.value.decode()}")
    break
else:
    print("No message received.")

producer.close()
consumer.close()