import React from "react";
import { BrowserRouter as Router, Routes, Route} from "react-router-dom";
import Sidebar from "./components/Sidebar/Sidebar";
import Header from "./components/Header/Header";
import Dashboard from "./components/Dashboard/Dashboard";
import TeamPage from "./components/Teams/Team";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="relative flex h-auto min-h-screen w-full flex-col bg-[#111418] dark group/design-root overflow-x-hidden"
        style={{ fontFamily: '"Space Grotesk", "Noto Sans", sans-serif' }}>
        <Header />
        <div className="flex h-full grow">
          <Sidebar />
          <div className="flex-1">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/football" element={<Dashboard />} />
              <Route path="/nba" element={<Dashboard />} />
              <Route path="/team/:teamName" element={<TeamPage />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;