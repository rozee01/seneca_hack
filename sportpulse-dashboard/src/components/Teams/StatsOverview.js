import React from "react";

const StatsOverview = ({ teamStats }) => {
  // Don't render if no team stats
  if (!teamStats) {
    return (
      <div className="bg-[#1e293b] rounded-lg p-6">
        <p className="text-gray-300 mb-2">Team Performance Metrics</p>
        <div className="flex items-center justify-center h-40">
          <p className="text-gray-500">No team data available</p>
        </div>
      </div>
    );
  }

  // Calculate win percentage
  const winPercentage = teamStats.games_played > 0 
    ? Math.round((teamStats.wins / teamStats.games_played) * 100)
    : 0;

  return (
    <div className="bg-[#1e293b] rounded-lg p-6">
      <p className="text-gray-300 mb-2">Team Performance Metrics</p>
      <div className="flex items-baseline gap-2 mb-2">
        <p className="text-4xl font-bold">{winPercentage}%</p>
        <p className="text-green-500">Win Rate</p>
      </div>
      <p className="text-gray-400 text-sm mb-4">
        {teamStats.wins} wins out of {teamStats.games_played} games
      </p>

      <div className="h-40">
        <svg fill="none" height="100%" width="100%" viewBox="0 0 472 150">
          <path
            d="M0 109C18.1538 109 18.1538 21 36.3077 21C54.4615 21 54.4615 41 72.6154 41C90.7692 41 90.7692 93 108.923 93C127.077 93 127.077 33 145.231 33C163.385 33 163.385 101 181.538 101C199.692 101 199.692 61 217.846 61C236 61 236 45 254.154 45C272.308 45 272.308 121 290.462 121C308.615 121 308.615 149 326.769 149C344.923 149 344.923 1 363.077 1C381.231 1 381.231 81 399.385 81C417.538 81 417.538 129 435.692 129C453.846 129 453.846 25 472 25V149H326.769H0V109Z"
            fill="url(#gradient)"
          ></path>
          <path
            d="M0 109C18.1538 109 18.1538 21 36.3077 21C54.4615 21 54.4615 41 72.6154 41C90.7692 41 90.7692 93 108.923 93C127.077 93 127.077 33 145.231 33C163.385 33 163.385 101 181.538 101C199.692 101 199.692 61 217.846 61C236 61 236 45 254.154 45C272.308 45 272.308 121 290.462 121C308.615 121 308.615 149 326.769 149C344.923 149 344.923 1 363.077 1C381.231 1 381.231 81 399.385 81C417.538 81 417.538 129 435.692 129C453.846 129 453.846 25 472 25"
            stroke="#0b73da"
            strokeWidth="3"
          ></path>
          <defs>
            <linearGradient id="gradient" x1="236" x2="236" y1="1" y2="149">
              <stop stopColor="#0b73da" stopOpacity="0.5"></stop>
              <stop offset="1" stopColor="#0b73da" stopOpacity="0"></stop>
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div className="flex justify-around text-xs text-gray-400 mt-2">
        {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => (
          <span key={day}>{day}</span>
        ))}
      </div>
      
      {teamStats && (
        <div className="mt-4 pt-4 border-t border-gray-600">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-blue-400">{teamStats.points}</p>
              <p className="text-xs text-gray-400">Total Points</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-400">{teamStats.wins}</p>
              <p className="text-xs text-gray-400">Wins</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-red-400">{teamStats.losses || 0}</p>
              <p className="text-xs text-gray-400">Losses</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatsOverview;
