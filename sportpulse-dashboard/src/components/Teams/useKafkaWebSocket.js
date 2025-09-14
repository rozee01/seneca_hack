import { useState, useEffect, useRef } from 'react';

const useKafkaWebSocket = (teamName) => {
  const [tweets, setTweets] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [error, setError] = useState(null);
  const [sentimentStats, setSentimentStats] = useState({
    positive: 0,
    neutral: 0,
    negative: 0,
    total: 0
  });
  
  const wsRef = useRef(null);

  // Calculate sentiment stats from tweets
  const updateSentimentStats = (tweetsList) => {
    if (tweetsList.length === 0) {
      setSentimentStats({ positive: 0, neutral: 0, negative: 0, total: 0 });
      return;
    }

    const total = tweetsList.length;
    const positive = tweetsList.filter(tweet => tweet.sentiment > 0.2).length;
    const negative = tweetsList.filter(tweet => tweet.sentiment < -0.2).length;
    const neutral = total - positive - negative;

    setSentimentStats({
      positive: Math.round((positive / total) * 100),
      neutral: Math.round((neutral / total) * 100),
      negative: Math.round((negative / total) * 100),
      total
    });
  };

  useEffect(() => {
    if (!teamName) return;

    const connectWebSocket = () => {
      try {
        setConnectionStatus('connecting');
        const wsUrl = `ws://localhost:8000/api/v1/ws/kafka/${teamName}`;
        
        console.log(`Connecting to WebSocket: ${wsUrl}`);
        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
          console.log(`WebSocket connected for team: ${teamName}`);
          setConnectionStatus('connected');
          setError(null);
          
          // Send ping to test connection
          wsRef.current.send(JSON.stringify({ type: 'ping' }));
        };

        wsRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('Received WebSocket message:', data);
            
            // Handle pong responses
            if (data.type === 'pong') {
              console.log('Received pong from server');
              return;
            }

            // Handle Kafka messages
            if (data.message && data.message.text) {
              const newTweet = {
                id: data.message.tweet_id || `tweet_${Date.now()}`,
                text: data.message.text,
                user: data.message.user || data.message.username || 'Anonymous',
                timestamp: new Date().toISOString(),
                sentiment: parseFloat(data.message.sentiment) || 0,
                likes: Math.floor(Math.random() * 100),
                dislikes: Math.floor(Math.random() * 10),
                isLive: true,
                platform: data.message.platform || 'twitter'
              };

              setTweets(prevTweets => {
                const updatedTweets = [newTweet, ...prevTweets.slice(0, 49)]; // Keep latest 50 tweets
                updateSentimentStats(updatedTweets);
                return updatedTweets;
              });
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        wsRef.current.onclose = (event) => {
          console.log(`WebSocket closed for team: ${teamName}`, event.code, event.reason);
          setConnectionStatus('disconnected');
          
          // Attempt to reconnect after 3 seconds if it wasn't a manual close
          if (event.code !== 1000) {
            setTimeout(() => {
              if (teamName) {
                connectWebSocket();
              }
            }, 3000);
          }
        };

        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          setError('WebSocket connection error');
          setConnectionStatus('error');
        };

      } catch (error) {
        console.error('Failed to create WebSocket connection:', error);
        setError('Failed to connect to live feed');
        setConnectionStatus('error');
      }
    };

    connectWebSocket();

    // Cleanup on unmount or team change
    return () => {
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
        wsRef.current = null;
      }
    };
  }, [teamName]);

  const clearTweets = () => {
    setTweets([]);
    setSentimentStats({ positive: 0, neutral: 0, negative: 0, total: 0 });
  };

  return {
    tweets,
    connectionStatus,
    error,
    sentimentStats,
    clearTweets
  };
};

export default useKafkaWebSocket;