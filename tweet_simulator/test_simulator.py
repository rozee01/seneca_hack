#!/usr/bin/env python3
"""
Test script for the Tweet Simulator

This script demonstrates how to use the tweet simulator and test its functionality.
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path


def test_csv_loading():
    """Test if the CSV file can be loaded properly."""
    print("🧪 Testing CSV loading...")
    
    csv_file = Path("tweet_simulator/sample_tweets.csv")
    if not csv_file.exists():
        print("❌ sample_tweets.csv not found")
        return False
    
    try:
        import csv
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            tweets = list(reader)
            print(f"✅ Loaded {len(tweets)} tweets from CSV")
            return True
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return False


def test_simulator_import():
    """Test if the simulator can be imported."""
    print("🧪 Testing simulator import...")
    
    try:
        from tweet_simulator import TweetSimulator
        print("✅ TweetSimulator imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


async def test_websocket_connection():
    """Test WebSocket connection."""
    print("🧪 Testing WebSocket connection...")
    
    try:
        import websockets
        
        # Start simulator in background
        process = subprocess.Popen([
            sys.executable, "tweet_simulator/tweet_simulator.py", 
            "--csv", "tweet_simulator/sample_tweets.csv", 
            "--rate", "1", 
            "--output", "websocket",
            "--duration", "5"
        ])
        
        # Wait for server to start
        await asyncio.sleep(2)
        
        # Connect to WebSocket
        uri = "ws://localhost:8765"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection successful")
            
            # Wait for welcome message first
            welcome_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            welcome_data = json.loads(welcome_message)
            
            if welcome_data.get('type') == 'welcome':
                print("✅ Received welcome message")
                
                # Wait for a tweet
                tweet_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                tweet_data = json.loads(tweet_message)
                
                if tweet_data.get('type') == 'tweet':
                    print("✅ Received tweet via WebSocket")
                    print(f"   Tweet: {tweet_data['data']['text'][:50]}...")
                    return True
                else:
                    print(f"❌ Unexpected message type: {tweet_data.get('type')}")
                    return False
            else:
                print(f"❌ Expected welcome message, got: {welcome_data.get('type')}")
                return False
                
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False
    finally:
        # Clean up process
        if 'process' in locals():
            process.terminate()
            process.wait()


def run_quick_demo():
    """Run a quick demonstration of the simulator."""
    print("\n🚀 Running Quick Demo...")
    print("This will emit 3 tweets at 1 tweet per second to the console")
    print("Press Ctrl+C to stop early\n")
    
    try:
        subprocess.run([
            sys.executable, "tweet_simulator/tweet_simulator.py",
            "--csv", "tweet_simulator/sample_tweets.csv",
            "--rate", "10",
            "--output", "stdout",
            "--duration", "5"
        ])
        print("\n✅ Demo completed successfully")
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")


async def main():
    """Run all tests."""
    print("🧪 Tweet Simulator Test Suite")
    print("=" * 50)
    
    tests = [
        ("CSV Loading", test_csv_loading),
        ("Simulator Import", test_simulator_import),
        ("WebSocket Connection", test_websocket_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The simulator is ready to use.")
        
        # Ask if user wants to see a demo
        try:
            response = input("\nWould you like to see a quick demo? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                run_quick_demo()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

