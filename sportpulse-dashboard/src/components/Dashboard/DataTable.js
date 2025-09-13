import React from "react";
import { useNavigate } from "react-router-dom";

const DataTable = ({ data }) => {
  const navigate = useNavigate();
  return (
    <table className="min-w-full bg-[#181C20] rounded-lg overflow-hidden">
      <thead>
        <tr>
          <th className="px-4 py-2 text-left text-gray-400">Team</th>
          <th className="px-4 py-2 text-left text-gray-400">Mentions</th>
          <th className="px-4 py-2 text-left text-gray-400">Sentiment</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr
            key={row.team}
            className="hover:bg-[var(--primary-color)] cursor-pointer transition"
            onClick={() => navigate(`/team/${encodeURIComponent(row.team)}`)}
          >
            <td className="px-4 py-2 text-white font-semibold">{row.team}</td>
            <td className="px-4 py-2 text-white">{row.mentions}</td>
            <td className="px-4 py-2 text-white">{row.sentiment}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default DataTable;
