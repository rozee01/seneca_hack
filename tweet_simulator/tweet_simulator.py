#!/usr/bin/env python3
"""
Tweet Simulator for Social Sentiment Analysis Pipeline

This script simulates real-time tweet streaming by reading from a CSV file
and emitting tweets at a configurable rate. Perfect for testing the sentiment
analysis pipeline without needing actual API access.

Usage:
    python tweet_simulator.py --csv tweets.csv --rate 5 --output websocket
    python tweet_simulator.py --csv tweets.csv --rate 10 --output stdout
"""

import asyncio
import csv
import json
import random
import time
import argparse
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import websockets
import websockets.server
from pathlib import Path


class TweetSimulator:
    def __init__(self, csv_file: str, rate: float = 1.0, output_type: str = "stdout"):
        """
        Initialize the tweet simulator.
        
        Args:
            csv_file: Path to CSV file containing tweet data
            rate: Tweets per second to emit
            output_type: Output method - 'stdout', 'websocket', or 'file'
        """
        self.csv_file = csv_file
        self.rate = rate
        self.output_type = output_type
        self.tweets = []
        self.current_index = 0
        self.websocket_server = None
        self.connected_clients = set()
        
    def load_tweets(self) -> List[Dict[str, Any]]:
        """Load tweets from CSV file."""
        tweets = []
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Convert CSV row to tweet-like JSON structure
                    tweet = {
                        'id': row.get('id', f"sim_{random.randint(100000, 999999)}"),
                        'text': row.get('text', ''),
                        'author_id': row.get('author_id', f"user_{random.randint(1000, 9999)}"),
                        'username': row.get('username', f"user{random.randint(100, 999)}"),
                        'created_at': row.get('created_at', datetime.now(timezone.utc).isoformat()),
                        'public_metrics': {
                            'retweet_count': int(row.get('retweet_count', random.randint(0, 100))),
                            'like_count': int(row.get('like_count', random.randint(0, 500))),
                            'reply_count': int(row.get('reply_count', random.randint(0, 50))),
                            'quote_count': int(row.get('quote_count', random.randint(0, 20)))
                        },
                        'source': 'simulator',
                        'platform': 'twitter',
                        'hashtags': self._extract_hashtags(row.get('text', '')),
                        'mentions': self._extract_mentions(row.get('text', '')),
                        'raw_data': row
                    }
                    tweets.append(tweet)
            
            print(f"✅ Loaded {len(tweets)} tweets from {self.csv_file}")
            return tweets
            
        except FileNotFoundError:
            print(f"❌ Error: CSV file '{self.csv_file}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading tweets: {e}")
            sys.exit(1)
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from tweet text."""
        import re
        hashtags = re.findall(r'#\w+', text)
        return hashtags
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from tweet text."""
        import re
        mentions = re.findall(r'@\w+', text)
        return mentions
    
    async def emit_tweet(self, tweet: Dict[str, Any]) -> None:
        """Emit a single tweet based on output type."""
        tweet_json = json.dumps(tweet, ensure_ascii=False, indent=2)
        
        if self.output_type == "stdout":
            print(f"\n🐦 TWEET EMITTED:")
            print(f"   ID: {tweet['id']}")
            print(f"   User: @{tweet['username']}")
            print(f"   Text: {tweet['text'][:100]}{'...' if len(tweet['text']) > 100 else ''}")
            print(f"   Hashtags: {tweet['hashtags']}")
            print(f"   Time: {tweet['created_at']}")
            print("-" * 80)
            
        elif self.output_type == "websocket":
            # Send to all connected WebSocket clients
            if self.connected_clients:
                message = json.dumps({
                    'type': 'tweet',
                    'data': tweet,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                disconnected = set()
                for client in self.connected_clients:
                    try:
                        await client.send(message)
                    except websockets.exceptions.ConnectionClosed:
                        disconnected.add(client)
                
                # Remove disconnected clients
                self.connected_clients -= disconnected
                
        elif self.output_type == "file":
            # Append to output file
            with open("tweet_stream.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(tweet) + "\n")
    
    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections."""
        self.connected_clients.add(websocket)
        print(f"🔌 Client connected. Total clients: {len(self.connected_clients)}")
        
        try:
            # Send welcome message
            welcome = {
                'type': 'welcome',
                'message': 'Connected to Tweet Simulator',
                'rate': self.rate,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            await websocket.send(json.dumps(welcome))
            
            # Keep connection alive
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.remove(websocket)
            print(f"🔌 Client disconnected. Total clients: {len(self.connected_clients)}")
    
    async def start_websocket_server(self, host: str = "localhost", port: int = 8765):
        """Start WebSocket server for real-time streaming."""
        self.websocket_server = await websockets.server.serve(
            self.websocket_handler, host, port
        )
        print(f"🌐 WebSocket server started on ws://{host}:{port}")
        print(f"   Connect with: websocat ws://{host}:{port}")
        print(f"   Or use the WebSocket client in your dashboard")
    
    async def run_simulation(self, duration: Optional[int] = None):
        """Run the tweet simulation."""
        self.tweets = self.load_tweets()
        
        if not self.tweets:
            print("❌ No tweets loaded. Exiting.")
            return
        
        # Start WebSocket server if needed
        if self.output_type == "websocket":
            await self.start_websocket_server()
        
        print(f"\n🚀 Starting tweet simulation...")
        print(f"   Rate: {self.rate} tweets/second")
        print(f"   Output: {self.output_type}")
        print(f"   Total tweets: {len(self.tweets)}")
        print(f"   Duration: {'Infinite' if duration is None else f'{duration} seconds'}")
        print(f"\nPress Ctrl+C to stop\n")
        
        start_time = time.time()
        tweet_count = 0
        
        try:
            while True:
                # Check duration limit
                if duration and (time.time() - start_time) >= duration:
                    print(f"\n⏰ Simulation completed after {duration} seconds")
                    break
                
                # Get next tweet (cycle through the list)
                tweet = self.tweets[self.current_index].copy()
                self.current_index = (self.current_index + 1) % len(self.tweets)
                
                # Update timestamp to current time
                tweet['created_at'] = datetime.now(timezone.utc).isoformat()
                tweet['id'] = f"sim_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
                
                # Emit the tweet
                await self.emit_tweet(tweet)
                tweet_count += 1
                
                # Wait for next tweet based on rate
                if self.rate > 0:
                    await asyncio.sleep(1.0 / self.rate)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Simulation stopped by user")
        
        finally:
            if self.websocket_server:
                self.websocket_server.close()
                await self.websocket_server.wait_closed()
        
        elapsed = time.time() - start_time
        print(f"\n📊 Simulation Summary:")
        print(f"   Total tweets emitted: {tweet_count}")
        print(f"   Duration: {elapsed:.1f} seconds")
        print(f"   Average rate: {tweet_count/elapsed:.2f} tweets/second")


def main():
    parser = argparse.ArgumentParser(description="Tweet Simulator for Social Sentiment Analysis")
    parser.add_argument("--csv", required=True, help="Path to CSV file containing tweet data")
    parser.add_argument("--rate", type=float, default=1.0, help="Tweets per second (default: 1.0)")
    parser.add_argument("--output", choices=["stdout", "websocket", "file"], default="stdout",
                       help="Output method (default: stdout)")
    parser.add_argument("--duration", type=int, help="Simulation duration in seconds (default: infinite)")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket port (default: 8765)")
    
    args = parser.parse_args()
    
    # Validate CSV file exists
    if not Path(args.csv).exists():
        print(f"❌ Error: CSV file '{args.csv}' not found")
        sys.exit(1)
    
    # Create and run simulator
    simulator = TweetSimulator(args.csv, args.rate, args.output)
    
    try:
        asyncio.run(simulator.run_simulation(args.duration))
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()

