import React, { useEffect, useState } from "react";
import Table from "./Table";
import FeatureSelectionGroup from "./FeatureSelectionGroup"


export default function Home() {

  const [features, setFeatures] = useState([]);
  const [showFeatures, setShowFeatures] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [checkedState, setCheckedState] = useState([]);
  const [recommenderButtonSelected, setRecommenderButtonSelected] = useState(false)
  const [fetchingFeatures, setFetchingFeatures] = useState(true)

  // const backEndUrl = "http://127.0.0.1:5000"  
  const backEndUrl = "https://coffee-rec-service.onrender.com"


  const FetchCoffeeFeaturesFromApi = () => {
    async function fetchMyAPI() {
      const response = await fetch(backEndUrl + "/get_features");
      const data_sp = await response.json();

      setFeatures(data_sp);
      setCheckedState(new Array(data_sp.length).fill(false));
      setFetchingFeatures(false)
      setShowFeatures(true);
      
    }

    fetchMyAPI();
  };

  const handleOnChange = (position) => {
    const updatedCheckedState = checkedState.map((item, index) =>
      index === position ? !item : item
    );

    setCheckedState(updatedCheckedState);
  };

  useEffect(() => {
    FetchCoffeeFeaturesFromApi();
  }, []);

  const generateCoffeeRecommendationUrl = () => {
    let url = backEndUrl + "/get_recommendations?";
    console.log(url)
    for (let i = 0; i < checkedState.length; i++) {
      if (checkedState[i]) {
        const feature_selected = features[i];
        url += "features=";
        url += feature_selected.trim();
        url += "&";
      }
    }
    return url;
  };

  const giveRecs = () => {
    setRecommendations([])
    setRecommenderButtonSelected(true)
    async function fetchRecommendations() {
      const response = await fetch(generateCoffeeRecommendationUrl());
      const data = await response.json();
      setRecommendations(data);
      setRecommenderButtonSelected(false)
    }
    
    fetchRecommendations();
  };

  const showLoading = () => {
    return (<>Loading Feature Data...</>)
  }

  function DisplayFeatureGroup() {
    return (<><FeatureSelectionGroup
      showFeatures={showFeatures}
      features={features}
      handleOnChange={handleOnChange}
      checkedState={checkedState}
    />
    <button onClick={() => giveRecs()}>Recommend me Coffee!</button></>)
  }

    return (
      <>
        <h1>Welcome to Coffee Recommender Service</h1>
        {features.length > 0 ? <DisplayFeatureGroup /> : showLoading()}
        <DisplayCoffeeRecommendations recommenderButtonSelected={recommenderButtonSelected} recommendations={recommendations} />
      </>
    );
}

function DisplayCoffeeRecommendations({ recommendations, recommenderButtonSelected }) {
    if (recommenderButtonSelected) {
      return (
        <>
          {recommendations.length > 0 ? (
            <Table
              recommendations={recommendations}
              headerData={["Coffee Roaster", "Description", "Feature Comparison"]}
            />
          ) : <p>Loading...</p>}
        </>
      );
    } else {
      return (
        <>
          {recommendations.length > 0 ? (
            <Table
              recommendations={recommendations}
              headerData={["Coffee Roaster", "Description", "Feature Comparison"]}
            />
          ) :null}
        </>
      );

    }
    return (
      <>
        <p></p>
      </>
    );
  }
  