"""
Simple Kafka message producer for testing WebSocket integration.
"""

import asyncio
import json
from datetime import datetime
from aiokafka import AIOKafkaProducer


async def send_test_messages():
    """Send test messages to cleaned_Liverpool topic."""
    
    producer = AIOKafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )
    
    try:
        await producer.start()
        print("✅ Connected to Kafka")
        
        # Send test messages to cleaned_Liverpool
        topic = "cleaned_Liverpool"
        
        for i in range(5):
            message = {
                "tweet_id": f"test_{i}",
                "text": f"Test message {i} for Liverpool! 🔴",
                "sentiment": 0.8,
                "user": f"test_user_{i}",
                "timestamp": datetime.now().isoformat(),
                "test_message": True
            }
            
            key = f"test_key_{i}"
            
            await producer.send_and_wait(topic, message, key=key)
            print(f"📤 Sent message {i+1} to {topic}")
            
            await asyncio.sleep(2)  # Wait 2 seconds between messages
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await producer.stop()
        print("🛑 Producer stopped")


if __name__ == "__main__":
    print("🚀 Starting Kafka test message producer")
    print("This will send 5 test messages to cleaned_Liverpool topic")
    print("Make sure:")
    print("1. Kafka is running on localhost:9092")
    print("2. Your API is running on localhost:8000") 
    print("3. WebSocket is connected to Liverpool topic")
    print()
    
    try:
        asyncio.run(send_test_messages())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"\n💥 Failed: {e}")