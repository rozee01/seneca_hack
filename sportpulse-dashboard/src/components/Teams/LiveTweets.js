import React, { useState, useEffect, useRef } from "react";

// Accept onSentimentUpdate as a prop

const LiveTweets = ({ teamName, onSentimentUpdate }) => {
  const [tweets, setTweets] = useState([]);
  const [pendingTweets, setPendingTweets] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const wsRef = useRef(null);

  // Accept onSentimentUpdate as a prop
  // Use props directly
  // If you want to use destructuring, update the function signature:
  // const LiveTweets = ({ teamName, onSentimentUpdate }) => {

  // Remove connect function, useEffect handles connection

  const disconnect = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setConnectionStatus('Disconnected');
    }
  };

  const sendPing = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const ping = { type: 'ping', timestamp: Date.now() };
      wsRef.current.send(JSON.stringify(ping));
    }
  };

  const clearTweets = () => {
    setTweets([]);
  };

  // Auto-connect when component mounts
  useEffect(() => {
    if (!teamName) return;
    // Clean up previous connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnectionStatus('Connecting...');
    const apiUrl = "ws://localhost:8000/api/v1/ws/kafka/";
    const wsUrl = `${apiUrl}${teamName}`;
    const websocket = new WebSocket(wsUrl);
    wsRef.current = websocket;
    websocket.onopen = function(event) {
      setConnectionStatus('Connected');
    };
    websocket.onmessage = function(event) {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'pong') return;
        if (data.message && data.message.text) {
          const newTweet = {
            id: data.message.tweet_id || Date.now(),
            text: data.message.text,
            user: data.message.screenname || data.message.user || data.message.username || 'Anonymous',
            location: data.message.location || '',
            topic: data.topic || data.message.topic || '',
            sentiment_label: data.message.sentiment_label || '',
            sentiment_score: data.message.sentiment_score || 0,
            timestamp: new Date(data.timestamp || Date.now()).toISOString(),
            isLive: true
          };
          // Check for duplicate in pendingTweets and tweets
          const isDuplicate = pendingTweets.some(t => t.text === newTweet.text && t.user === newTweet.user)
            || tweets.some(t => t.text === newTweet.text && t.user === newTweet.user);
          if (!isDuplicate) {
            setPendingTweets(prev => [...prev, newTweet]);
            if (onSentimentUpdate && newTweet.sentiment_label) {
              onSentimentUpdate({
                sentiment_label: newTweet.sentiment_label,
                sentiment_score: newTweet.sentiment_score
              });
            }
          }
        }
      } catch (e) {
        console.error('Error parsing message:', e);
      }
    };
    websocket.onclose = function(event) {
      setConnectionStatus('Disconnected');
    };
    websocket.onerror = function(error) {
      setConnectionStatus('Error');
    };
    // Cleanup on unmount or teamName change
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [teamName]);

  // Slowly add tweets one at a time
  useEffect(() => {
    const MAX_TWEETS = 20;
    if (pendingTweets.length > 0) {
      const timer = setTimeout(() => {
        setTweets(prev => {
          const updated = [pendingTweets[0], ...prev];
          return updated.slice(0, MAX_TWEETS); // Only keep the newest MAX_TWEETS
        });
        setPendingTweets(prev => prev.slice(1));
      }, 1200); // 1.2 seconds between tweets
      return () => clearTimeout(timer);
    }
  }, [pendingTweets]);

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
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${getStatusColor()}`}>{connectionStatus}</span>
          <span className="text-xs text-gray-500">({tweets.length} tweets)</span>
        </div>
      </div>

      {/* Tweets Display */}
      {tweets.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-bold mb-2 text-blue-300">Top Tweets:</h3>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {tweets.map((tweet) => (
              <div
                key={tweet.id}
                className="p-4 bg-gradient-to-r from-blue-900 via-blue-800 to-blue-700 rounded-xl shadow-lg border-l-8 border-blue-500"
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="font-bold text-base text-white">{tweet.user}</span>
                  <span className="text-gray-400 text-xs">{formatTime(tweet.timestamp)}</span>
                  <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full shadow">LIVE</span>
                  {tweet.sentiment_label && (
                    <span className="text-xs font-semibold text-yellow-300">
                      {tweet.sentiment_label} ({tweet.sentiment_score.toFixed(2)})
                    </span>
                  )}
                  <span className="text-xs text-blue-200">{tweet.topic}</span>
                </div>
                <p className="text-gray-100 text-base mb-2">{tweet.text}</p>
                {tweet.location && (
                  <div className="text-xs text-gray-300">Location: {tweet.location}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveTweets;