"""
Kafka client for message streaming.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError

from .config import settings

logger = logging.getLogger(__name__)


class KafkaClient:
    """Kafka client for producing and consuming messages."""
    
    def __init__(self):
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.producer: Optional[AIOKafkaProducer] = None
        self.is_connected = False
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.running = False
        
    async def start(self) -> None:
        """Start Kafka connections."""
        try:
            # Start producer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                retry_backoff_ms=1000,
                request_timeout_ms=30000,
                max_block_ms=10000,
            )
            await self.producer.start()
            
            # Start consumer
            self.consumer = AIOKafkaConsumer(
                settings.KAFKA_TOPIC_SENTIMENT,
                settings.KAFKA_TOPIC_RAW,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_GROUP_ID,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                max_poll_records=100,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
            )
            await self.consumer.start()
            
            self.is_connected = True
            self.running = True
            logger.info("Kafka connections established", 
                       bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                       topics=[settings.KAFKA_TOPIC_SENTIMENT, settings.KAFKA_TOPIC_RAW])
            
        except Exception as e:
            logger.error(f"Failed to start Kafka connections: {str(e)}")
            raise
    
    async def stop(self) -> None:
        """Stop Kafka connections."""
        self.running = False
        
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")
            
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
            
        self.is_connected = False
        logger.info("Kafka connections closed")
    
    async def produce_message(self, topic: str, message: Dict[str, Any], key: Optional[str] = None) -> None:
        """Produce a message to a Kafka topic."""
        if not self.producer or not self.is_connected:
            raise RuntimeError("Kafka producer not connected")
        
        try:
            # Add metadata to message
            message_with_metadata = {
                **message,
                "produced_at": datetime.now(timezone.utc).isoformat(),
                "producer_id": "sentiment-api"
            }
            
            await self.producer.send_and_wait(topic, message_with_metadata, key=key)
            logger.debug(f"Message produced to {topic} with key {key}, message_id: {message.get('id')}")
            
        except KafkaError as e:
            logger.error(f"Failed to produce message to {topic}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error producing message to {topic}: {str(e)}")
            raise
    
    def register_message_handler(self, topic: str, handler: Callable) -> None:
        """Register a message handler for a specific topic."""
        if topic not in self.message_handlers:
            self.message_handlers[topic] = []
        self.message_handlers[topic].append(handler)
        logger.info(f"Message handler registered for topic {topic}: {handler.__name__}")
    
    async def consume_messages(self) -> None:
        """Main message consumption loop."""
        if not self.consumer or not self.is_connected:
            raise RuntimeError("Kafka consumer not connected")
        
        logger.info("Starting message consumption")
        
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    await self._process_message(message)
                except Exception as e:
                    logger.error("Error processing message", 
                               topic=message.topic,
                               partition=message.partition,
                               offset=message.offset,
                               error=str(e))
                    continue
                    
        except Exception as e:
            logger.error(f"Error in message consumption loop: {str(e)}")
            raise
        finally:
            logger.info("Message consumption stopped")
    
    async def _process_message(self, message) -> None:
        """Process a single Kafka message."""
        topic = message.topic
        handlers = self.message_handlers.get(topic, [])
        
        if not handlers:
            logger.warning(f"No handlers registered for topic: {topic}")
            return
        
        # Process message with all registered handlers
        for handler in handlers:
            try:
                await handler(message.value, message.key, message.timestamp)
            except Exception as e:
                logger.error("Handler failed", 
                           topic=topic,
                           handler=handler.__name__,
                           error=str(e))
    
    async def get_topic_metadata(self) -> Dict[str, Any]:
        """Get metadata about Kafka topics."""
        if not self.consumer:
            raise RuntimeError("Kafka consumer not connected")
        
        try:
            metadata = self.consumer.cluster
            return {
                "topics": list(metadata.topics.keys()),
                "brokers": [f"{broker.host}:{broker.port}" for broker in metadata.brokers.values()],
                "consumer_group": settings.KAFKA_GROUP_ID,
                "connected": self.is_connected
            }
        except Exception as e:
            logger.error(f"Failed to get topic metadata: {str(e)}")
            raise


# Global Kafka client instance
kafka_client = KafkaClient()


@asynccontextmanager
async def get_kafka_client():
    """Context manager for Kafka operations."""
    if not kafka_client.is_connected:
        await kafka_client.start()
    
    try:
        yield kafka_client
    finally:
        # Don't close connections here as they might be used elsewhere
        pass


async def start_kafka_consumer() -> None:
    """Start the Kafka consumer in the background."""
    await kafka_client.start()
    
    # Start consumption in background task
    asyncio.create_task(kafka_client.consume_messages())


async def stop_kafka_consumer() -> None:
    """Stop the Kafka consumer."""
    await kafka_client.stop()


# Example message handlers
async def handle_sentiment_message(message: Dict[str, Any], key: Optional[str], timestamp: int) -> None:
    """Handle sentiment analysis messages."""
    logger.info("Processing sentiment message", 
               message_id=message.get("id"),
               platform=message.get("platform"),
               sentiment_score=message.get("sentiment_score"))


async def handle_raw_social_message(message: Dict[str, Any], key: Optional[str], timestamp: int) -> None:
    """Handle raw social media messages."""
    logger.info("Processing raw social message", 
               message_id=message.get("id"),
               platform=message.get("platform"))


# Register message handlers
def register_kafka_handlers() -> None:
    """Register all Kafka message handlers."""
    kafka_client.register_message_handler(settings.KAFKA_TOPIC_SENTIMENT, handle_sentiment_message)
    kafka_client.register_message_handler(settings.KAFKA_TOPIC_RAW, handle_raw_social_message)
