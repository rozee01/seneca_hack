import React from "react";
import { IoFootball } from "react-icons/io5";
import { GiBasketballBasket } from "react-icons/gi";
import { useNavigate, useLocation } from "react-router-dom";

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="flex flex-col w-64 bg-[#181C20] border-r border-gray-800">
      <div className="flex flex-col justify-between p-4 h-full">
        <div className="flex flex-col gap-6">
          <div className="flex flex-col gap-2">
            <div
              className={`flex items-center gap-3 px-4 py-2 rounded cursor-pointer ${
                location.pathname === "/football"
                  ? "bg-gray-700"
                  : "hover:bg-gray-700"
              }`}
              onClick={() => navigate("/football")}
            >
              <IoFootball size={24} className="text-white" />
              <span className="text-white font-semibold">Football</span>
            </div>
            <div
              className={`flex items-center gap-3 px-4 py-2 rounded cursor-pointer ${
                location.pathname === "/nba"
                  ? "bg-gray-700"
                  : "hover:bg-gray-700"
              }`}
              onClick={() => navigate("/nba")}
            >
              <GiBasketballBasket size={24} className="text-white" />
              <span className="text-white font-semibold">NBA</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
