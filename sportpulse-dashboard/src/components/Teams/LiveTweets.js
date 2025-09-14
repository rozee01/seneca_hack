import React, { useState, useEffect } from "react";

const LiveTweets = ({ teamName }) => {
  const [tweets, setTweets] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [ws, setWs] = useState(null);

  const connect = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      return;
    }

    if (!teamName) {
      return;
    }

    const apiUrl = "ws://localhost:8001/api/v1/ws/kafka/";
    const wsUrl = `${apiUrl}${teamName}`;
    
    setConnectionStatus('Connecting...');
    
    const websocket = new WebSocket(wsUrl);
    
    websocket.onopen = function(event) {
      setConnectionStatus('Connected');
      setWs(websocket);
    };
    
    websocket.onmessage = function(event) {
      try {
        const data = JSON.parse(event.data);
        
        // Handle pong responses
        if (data.type === 'pong') {
          return;
        }
        
        // Extract tweet data if it exists
        if (data.message && data.message.text) {
          const newTweet = {
            id: data.message.tweet_id || Date.now(),
            text: data.message.text,
            user: data.message.user || data.message.username || 'Anonymous',
            timestamp: new Date().toISOString(),
            sentiment: data.message.sentiment || 0,
            likes: Math.floor(Math.random() * 100),
            dislikes: Math.floor(Math.random() * 10),
            isLive: true
          };
          
          setTweets(prevTweets => [newTweet, ...prevTweets.slice(0, 19)]); // Keep latest 20 tweets
        }
      } catch (e) {
        console.error('Error parsing message:', e);
      }
    };
    
    websocket.onclose = function(event) {
      setConnectionStatus('Disconnected');
      setWs(null);
    };
    
    websocket.onerror = function(error) {
      setConnectionStatus('Error');
    };
  };

  const disconnect = () => {
    if (ws) {
      ws.close();
      setWs(null);
      setConnectionStatus('Disconnected');
    }
  };

  const sendPing = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      const ping = { type: 'ping', timestamp: Date.now() };
      ws.send(JSON.stringify(ping));
    }
  };

  const clearTweets = () => {
    setTweets([]);
  };

  // Auto-connect when component mounts
  useEffect(() => {
    if (teamName) {
      connect();
    }
    
    // Cleanup on unmount
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [teamName]);

  const getStatusColor = () => {
    if (connectionStatus === 'Connected') return 'text-green-400';
    if (connectionStatus === 'Connecting...') return 'text-yellow-400';
    if (connectionStatus === 'Error') return 'text-red-400';
    return 'text-gray-400';
  };

  const formatTime = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = now - time;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    return time.toLocaleDateString();
  };

  const getSentimentEmoji = (sentiment) => {
    if (sentiment > 0.2) return '😊';
    if (sentiment < -0.2) return '😞';
    return '😐';
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Live Tweets - {teamName}</h2>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            {connectionStatus}
          </span>
          <span className="text-xs text-gray-500">
            ({tweets.length} tweets)
          </span>
        </div>
      </div>

      {/* Control buttons */}
      <div className="flex gap-2 mb-4">
        <button 
          onClick={connect}
          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded"
        >
          Connect
        </button>
        <button 
          onClick={disconnect}
          className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded"
        >
          Disconnect
        </button>
        <button 
          onClick={sendPing}
          className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded"
        >
          Ping
        </button>
        <button 
          onClick={clearTweets}
          className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-sm rounded"
        >
          Clear
        </button>
      </div>

      {/* Tweets Display */}
      {tweets.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-bold mb-2">Live Tweets:</h3>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {tweets.map((tweet) => (
              <div
                key={tweet.id}
                className="p-3 bg-[#1e293b] rounded-lg border-l-4 border-blue-500"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-sm">{tweet.user}</span>
                  <span className="text-gray-500 text-xs">{formatTime(tweet.timestamp)}</span>
                  <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                    LIVE
                  </span>
                  <span className="text-xs">
                    {getSentimentEmoji(tweet.sentiment)}
                  </span>
                </div>
                <p className="text-gray-300 text-sm">{tweet.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {tweets.length > 0 && (
        <div className="mt-4 text-center">
          <button 
            onClick={clearTweets}
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            Clear tweets
          </button>
        </div>
      )}
    </div>
  );
};

export default LiveTweets;