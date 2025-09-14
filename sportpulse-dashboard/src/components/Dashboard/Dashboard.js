import React, { useState, useEffect } from "react";
import TopicList from "./TopicList";
import DataTable from "./DataTable";
import { useNavigate, useLocation } from "react-router-dom";
import { apiEndpoints, healthCheck } from "../../config/api";

const medals = ["🥇", "🥈", "🥉"];

const Dashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [topTeams, setTopTeams] = useState([]);
  const [tableData, setTableData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('unknown');
  
  const topics = [
    "📈 Market Performance Trends",
    "🎯 Sponsorship Opportunities", 
    "📊 Fan Engagement Analytics",
    "💰 Revenue Generation Potential",
    "🌟 Brand Association Benefits",
  ];

  // Determine sport from current path
  const currentSport = location.pathname === "/football" ? "football" : 
                     location.pathname === "/nba" ? "nba" : "nba"; // default to NBA

  const checkApiHealth = async () => {
    try {
      const response = await fetch(healthCheck);
      if (response.ok) {
        setApiStatus('healthy');
      } else {
        setApiStatus('unhealthy');
      }
    } catch (err) {
      setApiStatus('offline');
    }
  };

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    // Clear existing data when switching sports
    setTopTeams([]);
    setTableData([]);
    
    try {
      // Fetch top teams
      const topTeamsResponse = await fetch(apiEndpoints[currentSport].topTeams, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!topTeamsResponse.ok) {
        throw new Error(`HTTP ${topTeamsResponse.status}: Failed to fetch top teams`);
      }
      const topTeamsData = await topTeamsResponse.json();
      setTopTeams(topTeamsData.teams || []);

      // Fetch team mentions
      const mentionsResponse = await fetch(apiEndpoints[currentSport].teamMentions, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!mentionsResponse.ok) {
        throw new Error(`HTTP ${mentionsResponse.status}: Failed to fetch team mentions`);
      }
      const mentionsData = await mentionsResponse.json();
      setTableData(mentionsData.data || []);
      
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTeamClick = (teamName) => {
    const basePath = currentSport !== "nba" ? `/${currentSport}` : "";
    navigate(`${basePath}/team/${encodeURIComponent(teamName)}`);
  };

  useEffect(() => {
    checkApiHealth();
    fetchData();
  }, [currentSport]);

  return (
    <div className="px-8 py-6">
      {/* API Status Indicator */}
      <div className="mb-4 flex items-center gap-2">
        <span className="text-gray-400 text-sm">API Status:</span>
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          apiStatus === 'healthy' ? 'bg-green-900 text-green-200' :
          apiStatus === 'unhealthy' ? 'bg-yellow-900 text-yellow-200' :
          'bg-red-900 text-red-200'
        }`}>
          {apiStatus.toUpperCase()}
        </span>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-900 border border-red-700 rounded-lg">
          <p className="text-red-200">⚠️ API Error: {error}</p>
          <p className="text-red-300 text-sm">Please check API connection and try refreshing the page.</p>
        </div>
      )}
      
      <div className="mt-4">
        <h2 className="text-white text-xl font-bold tracking-tight mb-2">
          Top Investment Opportunities - {currentSport.toUpperCase()} Teams
          {loading && <span className="ml-2 text-sm text-gray-400">Loading...</span>}
        </h2>
        <p className="text-gray-400 text-sm mb-4">
          Teams ranked by sponsorship value, performance, and fan engagement metrics
        </p>
        <div className="flex flex-col md:flex-row gap-6">
          {topTeams.slice(0, 3).map((team, idx) => (
            <div
              key={team.name}
              className={`flex flex-col gap-3 bg-gradient-to-br from-[#23272f] to-[#181C20] rounded-xl shadow-lg p-5 w-full md:w-1/3 border-2 ${
                idx === 0
                  ? "border-yellow-400"
                  : idx === 1
                  ? "border-gray-400"
                  : "border-orange-400"
              } transition-transform duration-200 hover:scale-105 cursor-pointer relative overflow-hidden`}
              onClick={() => handleTeamClick(team.name)}
            >
              {/* Medal and Main Info */}
              <div className="flex items-center gap-4">
                <div className="text-3xl">{medals[idx]}</div>
                <div className="flex flex-col flex-1">
                  <span className="text-white font-semibold text-lg">
                    {team.name}
                  </span>
                  <span className="text-gray-400 text-sm">
                    {team.points} Points
                  </span>
                </div>
                {/* Growth Trend Indicator */}
                <div className={`text-lg ${
                  team.growth_trend === 'up' ? 'text-green-400' : 
                  team.growth_trend === 'down' ? 'text-red-400' : 
                  'text-yellow-400'
                }`}>
                  {team.growth_trend === 'up' ? '📈' : 
                   team.growth_trend === 'down' ? '📉' : '📊'}
                </div>
              </div>
              
              {/* Investor Metrics */}
              <div className="bg-black/20 rounded-lg p-3 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-xs">Sponsorship Value</span>
                  <div className="flex items-center gap-1">
                    <span className={`text-sm font-bold ${
                      team.sponsorship_value_score >= 80 ? 'text-green-400' :
                      team.sponsorship_value_score >= 60 ? 'text-yellow-400' :
                      'text-red-400'
                    }`}>
                      {team.sponsorship_value_score}/100
                    </span>
                    <span className="text-xs" title="Combined score based on performance, sentiment, and engagement">ℹ️</span>
                  </div>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-xs">Fan Engagement</span>
                  <span className="text-blue-400 text-sm font-semibold">
                    {team.fan_engagement?.toLocaleString() || 'N/A'}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-xs">Sentiment Score</span>
                  <span className={`text-sm font-semibold ${
                    team.sentiment_score >= 80 ? 'text-green-400' :
                    team.sentiment_score >= 60 ? 'text-yellow-400' :
                    'text-red-400'
                  }`}>
                    {team.sentiment_score}%
                  </span>
                </div>
              </div>
              
              {/* Investment Recommendation Badge */}
              {team.sponsorship_value_score >= 75 && (
                <div className="absolute top-2 right-2 bg-green-600 text-green-100 text-xs px-2 py-1 rounded-full font-medium">
                  🎯 Prime Investment
                </div>
              )}
              {team.sponsorship_value_score >= 60 && team.sponsorship_value_score < 75 && (
                <div className="absolute top-2 right-2 bg-yellow-600 text-yellow-100 text-xs px-2 py-1 rounded-full font-medium">
                  💡 Good Potential
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      
      <div className="mt-8">
        <h2 className="text-white text-xl font-bold tracking-tight mb-2">
          Investment Insights & Market Trends
        </h2>
        <p className="text-gray-400 text-sm mb-4">
          Key areas of analysis for sponsorship and investment decisions
        </p>
        <TopicList topics={topics} />
      </div>

      <div className="mt-8">
        <h2 className="text-white text-xl font-bold tracking-tight mb-2">
          Team Performance & Engagement Analytics
          {loading && <span className="ml-2 text-sm text-gray-400">Loading...</span>}
        </h2>
        <p className="text-gray-400 text-sm mb-4">
          Track team mentions, growth trends, and engagement levels for investment decisions
        </p>
        <DataTable data={tableData} />
      </div>
    </div>
  );
};

export default Dashboard;
