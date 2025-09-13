from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

from ..kafka_client import kafka_client

router = APIRouter(prefix="/kafka", tags=["Kafka Management"])


class TeamsSubscription(BaseModel):
    """Request model for subscribing to team topics."""
    teams: List[str]


@router.post("/subscribe/teams")
async def subscribe_to_teams(subscription: TeamsSubscription):
    """
    Subscribe to Kafka topics for specific teams.
    
    This will subscribe to team topics directly (e.g., Liverpool, Chelsea, etc.)
    """
    try:
        if not kafka_client.is_connected:
            # Start Kafka client if not already connected
            await kafka_client.start()
        
        await kafka_client.subscribe_to_sports_topics(subscription.teams)
        
        return {
            "status": "success",
            "message": f"Subscribed to {len(subscription.teams)} team topics",
            "teams": subscription.teams,
            "topics": subscription.teams
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to subscribe to teams: {str(e)}")


@router.get("/topics")
async def get_kafka_topics():
    """
    Get information about Kafka topics and subscriptions.
    """
    try:
        if not kafka_client.consumer:
            return {
                "status": "disconnected",
                "message": "Kafka consumer not connected",
                "subscribed_topics": []
            }
        
        metadata = await kafka_client.get_topic_metadata()
        
        current_subscription = list(kafka_client.consumer.subscription()) if kafka_client.consumer.subscription() else []
        
        return {
            "status": "connected",
            "subscribed_topics": current_subscription,
            "available_topics": metadata.get("topics", []),
            "brokers": metadata.get("brokers", []),
            "consumer_group": metadata.get("consumer_group", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get topic information: {str(e)}")


@router.post("/start")
async def start_kafka_consumer():
    """
    Start the Kafka consumer.
    """
    try:
        if kafka_client.is_connected:
            return {"status": "already_running", "message": "Kafka consumer is already running"}
        
        await kafka_client.start()
        
        return {"status": "success", "message": "Kafka consumer started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Kafka consumer: {str(e)}")


@router.post("/stop")
async def stop_kafka_consumer():
    """
    Stop the Kafka consumer.
    """
    try:
        if not kafka_client.is_connected:
            return {"status": "already_stopped", "message": "Kafka consumer is not running"}
        
        await kafka_client.stop()
        
        return {"status": "success", "message": "Kafka consumer stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop Kafka consumer: {str(e)}")


@router.get("/status")
async def get_kafka_status():
    """
    Get the current status of the Kafka consumer.
    """
    return {
        "connected": kafka_client.is_connected,
        "running": kafka_client.running,
        "consumer_active": kafka_client.consumer is not None,
        "producer_active": kafka_client.producer is not None,
    }

@router.post("/start-consumption")
async def start_message_consumption():
    """
    Start consuming messages from subscribed topics.
    """
    try:
        if not kafka_client.is_connected:
            await kafka_client.start()
        
        # Start consuming messages in background
        import asyncio
        asyncio.create_task(kafka_client.consume_messages())
        
        return {
            "status": "success",
            "message": "Message consumption started",
            "running": kafka_client.running
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start message consumption: {str(e)}")