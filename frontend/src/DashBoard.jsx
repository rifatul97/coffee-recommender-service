import { useEffect, useState } from "react";
import React from "react";
import { tab } from "@testing-library/user-event/dist/tab";

export default function DashBoard() {
  const [selected, setSelected] = useState(-1);
  const [imageByte, setImageByte] = useState("");
  const [coffeeRoasters, setCoffeeRoasters] = useState([]);
  const [fetchingStarted, setFetchingStarted] = useState(false);
  // const backEndUrl = "http://127.0.0.1:5000";
  const backEndUrl = "https://coffee-rec-service.onrender.com"

  const DashboardNavbarStyle = {
    lineHeight: "25px",
    flexDirection: "column",
    flexWrap: "wrap",
    display: "flex",
    height: "50vh",
    listStyle: "none",
    // fontSize: "12px"
  };

  useEffect(() => {
    console.log("selected change to " + selected);
    setImageByte("");
  }, selected);

  const giveVisual = (endpoint) => {
    async function fetchVisual() {
      setFetchingStarted(true);
      const response = await fetch(backEndUrl + endpoint);
      const data = await response.json();
      if (imageByte === "") {
        setImageByte(data);
      }
      setFetchingStarted(false);
    }

    if (!fetchingStarted) {
      fetchVisual();
    }
  };

  const getCoffeeList = () => {
    async function fetchCoffeeList() {
      const response = await fetch(backEndUrl + "/get_coffee_roasters");
      const data = await response.json();
      console.log(data);
      setCoffeeRoasters(data);
    }

    fetchCoffeeList();
  };

  function DisplayUserInteractionVisualization() {
    if (imageByte === "") {
      giveVisual("/get_features/users/count");
    }

    return (
      <>
        <img
          src={"data:image/png;base64," + imageByte}
          width={500}
          height={500}
          alt=""
        />
      </>
    );
  }

  const ShowLoading = () => {
    return <>Loading...</>;
  };

  function DisplayCoffeeRoasterDistribution() {
    const [selectedCoffeeRoaster, setSelectedCoffeeRoaster] = useState("");
    const [coffeeRoasterName, setcoffeeRoasterName] = useState("")
    const [coffeeDescription, setCoffeeDescription] = useState("")

    const [coffeeData, setCoffeeData] = useState({name : '', description : '', pie_chart: ''})
    if (coffeeRoasters.length == 0) {
      getCoffeeList();
    }

    if (imageByte == "") {
    }

    const getCoffeeRoasterInformation = (coffee_id) => {
      async function fetchCoffeeRoasterInformation() {
        const response = await fetch(
          backEndUrl +
            "/get_coffee_roaster_feature_distribution?coffee_id=" +
            coffee_id
        );
        const data = await response.json();
        // console.log(data["description"])
        setCoffeeData({...coffeeData, name: data["coffeeRoasterName"], description: data["description"], pie_chart: data["imagebytes"]})  
      }

      fetchCoffeeRoasterInformation();
    };

    const handleCoffeeSelect = (coffeeRoaster) => {
      if (coffeeRoaster >= 0) {
        setCoffeeData({...coffeeData, name: '', description: '', pie_chart: ''})
        setSelectedCoffeeRoaster(coffeeRoaster);
        getCoffeeRoasterInformation(coffeeRoaster);
      }
    };

    const CoffeeRoasterSelect = () => {
      return (
        <select
          name="select"
          style={{ height: "50px" }}
          value={selectedCoffeeRoaster}
          onChange={(event) => handleCoffeeSelect(event.target.value)}
        >
          {<option value={-1}>select coffee roaster</option>}
          {coffeeRoasters.map(function (n, index) {
            return <option value={index}>{n}</option>;
          })}
        </select>
      );
    };

    function DisplayCoffeeRoasterInformation(name, description, imageByte) {
      return (
        <div style={{'display': 'inline-block'}}>
          <img
            src={"data:image/png;base64," + imageByte}
            width={400}
            height={300}
            alt=""
          />
          <br />
          <h6>Name:</h6> {name}
          <h6>Description:</h6> {description}
        </div>
      );
    }

    return (
      <>
        <CoffeeRoasterSelect />
        {coffeeData.pie_chart !== ''  ? (
          DisplayCoffeeRoasterInformation(coffeeData.name, coffeeData.description, coffeeData.pie_chart)
        ) : null}
      </>
    );
  }

  function DisplayWordFreqChartOfCoffeeReviews() {
    if (imageByte === "") {
      giveVisual("/visualize_top_feature_words_from_blind_review");
    }

    return (
      <>
        <img
          src={"data:image/png;base64," + imageByte}
          width={1100}
          height={1500}
          alt=""
        />
      </>
    );
  }

  function DisplayNMFVisualization() {
    if (imageByte === "" && fetchingStarted == false) {
      giveVisual("/visualize_feature_groups");
    }

    return (
      <>
        {imageByte !== "" ? (
          <>
            <img
              src={"data:image/png;base64," + imageByte}
              width={700}
              height={700}
              alt=""
            />
          </>
        ) : (
          <ShowLoading />
        )}
      </>
    );
  }

  function DisplayContent(i) {
    switch (i) {
      case 1: {
        return <DisplayUserInteractionVisualization />;
      }
      case 2: {
        return (
          <>
            <DisplayWordFreqChartOfCoffeeReviews />
          </>
        );
      }
      case 3: {
        return (
          <>
            <DisplayNMFVisualization />
          </>
        );
      }
      case 4: {
        return <DisplayCoffeeRoasterDistribution />;
      }
      case 5: {
        return (<DisplayNMFEvaluationCount />)
      }

      default: {
        return <></>;
      }
    }
    return <></>;
  }

  function DisplayNMFEvaluationCount () {
    if (imageByte == "") {
      giveVisual("/visualize_number_of_features")
    }


    return (<>{fetchingStarted ? <ShowLoading /> : <img
    src={"data:image/png;base64," + imageByte}
    width={1000}
    height={500}
    alt=""
  />}</>)
  }

  function displayContent(i) {
    console.log("that is " + i);
    setImageByte("");
    setSelected(i);
  }

  const tabs = [
    {
      id: 1,
      text: "User Features Selected Traffic",
      type: "descriptive",
      description: "The Bar Chart displays each features the number of user searched. This will be useful for identifying the popularity",
    },
    {
      id: 2,
      text: "Common Feature Words Appeared on coffeereviews Dataset",
      type: "descriptive",
      description: "The Bar Chart displays the number of feature words appeared throughout the coffee review based on the TF-IDF model setting. This visualization helped me to identify and eliminate the stop-words and also finding the right setting for the TF-IDF model that will generate the most amount of meaningful feature words in the top.",
    },
    {
      id: 3,
      text: "NMF Model Output",
      type: "non-descriptive",
      description: "The visualization of the NMF model output using WordCloud. This visualization helped me to identify the feature word from each group that makes the most sense.",
    },
    {
      id: 4,
      text: "Coffee Roaster Feature Distribution",
      type: "descriptive",
      description: "Displays the distribution of features for each coffee roaster selected.",
    },
    {
      id: 5,
      text: "NMF Model best fit",
      type: "descriptive",
      description: "Scatter plot visualization was used to find the peak value of the NMF evaluation. This was plotted using coherence score calculated for each number of component against number of component.",
    },
  ];

  return (
    <div style={{ display: "flex" }}>
      <div>
        <p>View Visualization of: </p>
        <ul className="dashboard-action-list" style={DashboardNavbarStyle}>
          {tabs.map((tab, index) => {
            return (
              <u>
                <li
                  onClick={() => displayContent(tab.id)}
                  style={{ color: index == selected - 1 ? "blue" : "black" }}
                >
                  {tab.id}
                  {". "}
                  {tab.text}
                </li>
              </u>
            );
          })}
        </ul>
        {selected >= 0 ? 
          <div style={{'width' : 300, padding: '12'}}>
            <h3>Type: {tabs[selected-1].type}</h3>
            <h4>{tabs[selected-1].description}</h4>
          </div>
         : null}
      </div>
      {/* <hr width="1" /> */}

      {selected > 0 ? DisplayContent(selected) : null}
    </div>
  );
}
