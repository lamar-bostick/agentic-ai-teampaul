import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [dependencies, setDependencies] = useState(null);

  function handleClick() {
    axios.get("http://localhost:5000/analyze/dependencies")
      .then(response => {
        setDependencies(response.data);
      })
      .catch(error => {
        console.error("Axios error:", error);
      });
  }

  return (
    <div className="App">
      <h1>SkyBridge Cloud Migration</h1>
      <button onClick={handleClick}>
        Analyze Dependencies
      </button>

      {dependencies && (
        <pre>{JSON.stringify(dependencies, null, 2)}</pre>
      )}
    </div>
  );
}

export default App;
