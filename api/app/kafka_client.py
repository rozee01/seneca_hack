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
                request_timeout_ms=30000,
            )
            await self.producer.start()
            
            
            self.consumer = AIOKafkaConsumer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
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
            logger.info(f"Kafka connections established - "
                       f"Bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}")
            
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
    
    async def subscribe_to_sports_topics(self, team_names: List[str]) -> None:
        """Subscribe to sports topics dynamically."""
        if not self.consumer:
            logger.error("Consumer not initialized")
            return
            
        # Topics are just team names, not prefixed with "cleaned_"
        sports_topics = team_names
        
        try:
            # Get current subscription
            current_topics = self.consumer.subscription()
            if current_topics:
                # Add new sports topics to existing subscription
                all_topics = list(current_topics) + sports_topics
            else:
                all_topics = sports_topics
            
            # Remove duplicates
            all_topics = list(set(all_topics))
            
            # Subscribe to all topics
            self.consumer.subscribe(all_topics)
            logger.info(f"Subscribed to sports topics: {sports_topics}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to sports topics: {str(e)}")
    
    async def handle_sports_topic_message(self, topic: str, message: Dict[str, Any], key: Optional[str], timestamp: int) -> None:
        """Handle messages from sports topics."""
        # Check if this is a sports topic (team names like Liverpool, Chelsea, etc.)
        known_teams = [
            'Liverpool', 'Chelsea', 'Arsenal', 'ManchesterUnited', 'TottenhamHotspur', 
            'Everton', 'LeicesterCity', 'AFC_Bournemouth', 'Southampton'
        ]
        
        if topic in known_teams:
            from .sports_processor import sports_processor
            await sports_processor.process_sports_message(message, topic, key, timestamp)
        else:
            # Handle other specific topics
            if topic in self.message_handlers:
                for handler in self.message_handlers[topic]:
                    try:
                        await handler(message, key, timestamp)
                    except Exception as e:
                        logger.error(f"Error in message handler for topic {topic}: {str(e)}")
            else:
                logger.warning(f"No handlers registered for topic: {topic}")
    
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
                    logger.error(f"Error processing message from topic {message.topic}, partition {message.partition}, offset {message.offset}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in message consumption loop: {str(e)}")
            raise
        finally:
            logger.info("Message consumption stopped")
    
    async def _process_message(self, message) -> None:
        """Process a single Kafka message."""
        try:
            topic = message.topic
            
            # Log raw message details
            logger.info(f"📨 RAW KAFKA MESSAGE:")
            logger.info(f"   Topic: {topic}")
            logger.info(f"   Partition: {message.partition}")
            logger.info(f"   Offset: {message.offset}")
            logger.info(f"   Timestamp: {message.timestamp}")
            logger.info(f"   Key: {message.key}")
            logger.info(f"   Value (raw): {message.value}")
            
            # Handle message parsing - check if it's already parsed or needs parsing
            try:
                if isinstance(message.value, dict):
                    # Already parsed by value_deserializer
                    data = message.value
                    logger.info(f"   Message already parsed as dict")
                elif isinstance(message.value, (bytes, str)):
                    # Need to parse JSON
                    if isinstance(message.value, bytes):
                        data = json.loads(message.value.decode('utf-8'))
                    else:
                        data = json.loads(message.value)
                    logger.info(f"   Message parsed from bytes/string")
                else:
                    logger.error(f"Unknown message value type: {type(message.value)}")
                    return
                    
                logger.info(f"   Parsed Data: {json.dumps(data, indent=4)}")
            except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as e:
                logger.error(f"Failed to decode message from topic {topic}: {str(e)}")
                return
            
            # Handle key parsing
            if isinstance(message.key, bytes):
                key = message.key.decode('utf-8')
            elif isinstance(message.key, str):
                key = message.key
            else:
                key = None
                
            timestamp = message.timestamp
            
            # Use the new unified handler
            await self.handle_sports_topic_message(topic, data, key, timestamp)
            
        except Exception as e:
            logger.error(f"Error processing message from topic {topic}: {str(e)}")
    
    async def get_topic_metadata(self) -> Dict[str, Any]:
        """Get metadata about Kafka topics."""
        try:
            # Since we know the available topics from our Kafka setup, return them directly
            # In a production system, you'd want to dynamically fetch these
            known_topics = [
                'Liverpool', 'Chelsea', 'Arsenal', 'ManchesterUnited', 'TottenhamHotspur', 
                'Everton', 'LeicesterCity', 'AFC_Bournemouth', 'Southampton',
            ]
            
            return {
                "topics": known_topics,
                "brokers": [settings.KAFKA_BOOTSTRAP_SERVERS],
                "consumer_group": getattr(settings, 'KAFKA_GROUP_ID', 'default-group'),
                "connected": self.is_connected
            }
        except Exception as e:
            logger.error(f"Failed to get topic metadata: {str(e)}")
            return {
                "topics": [],
                "brokers": [settings.KAFKA_BOOTSTRAP_SERVERS],
                "consumer_group": getattr(settings, 'KAFKA_GROUP_ID', 'default-group'),
                "connected": self.is_connected,
                "error": str(e)
            }


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
    logger.info(f"Processing sentiment message: {message.get('id')} from {message.get('platform')} with score {message.get('sentiment_score')}")


async def handle_raw_social_message(message: Dict[str, Any], key: Optional[str], timestamp: int) -> None:
    """Handle raw social media messages."""
    logger.info(f"Processing raw social message: {message.get('id')} from {message.get('platform')}")