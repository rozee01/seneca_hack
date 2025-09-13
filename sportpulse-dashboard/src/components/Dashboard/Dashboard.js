import React from "react";
import TopicList from "./TopicList";
import DataTable from "./DataTable";
import { useNavigate } from "react-router-dom";

const medals = ["🥇", "🥈", "🥉"];

const Dashboard = () => {
  const navigate = useNavigate();
  const topics = [
    "Match Highlights",
    "Player Performances",
    "Team Strategies",
    "Fan Reactions",
    "Upcoming Games",
  ];

  const topTeams = [
    { name: "Team A", points: 78 },
    { name: "Team C", points: 74 },
    { name: "Team B", points: 70 },
  ];

  const tableData = [
    { team: "Team A", mentions: "12,345", sentiment: "Positive" },
    { team: "Team B", mentions: "10,234", sentiment: "Neutral" },
    { team: "Team C", mentions: "8,765", sentiment: "Positive" },
    { team: "Team D", mentions: "6,543", sentiment: "Negative" },
    { team: "Team E", mentions: "5,432", sentiment: "Positive" },
  ];

  return (
    <div className="px-8 py-6">
      <div className="mt-4">
        <h2 className="text-white text-xl font-bold tracking-tight mb-4">
          Top Ranking Teams
        </h2>
        <div className="flex flex-col md:flex-row gap-6">
          {topTeams.map((team, idx) => (
            <div
              key={team.name}
              className={`flex items-center gap-4 bg-gradient-to-br from-[#23272f] to-[#181C20] rounded-xl shadow-lg p-5 w-full md:w-1/3 border-2 ${
                idx === 0
                  ? "border-yellow-400"
                  : idx === 1
                  ? "border-gray-400"
                  : "border-orange-400"
              } transition-transform duration-200 hover:scale-105`}
              onClick={() => navigate(`/team/${encodeURIComponent(team.name)}`)}
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
        </h2>
        <DataTable data={tableData} />
      </div>
    </div>
  );
};

export default Dashboard;
