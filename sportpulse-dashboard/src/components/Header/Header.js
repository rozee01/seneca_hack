import React from "react";
import { MdSportsBaseball } from "react-icons/md";
const Header = () => {
  return (
    <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#283039] px-10 py-3 bg-gradient-to-r from-[#181C20] via-[#23272f] to-[#181C20] shadow-lg py-6">
      <div className="flex items-center gap-10">
        <div className="flex items-center gap-3 text-white">
          <MdSportsBaseball size={30} />
          <h2 className="text-white text-3xl font-extrabold leading-tight tracking-tighter drop-shadow">
            Sportpulse
          </h2>
        </div>
      </div>
    </header>
  );
};

export default Header;
