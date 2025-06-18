import React, { useState } from "react";
import axios from "axios";

function App() {
  const [zipFile, setZipFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [leaseResult, setLeaseResult] = useState(null);
  const [dependencyResult, setDependencyResult] = useState(null);
  const [planResult, setPlanResult] = useState(null);

  const handleFileChange = (e) => {
    setZipFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!zipFile) {
      alert("Please select a .zip file.");
      return;
    }

    const formData = new FormData();
    formData.append("files", zipFile);

    try {
      const response = await axios.post("http://localhost:5000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setUploadResult(response.data);
    } catch (error) {
      console.error("Upload Failed:", error);
      alert("Error uploading file.");
    }
  };

  const handleLeaseClick = () => {
    axios.get("http://localhost:5000/analyze/lease")
      .then((response) => setLeaseResult(response.data))
      .catch((error) => console.error("Lease Analysis Error:", error));
  };

  const handleDependencyClick = () => {
    axios.get("http://localhost:5000/analyze/dependencies")
      .then((response) => setDependencyResult(response.data))
      .catch((error) => console.error("Dependency Analysis Error:", error));
  };

  const handlePlanClick = () => {
    axios.get("http://localhost:5000/generate-plan")
      .then((response) => setPlanResult(response.data))
      .catch((error) => console.error("Plan Generation Error:", error));
  };

  return (
    <div className="App" style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>SkyBridge Cloud Migration</h1>

      {/* Upload Section */}
      <input type="file" accept=".zip" onChange={handleFileChange} />
      <button onClick={handleUpload} style={{ marginLeft: "10px" }}>
        Upload ZIP
      </button>

      {uploadResult && (
        <div style={{ marginTop: "20px" }}>
          <h3>Upload Result:</h3>
          <pre>{JSON.stringify(uploadResult, null, 2)}</pre>
        </div>
      )}

      {/* Analysis Buttons */}
      <div style={{ marginTop: "30px" }}>
        <button onClick={handleLeaseClick}>Analyze Lease</button>
        <button onClick={handleDependencyClick} style={{ marginLeft: "10px" }}>
          Analyze Dependencies
        </button>
        <button onClick={handlePlanClick} style={{ marginLeft: "10px" }}>
          Generate Migration Plan
        </button>
      </div>

      {/* Results */}
      {leaseResult && (
        <>
          <h3>Lease Analysis Result:</h3>
          <pre>{JSON.stringify(leaseResult, null, 2)}</pre>
        </>
      )}

      {dependencyResult && (
        <>
          <h3>Dependency Analysis Result:</h3>
          <pre>{JSON.stringify(dependencyResult, null, 2)}</pre>
        </>
      )}

      {planResult && (
        <>
          <h3>Migration Plan:</h3>
          <pre>{JSON.stringify(planResult, null, 2)}</pre>
        </>
      )}
    </div>
  );
}

export default App;
