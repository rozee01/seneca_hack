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
    "Match Highlights",
    "Player Performances",
    "Team Strategies",
    "Fan Reactions",
    "Upcoming Games",
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
        <h2 className="text-white text-xl font-bold tracking-tight mb-4">
          Top Ranking {currentSport.toUpperCase()} Teams
          {loading && <span className="ml-2 text-sm text-gray-400">Loading...</span>}
        </h2>
        <div className="flex flex-col md:flex-row gap-6">
          {topTeams.slice(0, 3).map((team, idx) => (
            <div
              key={team.name}
              className={`flex items-center gap-4 bg-gradient-to-br from-[#23272f] to-[#181C20] rounded-xl shadow-lg p-5 w-full md:w-1/3 border-2 ${
                idx === 0
                  ? "border-yellow-400"
                  : idx === 1
                  ? "border-gray-400"
                  : "border-orange-400"
              } transition-transform duration-200 hover:scale-105 cursor-pointer`}
              onClick={() => handleTeamClick(team.name)}
            >
              <div className="text-3xl">{medals[idx]}</div>
              <div className="flex flex-col flex-1">
                <span className="text-white font-semibold text-lg">
                  {team.name}
                </span>
                <span className="text-gray-400 text-sm">
                  Points: {team.points}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="mt-8">
        <h2 className="text-white text-xl font-bold tracking-tight mb-4">
          Trending Topics
        </h2>
        <TopicList topics={topics} />
      </div>

      <div className="mt-8">
        <h2 className="text-white text-xl font-bold tracking-tight mb-4">
          Team Mentions
          {loading && <span className="ml-2 text-sm text-gray-400">Loading...</span>}
        </h2>
        <DataTable data={tableData} />
      </div>
    </div>
  );
};

export default Dashboard;
