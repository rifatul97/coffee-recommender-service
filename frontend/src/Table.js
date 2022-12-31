import { useState } from "react";

const Table = (props) => {
  const { recommendations, headerData, recommenderButtonSelected } = props;
  const [selected, setSelected] = useState(false);

  const tableHeader = () => {
    return headerData.map((data, idx) => {
      return (
        <td key={idx} style={{ fontWeight: "bold" }}>
          {data}
        </td>
      );
    });
  };

  const returnTableData = () => {
    return recommendations.map((recommendation, idx) => {
      const imagebytes = recommendation["imagebytes"];
      console.log("here => " + imagebytes);
      return (
        <tr data-id={idx} key={idx}>
          <td>{recommendation["coffeeRoasterName"]}</td>
          <td>{recommendation["description"]}</td>
          <td>
            <img
              src={"data:image/png;base64," + imagebytes}
              width={400}
              height={300}
              alt=""
            />
          </td>
        </tr>
      );
    });
  };

  const FeedbackButton = ({ selected }) => {
    if (selected) {
      return <>Thank you for the feedback!</>;
    }
    return (
      <>
        {
          <center><form>
            <b><i>Did you found the recommender system helpful?</i></b> Yes!!
            <input
              type="radio"
              name="agree"
              value="yes"
              onClick={() => setSelected(true)}
            />
             No.. 
            <input
              type="radio"
              name="agree"
              value="no"
              onClick={() => setSelected(true)}
            />
            <br />
             </form></center>
        }
      </>
    );
  };

  const ShowTable = () => {
    return (<>  <FeedbackButton selected={selected} />
    <br />
    <br />
    <table>
      <thead>
        <tr>{tableHeader()}</tr>
      </thead>
      <tbody>{returnTableData()}</tbody>
    </table></>)
  }

  function ShowLoading() {
    return (<p>
    Loading...
    </p>)
  }


  return (
    <>
      {recommenderButtonSelected ? ShowLoading() : ShowTable()}
    </>
  );
};

export default Table;
