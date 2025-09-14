import React, { useState, useEffect } from "react";
import StatsOverview from "./StatsOverview";
import SentimentChart from "./SentimentChart";
import TopPosts from "./TopPosts";
import { useParams, useLocation } from "react-router-dom";
import { apiEndpoints } from "../../config/api";

const TeamPage = () => {
  const { teamName } = useParams();
  const location = useLocation();
  const [teamStats, setTeamStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Determine sport from current path or default to NBA
  const currentSport = location.pathname.includes("/football") ? "football" : "nba";
  
  const sentimentData = {
    positive: 75,
    neutral: 15,
    negative: 10,
    trend: 8,
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
          Overview for {teamStats?.team_name || teamName}
          {loading && <span className="ml-2 text-sm text-gray-400">Loading...</span>}
        </h2>
        {error && (
          <div className="mt-2 p-3 bg-red-900 border border-red-700 rounded">
            <p className="text-red-200 text-sm">⚠️ {error}</p>
          </div>
        )}
      </div>
      
      {teamStats && (
        <div className="mb-6 p-4 bg-[#1e293b] rounded-lg">
          <h3 className="text-lg font-semibold mb-3">Team Statistics</h3>
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
              <span className="text-gray-400">Points:</span>
              <span className="ml-2 font-semibold text-blue-400">{teamStats.points}</span>
            </div>
          </div>
        </div>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <StatsOverview teamStats={teamStats} />
        <SentimentChart {...sentimentData} />
      </div>

      <TopPosts />
    </div>
  );
};

export default TeamPage;
