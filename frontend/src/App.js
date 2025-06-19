import React, { useState } from "react";
import axios from "axios";

function App() {
  const [zipFile, setZipFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);

  const [leasePrompt, setLeasePrompt] = useState("");
  const [leaseResult, setLeaseResult] = useState(null);

  const [dependencyPrompt, setDependencyPrompt] = useState("");
  const [dependencyResult, setDependencyResult] = useState(null);

  const [migrationPrompt, setMigrationPrompt] = useState("");
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
    axios
      .post("http://localhost:5000/analyze/lease", { prompt: leasePrompt })
      .then((response) => setLeaseResult(response.data))
      .catch((error) => console.error("Lease Analysis Error:", error));
  };

  const handleDependencyClick = () => {
    axios
      .post("http://localhost:5000/analyze/dependencies", { prompt: dependencyPrompt })
      .then((response) => setDependencyResult(response.data))
      .catch((error) => console.error("Dependency Analysis Error:", error));
  };

  const handlePlanClick = () => {
    axios
      .post("http://localhost:5000/generate-plan", { prompt: migrationPrompt })
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

      {/* Lease Agent Section */}
      <div style={{ marginTop: "30px" }}>
        <h2>Lease Agent Prompt</h2>
        <textarea
          rows={4}
          cols={60}
          value={leasePrompt}
          onChange={(e) => setLeasePrompt(e.target.value)}
          placeholder="Enter your lease analysis prompt here..."
          style={{ display: "block", marginBottom: "10px" }}
        />
        <button onClick={handleLeaseClick}>Analyze Lease</button>

        {leaseResult && (
          <>
            <h3 style={{ marginTop: "20px" }}>Lease Analysis Result:</h3>
            <textarea
              readOnly
              value={leaseResult.response || JSON.stringify(leaseResult, null, 2)}
              rows={10}
              style={{
                width: "100%",
                whiteSpace: "pre-wrap",
                overflowY: "auto",
                padding: "1rem",
                fontFamily: "monospace",
                borderRadius: "6px",
                border: "1px solid #ccc",
                background: "#f9f9f9",
              }}
            />
          </>
        )}
      </div>

      {/* Dependency Agent Section */}
      <div style={{ marginTop: "40px" }}>
        <h2>Dependency Agent Prompt</h2>
        <textarea
          rows={4}
          cols={60}
          value={dependencyPrompt}
          onChange={(e) => setDependencyPrompt(e.target.value)}
          placeholder="Enter your dependency analysis prompt here..."
          style={{ display: "block", marginBottom: "10px" }}
        />
        <button onClick={handleDependencyClick}>Analyze Dependencies</button>

        {dependencyResult && (
          <>
            <h3 style={{ marginTop: "20px" }}>Dependency Analysis Result:</h3>
            <textarea
              readOnly
              value={dependencyResult.response || JSON.stringify(dependencyResult, null, 2)}
              rows={10}
              style={{
                width: "100%",
                whiteSpace: "pre-wrap",
                overflowY: "auto",
                padding: "1rem",
                fontFamily: "monospace",
                borderRadius: "6px",
                border: "1px solid #ccc",
                background: "#f9f9f9",
              }}
            />
          </>
        )}
      </div>

      {/* Migration Plan Agent Section */}
      <div style={{ marginTop: "40px" }}>
        <h2>Migration Plan Prompt</h2>
        <textarea
          rows={4}
          cols={60}
          value={migrationPrompt}
          onChange={(e) => setMigrationPrompt(e.target.value)}
          placeholder="Enter your migration planning prompt here..."
          style={{ display: "block", marginBottom: "10px" }}
        />
        <button onClick={handlePlanClick}>Generate Migration Plan</button>

        {planResult && (
          <>
            <h3 style={{ marginTop: "20px" }}>Migration Plan Result:</h3>
            <textarea
              readOnly
              value={planResult.response || JSON.stringify(planResult, null, 2)}
              rows={10}
              style={{
                width: "100%",
                whiteSpace: "pre-wrap",
                overflowY: "auto",
                padding: "1rem",
                fontFamily: "monospace",
                borderRadius: "6px",
                border: "1px solid #ccc",
                background: "#f9f9f9",
              }}
            />
          </>
        )}
      </div>
    </div>
  );
}

export default App;
