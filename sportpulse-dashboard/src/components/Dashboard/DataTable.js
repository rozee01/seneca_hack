import React from "react";
import { useNavigate, useLocation } from "react-router-dom";

const DataTable = ({ data }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Determine current sport from path
  const currentSport = location.pathname === "/football" ? "football" : 
                     location.pathname === "/nba" ? "nba" : "";

  const handleTeamClick = (teamName) => {
    const basePath = currentSport ? `/${currentSport}` : "";
    navigate(`${basePath}/team/${encodeURIComponent(teamName)}`);
  };

  return (
    <table className="min-w-full bg-[#181C20] rounded-lg overflow-hidden">
      <thead>
        <tr>
          <th className="px-4 py-2 text-left text-gray-400">Team</th>
          <th className="px-4 py-2 text-left text-gray-400">Mentions</th>
          <th className="px-4 py-2 text-left text-gray-400">Weekly Change</th>
          <th className="px-4 py-2 text-left text-gray-400">Engagement</th>
          <th className="px-4 py-2 text-left text-gray-400">Sentiment</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row, index) => (
          <tr
            key={`${row.team}-${index}`}
            className="hover:bg-[var(--primary-color)] cursor-pointer transition"
            onClick={() => handleTeamClick(row.team)}
          >
            <td className="px-4 py-2 text-white font-semibold">{row.team}</td>
            <td className="px-4 py-2 text-white">{row.mentions}</td>
            <td className="px-4 py-2">
              <span className={`text-sm font-medium ${
                row.weekly_change?.startsWith('+') ? 'text-green-400' :
                row.weekly_change?.startsWith('-') ? 'text-red-400' :
                'text-gray-400'
              }`}>
                {row.weekly_change || 'N/A'}
              </span>
            </td>
            <td className="px-4 py-2">
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                row.engagement_level === 'High' ? 'bg-green-900 text-green-200' :
                row.engagement_level === 'Medium' ? 'bg-yellow-900 text-yellow-200' :
                'bg-gray-900 text-gray-200'
              }`}>
                {row.engagement_level || 'N/A'}
              </span>
            </td>
            <td className="px-4 py-2">
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                row.sentiment === 'Positive' ? 'bg-green-900 text-green-200' :
                row.sentiment === 'Negative' ? 'bg-red-900 text-red-200' :
                'bg-gray-900 text-gray-200'
              }`}>
                {row.sentiment}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default DataTable;
