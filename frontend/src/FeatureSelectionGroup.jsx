export default function FeatureSelectionGroup({features, handleOnChange, checkedState}) {
    return (<>{features.length !== 0 ? <DisplayFeatures features={features} handleOnChange={handleOnChange} checkedState={checkedState}/> : null}</>)
}

function DisplayFeatures({ features, handleOnChange, checkedState }) {
    return (
      <>
        <h3>Select Coffee Features:</h3>
        <ul
          className="coffee-feature-list"
          style={{
            "lineHeight": "25px",
            "flexDirection": "column",
            "flexWrap": "wrap",
            "display": "flex",
            "height": "15vh",
            "listStyle": "none",
          }}
        >
          {features.map((feature, index) => {
            return (
              <li key={index}>
                <div
                  className="coffee-feature-list-item"
                  style={{ flex: "1 0 25%" }}
                >
                  <input
                    type="checkbox"
                    id={`custom-checkbox-${index}`}
                    name={feature}
                    value={feature}
                    checked={checkedState[index]}
                    onChange={() => handleOnChange(index)}
                  />
                  <label htmlFor={`custom-checkbox-${index}`}>{feature}</label>
                </div>
              </li>
            );
          })}
        </ul>
      </>
    );
  }

