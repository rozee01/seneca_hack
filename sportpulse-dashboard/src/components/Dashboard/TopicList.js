import React from "react";

const TopicList = ({ topics }) => (
  <ul className="flex flex-wrap gap-4">
    {topics.map((topic, idx) => (
      <li
        key={idx}
        className="bg-[#23272f] text-white px-4 py-2 rounded-lg shadow transition-all duration-200 cursor-pointer
                   hover:bg-[var(--primary-color)] hover:scale-105"
      >
        {topic}
      </li>
    ))}
  </ul>
);

export default TopicList;
