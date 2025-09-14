import React, { useState, useEffect } from "react";
import StatsOverview from "./StatsOverview";
import SentimentChart from "./SentimentChart";
import LiveTweets from "./LiveTweets";
import { useParams, useLocation } from "react-router-dom";
import { apiEndpoints } from "../../config/api";

const TeamPage = () => {
  const { teamName } = useParams();
  const location = useLocation();
  const [teamStats, setTeamStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [liveSentimentData, setLiveSentimentData] = useState(null);
  
  // Determine sport from current path or default to NBA
  const currentSport = location.pathname.includes("/football") ? "football" : "nba";
  
  // Map URL team names to standardized Kafka topic names
  const getStandardizedTeamName = (urlTeamName) => {
    const baseTeams = [
      'Birmingham', 'Liverpool', 'Leicester', 'Sheffield', 'Galatasaray',
      'Internazionale', 'PSV', 'Burnley', 'Norwich', 'Manchester',
      'Chelsea', 'Arsenal', 'Tottenham', 'Everton', 'Bournemouth', 'Southampton'
    ];
    
    // Create mapping from various formats to standard names
    const teamMapping = {
      // Birmingham variations
      'birmingham city': 'Birmingham',
      'birmingham city fc': 'Birmingham',
      'birmingham fc': 'Birmingham',
      
      // Liverpool variations
      'liverpool fc': 'Liverpool',
      'liverpool': 'Liverpool',
      
      // Leicester variations
      'leicester city': 'Leicester',
      'leicester city fc': 'Leicester',
      'leicester fc': 'Leicester',
      'leicester': 'Leicester',
      
      // Sheffield variations
      'sheffield united': 'Sheffield',
      'sheffield united fc': 'Sheffield',
      'sheffield fc': 'Sheffield',
      'sheffield': 'Sheffield',
      
      // Galatasaray variations
      'galatasaray': 'Galatasaray',
      'galatasaray sk': 'Galatasaray',
      
      // Internazionale variations
      'fc internazionale milano': 'Internazionale',
      'internazionale': 'Internazionale',
      'inter': 'Internazionale',
      'inter milan': 'Internazionale',
      
      // PSV variations
      'psv': 'PSV',
      'psv eindhoven': 'PSV',
      
      // Burnley variations
      'burnley fc': 'Burnley',
      'burnley': 'Burnley',
      
      // Norwich variations
      'norwich city': 'Norwich',
      'norwich city fc': 'Norwich',
      'norwich fc': 'Norwich',
      'norwich': 'Norwich',
      
      // Manchester variations (both City and United)
      'manchester city': 'Manchester',
      'manchester city fc': 'Manchester',
      'manchester fc': 'Manchester',
      'manchester united': 'Manchester',
      'manchester united fc': 'Manchester',
      'manchester': 'Manchester',
      
      // Chelsea variations
      'chelsea fc': 'Chelsea',
      'chelsea': 'Chelsea',
      
      // Arsenal variations
      'arsenal fc': 'Arsenal',
      'arsenal': 'Arsenal',
      
      // Tottenham variations
      'tottenham': 'Tottenham',
      'tottenham hotspur': 'Tottenham',
      'tottenham fc': 'Tottenham',
      'spurs': 'Tottenham',
      
      // Everton variations
      'everton fc': 'Everton',
      'everton': 'Everton',
      
      // Bournemouth variations
      'afc bournemouth': 'Bournemouth',
      'bournemouth fc': 'Bournemouth',
      'bournemouth': 'Bournemouth',
      
      // Southampton variations
      'southampton fc': 'Southampton',
      'southampton': 'Southampton',
    };
    
    // Normalize the input (lowercase, replace spaces/hyphens)
    const normalized = urlTeamName?.toLowerCase().replace(/[-_]/g, '-');
    
    // Try exact match first
    if (teamMapping[normalized]) {
      return teamMapping[normalized];
    }
    
    // Try without hyphens/spaces
    const withoutSeparators = normalized?.replace(/[-\s]/g, '');
    if (teamMapping[withoutSeparators]) {
      return teamMapping[withoutSeparators];
    }
    
    // Check if it's already a base team name
    const directMatch = baseTeams.find(team => 
      team.toLowerCase() === normalized || 
      team.toLowerCase().replace(/[-_]/g, '') === withoutSeparators
    );
    
    if (directMatch) {
      return directMatch;
    }
    
    // Default fallback - return original if no mapping found
    return urlTeamName;
  };
  
  const standardizedTeamName = getStandardizedTeamName(teamName);
  
  // Default sentiment data (will be updated by live data)
  const sentimentData = liveSentimentData || {
    positive: 75,
    neutral: 15,
    negative: 10,
    trend: 8,
  };

  // Handler for receiving live sentiment updates
  const handleSentimentUpdate = (newSentimentStats) => {
    // Accepts either aggregate or single tweet update
    if (newSentimentStats.sentiment_label) {
      setLiveSentimentData(prev => {
        const base = prev || { positive: 0, neutral: 0, negative: 0, trend: 0 };
        let updated = { ...base };
        if (newSentimentStats.sentiment_label === 'positive') updated.positive = (updated.positive || 0) + 1;
        if (newSentimentStats.sentiment_label === 'neutral') updated.neutral = (updated.neutral || 0) + 1;
        if (newSentimentStats.sentiment_label === 'negative') updated.negative = (updated.negative || 0) + 1;
        updated.trend = 0;
        return updated;
      });
    } else {
      setLiveSentimentData({
        positive: newSentimentStats.positive,
        neutral: newSentimentStats.neutral,
        negative: newSentimentStats.negative,
        trend: 0,
      });
    }
  };

  const fetchTeamStats = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(apiEndpoints[currentSport].teamStats(teamName), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch team stats`);
      }
      const data = await response.json();
      setTeamStats(data.stats);
    } catch (err) {
      console.error('Error fetching team stats:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (teamName) {
      fetchTeamStats();
    }
  }, [teamName, currentSport]);
  return (
    <div
      className="min-h-screen bg-[#111418] text-white p-8"
      style={{ fontFamily: '"Space Grotesk", "Noto Sans", sans-serif' }}
    >
      <div className="mb-4">
        <h2 className="text-2xl font-bold">
          Investment Analysis: {teamStats?.team_name || teamName}
          {loading && <span className="ml-2 text-sm text-gray-400">Loading...</span>}
        </h2>
        <p className="text-gray-400 text-sm mt-1">
          Comprehensive team metrics for sponsorship and investment decisions
        </p>
        {error && (
          <div className="mt-2 p-3 bg-red-900 border border-red-700 rounded">
            <p className="text-red-200 text-sm">⚠️ {error}</p>
          </div>
        )}
      </div>
      
      {teamStats && (
        <>
          {/* Sponsorship Value Score - Highlight */}
          <div className="mb-6 p-6 bg-gradient-to-r from-[#1e293b] to-[#334155] rounded-lg border-l-4 border-blue-500">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-blue-400">Sponsorship Value Score</h3>
              <div className="flex items-center gap-2">
                <span className={`text-3xl font-bold ${
                  teamStats.sponsorship_value_score >= 80 ? 'text-green-400' :
                  teamStats.sponsorship_value_score >= 60 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {teamStats.sponsorship_value_score}/100
                </span>
                <span className={`text-sm px-3 py-1 rounded-full font-medium ${
                  teamStats.sponsorship_value_score >= 80 ? 'bg-green-900 text-green-200' :
                  teamStats.sponsorship_value_score >= 60 ? 'bg-yellow-900 text-yellow-200' :
                  'bg-red-900 text-red-200'
                }`}>
                  {teamStats.sponsorship_value_score >= 80 ? 'Excellent Investment' :
                   teamStats.sponsorship_value_score >= 60 ? 'Good Opportunity' :
                   'High Risk'}
                </span>
              </div>
            </div>
            <p className="text-gray-300 text-sm">
              Combined score based on performance metrics, fan engagement, and sentiment analysis
            </p>
          </div>

          {/* Performance Metrics */}
          <div className="mb-6 p-4 bg-[#1e293b] rounded-lg">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              📊 Performance Metrics
              <span className={`text-sm px-2 py-1 rounded-full ${
                teamStats.growth_trend === 'up' ? 'bg-green-900 text-green-200' :
                teamStats.growth_trend === 'down' ? 'bg-red-900 text-red-200' :
                'bg-yellow-900 text-yellow-200'
              }`}>
                {teamStats.growth_trend === 'up' ? '📈 Growing' :
                 teamStats.growth_trend === 'down' ? '📉 Declining' :
                 '📊 Stable'}
              </span>
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Games Played:</span>
                <span className="ml-2 font-semibold">{teamStats.games_played}</span>
              </div>
              <div>
                <span className="text-gray-400">Wins:</span>
                <span className="ml-2 font-semibold text-green-400">{teamStats.wins}</span>
              </div>
              <div>
                <span className="text-gray-400">Losses:</span>
                <span className="ml-2 font-semibold text-red-400">{teamStats.losses}</span>
              </div>
              <div>
                <span className="text-gray-400">Win Rate:</span>
                <span className="ml-2 font-semibold text-blue-400">
                  {((teamStats.win_percentage || 0) * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Investment Metrics */}
          <div className="mb-6 p-4 bg-[#1e293b] rounded-lg">
            <h3 className="text-lg font-semibold mb-3">🎯 Investment Insights</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-[#0f172a] p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">Fan Engagement</span>
                  <span className="text-blue-400 text-lg font-bold">
                    {teamStats.fan_engagement?.toLocaleString() || 'N/A'}
                  </span>
                </div>
                <p className="text-gray-500 text-xs">Active mentions & interactions</p>
              </div>
              
              <div className="bg-[#0f172a] p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">Sentiment Score</span>
                  <span className={`text-lg font-bold ${
                    teamStats.sentiment_score >= 80 ? 'text-green-400' :
                    teamStats.sentiment_score >= 60 ? 'text-yellow-400' :
                    'text-red-400'
                  }`}>
                    {teamStats.sentiment_score}%
                  </span>
                </div>
                <p className="text-gray-500 text-xs">Overall fan sentiment</p>
              </div>
              
              <div className="bg-[#0f172a] p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">Market Reach</span>
                  <span className="text-purple-400 text-lg font-bold">
                    {teamStats.market_reach?.toLocaleString() || 'N/A'}
                  </span>
                </div>
                <p className="text-gray-500 text-xs">Estimated total audience</p>
              </div>
            </div>
          </div>
        </>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <StatsOverview teamStats={teamStats} />
        <div>
          <SentimentChart teamName={standardizedTeamName} {...sentimentData} />
          {liveSentimentData && (
            <div className="mt-2 text-center">
              <span className="bg-green-900/20 text-green-400 text-xs px-2 py-1 rounded-full">
                📡 Live Data ({liveSentimentData.positive + liveSentimentData.neutral + liveSentimentData.negative} tweets)
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1  gap-6">
        <LiveTweets teamName={standardizedTeamName} onSentimentUpdate={handleSentimentUpdate} />
      </div>
    </div>
  );
};

export default TeamPage;
