"""
Simple WebSocket test client for testing Kafka stream integration.
"""

import asyncio
import json
import websockets
from datetime import datetime


async def test_websocket_connection():
    """Test WebSocket connection to specific topic."""
    uri = "ws://localhost:8000/api/v1/ws/kafka/Liverpool"
    
    print(f"🔌 Connecting to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Send a ping to test bidirectional communication
            ping_message = {
                "type": "ping",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(ping_message))
            print(f"📤 Sent ping: {ping_message}")
            
            # Listen for messages for 30 seconds
            print("👂 Listening for messages (30 seconds)...")
            
            timeout = 30
            start_time = asyncio.get_event_loop().time()
            
            while True:
                try:
                    # Wait for message with timeout
                    remaining_time = timeout - (asyncio.get_event_loop().time() - start_time)
                    if remaining_time <= 0:
                        print("⏰ Timeout reached")
                        break
                    
                    message = await asyncio.wait_for(websocket.recv(), timeout=remaining_time)
                    data = json.loads(message)
                    
                    print(f"📥 Received message at {datetime.now().strftime('%H:%M:%S')}:")
                    print(f"   Topic: {data.get('topic', 'N/A')}")
                    print(f"   Type: {data.get('type', 'kafka_message')}")
                    print(f"   Content: {json.dumps(data, indent=2)}")
                    print("-" * 50)
                    
                except asyncio.TimeoutError:
                    print("⏰ No messages received in the last few seconds")
                    break
                except websockets.exceptions.ConnectionClosed:
                    print("❌ Connection closed by server")
                    break
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
                    
    except Exception as e:
        print(f"❌ Failed to connect: {e}")


async def test_all_topics():
    """Test WebSocket connection to all topics."""
    uri = "ws://localhost:8000/api/v1/ws/kafka/all"
    
    print(f"🔌 Connecting to ALL topics: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to all topics!")
            
            # Send a ping
            ping_message = {"type": "ping", "timestamp": datetime.now().isoformat()}
            await websocket.send(json.dumps(ping_message))
            print(f"📤 Sent ping: {ping_message}")
            
            # Listen for messages
            print("👂 Listening for messages from all topics (30 seconds)...")
            
            timeout = 30
            start_time = asyncio.get_event_loop().time()
            
            while True:
                try:
                    remaining_time = timeout - (asyncio.get_event_loop().time() - start_time)
                    if remaining_time <= 0:
                        break
                    
                    message = await asyncio.wait_for(websocket.recv(), timeout=remaining_time)
                    data = json.loads(message)
                    
                    print(f"📥 Message from topic '{data.get('topic', 'unknown')}':")
                    print(f"   {json.dumps(data, indent=2)}")
                    print("-" * 50)
                    
                except asyncio.TimeoutError:
                    print("⏰ No messages received")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    break
                    
    except Exception as e:
        print(f"❌ Failed to connect: {e}")


async def test_health_endpoint():
    """Test the health endpoint."""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/api/v1/ws/health') as response:
                data = await response.json()
                print("🏥 Health Check Result:")
                print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"❌ Health check failed: {e}")


async def main():
    """Run all tests."""
    print("🧪 Starting WebSocket Tests\n")
    
    # Test 1: Health endpoint
    print("=" * 60)
    print("TEST 1: Health Endpoint")
    print("=" * 60)
    await test_health_endpoint()
    
    await asyncio.sleep(2)
    
    # Test 2: Single topic connection
    print("\n" + "=" * 60)
    print("TEST 2: Single Topic Connection (Liverpool)")
    print("=" * 60)
    await test_websocket_connection()
    
    await asyncio.sleep(2)
    
    # Test 3: All topics connection
    print("\n" + "=" * 60)
    print("TEST 3: All Topics Connection")
    print("=" * 60)
    await test_all_topics()
    
    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    print("🚀 WebSocket Test Client")
    print("Make sure your API is running on localhost:8000")
    print("And that Kafka is running with some test data")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Tests stopped by user")
    except Exception as e:
        print(f"\n💥 Test failed: {e}")