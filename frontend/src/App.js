import { useState } from "react";
import DashBoard from "./DashBoard";
import Home from "./Home";
import "./index.css";
import NavBar from "./NavBar";

export default function App() {

  const [currentView, setCurrentView] = useState("home");
  const AppStyle = {'padding' : '12px'}

  const MainContent = () => {
    if (currentView == "home") {
      return <Home />
    }
    return <DashBoard />
  }

  return (
    <div style={AppStyle}>
      <NavBar currentView={currentView} setCurrentView={setCurrentView} />
      <MainContent />
    </div>
  );
}

