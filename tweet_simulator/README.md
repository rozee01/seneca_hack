# Tweet Simulator

A Python script that simulates real-time tweet streaming for testing social sentiment analysis pipelines. This tool reads tweet data from a CSV file and emits tweets at a configurable rate, perfect for development and testing without needing actual API access.

## Features

- **Configurable Rate**: Set tweets per second (0.1 to 100+)
- **Multiple Output Methods**: 
  - `stdout`: Print tweets to console
  - `websocket`: Stream via WebSocket for real-time dashboards
  - `file`: Save to JSONL file
- **Realistic Data**: Includes sentiment scores, hashtags, mentions, and engagement metrics
- **Cycling**: Automatically cycles through tweet data for continuous streaming
- **WebSocket Server**: Built-in WebSocket server for real-time dashboard integration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run with Sample Data

```bash
# Emit 5 tweets per second to console
python tweet_simulator.py --csv sample_tweets.csv --rate 5 --output stdout

# Stream via WebSocket (for dashboard integration)
python tweet_simulator.py --csv sample_tweets.csv --rate 2 --output websocket

# Save to file
python tweet_simulator.py --csv sample_tweets.csv --rate 1 --output file
```

### 3. Connect to WebSocket Stream

If using WebSocket output, connect to `ws://localhost:8765` to receive real-time tweet data.

## Usage

```bash
python tweet_simulator.py [OPTIONS]

Options:
  --csv PATH        Path to CSV file containing tweet data (required)
  --rate FLOAT      Tweets per second (default: 1.0)
  --output METHOD   Output method: stdout, websocket, file (default: stdout)
  --duration INT    Simulation duration in seconds (default: infinite)
  --port INT        WebSocket port (default: 8765)
```

## CSV Format

The CSV file should contain the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `id` | Unique tweet ID | `1234567890` |
| `text` | Tweet content | `"Amazing match! #LoLWorlds"` |
| `author_id` | Author user ID | `user_001` |
| `username` | Author username | `esports_fan` |
| `created_at` | Timestamp | `2024-12-09T20:30:00Z` |
| `retweet_count` | Number of retweets | `45` |
| `like_count` | Number of likes | `234` |
| `reply_count` | Number of replies | `12` |
| `quote_count` | Number of quote tweets | `8` |
| `sentiment_score` | Sentiment score (-1 to 1) | `0.8` |

## Output Formats

### Console Output (stdout)
```
🐦 TWEET EMITTED:
   ID: sim_1702147200_1234
   User: @liquid_fan
   Text: Just watched the most incredible match! @TeamLiquid absolutely dominated! #LoLWorlds #esports
   Sentiment: 0.80
   Hashtags: ['#LoLWorlds', '#esports']
   Time: 2024-12-09T20:30:00Z
--------------------------------------------------------------------------------
```

### WebSocket Output
```json
{
  "type": "tweet",
  "data": {
    "id": "sim_1702147200_1234",
    "text": "Amazing match! #LoLWorlds",
    "username": "esports_fan",
    "sentiment_score": 0.8,
    "hashtags": ["#LoLWorlds"],
    "mentions": ["@TeamLiquid"],
    "public_metrics": {
      "retweet_count": 45,
      "like_count": 234,
      "reply_count": 12,
      "quote_count": 8
    }
  },
  "timestamp": "2024-12-09T20:30:00Z"
}
```

### File Output (JSONL)
Each tweet is written as a separate JSON line to `tweet_stream.jsonl`.

## Integration with Sentiment Pipeline

This simulator is designed to work with your sentiment analysis pipeline:

1. **WebSocket Integration**: Connect your sentiment processor to the WebSocket stream
2. **File Processing**: Process the JSONL output file with your batch processors
3. **Real-time Dashboard**: Use WebSocket output for live dashboard updates

## Example Integration

```python
import asyncio
import websockets
import json

async def process_tweets():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'tweet':
                tweet = data['data']
                # Process tweet with your sentiment analysis
                print(f"Processing: {tweet['text']}")
                print(f"Sentiment: {tweet['sentiment_score']}")

asyncio.run(process_tweets())
```

## Customization

### Adding New Tweet Sources

1. Create a new CSV file with your tweet data
2. Ensure the CSV follows the required format
3. Run the simulator with your CSV file

### Modifying Tweet Structure

Edit the `load_tweets()` method in `tweet_simulator.py` to customize the tweet JSON structure for your specific needs.

## Troubleshooting

### Common Issues

1. **CSV File Not Found**: Ensure the CSV file path is correct
2. **WebSocket Connection Failed**: Check if port 8765 is available
3. **Rate Too High**: Lower the rate if your system can't handle the load

### Performance Tips

- Use lower rates (0.1-1.0) for development
- Use higher rates (5-10) for stress testing
- WebSocket output is most efficient for real-time processing
- File output is best for batch processing

## Next Steps

This simulator is the first component of your social sentiment analysis pipeline. Next, you'll want to:

1. Build a sentiment analysis processor to consume the tweet stream
2. Create a real-time dashboard to visualize the sentiment data
3. Add more data sources (Reddit, Twitch chat, etc.)
4. Implement alerting for sentiment spikes

## License

This project is part of the Seneca Hack social sentiment analysis pipeline.

