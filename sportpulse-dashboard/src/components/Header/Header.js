import React from "react";
import logo from "../../assets/logo.png";

const Header = () => {
  return (
    <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#283039] px-10 py-3 bg-gradient-to-r from-[#181C20] via-[#23272f] to-[#181C20] shadow-lg py-6">
      <div className="flex items-center gap-10">
        <div className="flex items-center gap-3 text-white">
          <img
            src={logo}
            alt="Sportpulse Logo"
            className="h-20 w-50 object-contain"
          />
        </div>
      </div>
    </header>
  );
};

export default Header;
