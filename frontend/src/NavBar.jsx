import React from "react";

export default function NavBar({ currentView, setCurrentView }) {
  const HomeText = ({ currentView }) => {
    console.log(currentView);
    return (
      <>
        {currentView == "home" ? (
          <p
            onClick={() => setCurrentView("home")}
            style={{ margin: "5px", color: "blue" }}
          >
            <u>Home</u>
          </p>
        ) : (
          <p
            onClick={() => setCurrentView("home")}
            style={{ margin: "5px", color: "black" }}
          >
            <u>Home</u>
          </p>
        )}
      </>
    );
  };

  const DashboardText = ({ currentView }) => {
    console.log(currentView);
    return (
      <>
        {currentView == "dashboard" ? (
          <p
            onClick={() => setCurrentView("dashboard")}
            style={{ margin: "5px", color: "blue" }}
          >
            <u>Dashboard</u>
          </p>
        ) : (
          <p
            onClick={() => setCurrentView("dashboard")}
            style={{ margin: "5px", color: "black" }}
          >
            <u>Dashboard</u>
          </p>
        )}
      </>
    );
  };
  //  :
  // })</>)

  return (
    <div style={{ display: "flex", padding: "12" }}>
      <HomeText currentView={currentView} />
      <DashboardText currentView={currentView} />
    </div>
  );
}
