"""
WebSocket routes for real-time Kafka stream access.
"""

import asyncio
import json
import logging
from typing import Dict, Set
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, topic: str):
        """Accept WebSocket connection and add to topic group."""
        await websocket.accept()
        if topic not in self.active_connections:
            self.active_connections[topic] = set()
        self.active_connections[topic].add(websocket)
        logger.info(f"WebSocket connected to topic: {topic}")
        
    def disconnect(self, websocket: WebSocket, topic: str):
        """Remove WebSocket connection from topic group."""
        if topic in self.active_connections:
            self.active_connections[topic].discard(websocket)
            if not self.active_connections[topic]:
                del self.active_connections[topic]
        logger.info(f"WebSocket disconnected from topic: {topic}")
        
    async def send_to_topic(self, message: dict, topic: str):
        """Send message to all WebSockets connected to a topic."""
        if topic in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[topic]:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_text(json.dumps(message))
                    else:
                        dead_connections.add(connection)
                except Exception as e:
                    logger.error(f"Error sending to WebSocket: {e}")
                    dead_connections.add(connection)
            
            # Clean up dead connections
            for dead_conn in dead_connections:
                self.active_connections[topic].discard(dead_conn)

manager = ConnectionManager()

@router.websocket("/ws/kafka/{topic}")
async def websocket_kafka_stream(websocket: WebSocket, topic: str):
    """
    WebSocket endpoint for streaming Kafka messages for a specific topic.
    """
    await manager.connect(websocket, topic)
    
    try:
        # Import here to avoid circular imports
        from ..kafka_client import kafka_client
        
        # Ensure Kafka consumer is started and connected
        if not kafka_client.is_connected:
            await kafka_client.start()
        
        # Convert topic to team name for subscription
        if topic.startswith('cleaned_'):
            team_name = topic.replace('cleaned_', '')
        else:
            team_name = topic
        
        # Subscribe to the team topic using existing logic
        await kafka_client.subscribe_to_sports_topics([team_name])
        
        # Start message consumption if not already running
        if not kafka_client.running:
            import asyncio
            asyncio.create_task(kafka_client.consume_messages())
        
        # Register WebSocket handler for this topic  
        def create_ws_handler(ws_topic):
            async def ws_handler(message_data):
                await manager.send_to_topic(message_data, ws_topic)
            return ws_handler
        
        kafka_client.register_websocket_handler(team_name, create_ws_handler(topic))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (optional - for bidirectional communication)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle client messages if needed
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket communication: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, topic)

@router.websocket("/ws/kafka/all")
async def websocket_all_kafka_streams(websocket: WebSocket):
    """
    WebSocket endpoint for streaming all Kafka messages from all topics.
    """
    await manager.connect(websocket, "all")
    
    try:
        from ..kafka_client import kafka_client
        
        # Ensure Kafka consumer is started and connected
        if not kafka_client.is_connected:
            await kafka_client.start()
        
        # Subscribe to all team topics using existing logic
        all_teams = [
            'Liverpool', 'Chelsea', 'Arsenal', 'ManchesterUnited', 'TottenhamHotspur', 
            'Everton', 'LeicesterCity', 'AFC_Bournemouth', 'Southampton'
        ]
        await kafka_client.subscribe_to_sports_topics(all_teams)
        
        # Start message consumption if not already running
        if not kafka_client.running:
            import asyncio
            asyncio.create_task(kafka_client.consume_messages())
        
        # Register WebSocket handler for all teams
        def create_all_handler():
            async def ws_handler(message_data):
                # Add topic info for all streams
                enhanced_message = {
                    "stream_type": "all",
                    **message_data
                }
                await manager.send_to_topic(enhanced_message, "all")
            return ws_handler
        
        # Register for all teams
        for team in all_teams:
            kafka_client.register_websocket_handler(team, create_all_handler())
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket communication: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, "all")

# Health check for WebSocket
@router.get("/ws/health")
async def websocket_health():
    """Health check for WebSocket service."""
    from ..kafka_client import kafka_client
    
    result = {
        "status": "healthy",
        "active_connections": {
            topic: len(connections) 
            for topic, connections in manager.active_connections.items()
        },
        "kafka_status": {
            "connected": kafka_client.is_connected,
            "running": kafka_client.running,
            "subscribed_topics": list(kafka_client.consumer.subscription()) if kafka_client.consumer and kafka_client.consumer.subscription() else [],
            "websocket_handlers": list(kafka_client.websocket_handlers.keys())
        }
    }
    
    # Return with CORS headers for local testing
    response = JSONResponse(content=result)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@router.post("/ws/test-send/{topic}")
async def test_send_message(topic: str):
    """Test endpoint to send a message to WebSocket clients."""
    test_message = {
        "topic": topic,
        "message": {
            "test": True,
            "content": f"Test message for {topic}",
            "timestamp": asyncio.get_event_loop().time()
        },
        "key": "test_key",
        "timestamp": int(asyncio.get_event_loop().time() * 1000),
        "received_at": datetime.now().isoformat()
    }
    
    await manager.send_to_topic(test_message, topic)
    
    result = {
        "status": "sent",
        "message": "Test message sent to WebSocket clients",
        "topic": topic,
        "active_connections": len(manager.active_connections.get(topic, []))
    }
    
    # Return with CORS headers for local testing
    response = JSONResponse(content=result)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response