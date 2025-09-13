import React from "react";
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

const SentimentChart = ({
  positive = 0,
  neutral = 0,
  negative = 0,
  trend = 0,
}) => {
  // S'assurer que les valeurs sont des nombres
  const positiveValue = Number(positive);
  const neutralValue = Number(neutral);
  const negativeValue = Number(negative);

  const data = {
    labels: ["Positive", "Neutral", "Negative"],
    datasets: [
      {
        data: [positiveValue, neutralValue, negativeValue],
        backgroundColor: [
          "#10B981", // Vert
          "#6366F1", // Bleu
          "#EF4444", // Rouge
        ],
        borderColor: "#1e293b",
        borderWidth: 3,
        hoverBackgroundColor: ["#059669", "#4F46E5", "#DC2626"],
        hoverOffset: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "65%",
    plugins: {
      legend: {
        display: false, // Cache la légende par défaut
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || "";
            const value = context.parsed;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value}% (${percentage}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="bg-[#1e293b] rounded-lg p-6">
      <p className="text-gray-300 mb-2">Sentiment Distribution</p>
      <div className="flex items-baseline gap-2 mb-2">
        <p className="text-4xl font-bold">{positiveValue}%</p>
      </div>
      <p className="text-gray-400 text-sm mb-6">Positive sentiment</p>

      <div className="relative h-64 mx-auto">
        <Doughnut data={data} options={options} />

        {/* Texte au centre */}
        <div className="absolute inset-0 flex items-center justify-center flex-col pointer-events-none">
          <span className="text-2xl font-bold text-white">
            {positiveValue}%
          </span>
          <span className="text-sm text-green-400">Positive</span>
        </div>
      </div>

      {/* Légende personnalisée */}
      <div className="flex justify-center gap-6 mt-6">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
          <span className="text-white text-sm">Positive</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
          <span className="text-white text-sm">Neutral</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
          <span className="text-white text-sm">Negative</span>
        </div>
      </div>
    </div>
  );
};

export default SentimentChart;
