import React from "react";
import StatsOverview from "./StatsOverview";
import SentimentChart from "./SentimentChart";
import TopPosts from "./TopPosts";
import { useParams } from "react-router-dom";


const TeamPage = () => {
  const { teamName } = useParams();
  const sentimentData = {
    positive: 75,
    neutral: 15,
    negative: 10,
    trend: 8,
  };
  return (
    <div
      className="min-h-screen bg-[#111418] text-white p-8"
      style={{ fontFamily: '"Space Grotesk", "Noto Sans", sans-serif' }}
    >
      <h2 className="text-2xl font-bold mb-8">Overview for {teamName}</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <StatsOverview />

        <SentimentChart {...sentimentData} />
      </div>

      <TopPosts />
    </div>
  );
};

export default TeamPage;
