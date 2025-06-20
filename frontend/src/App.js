import React, { useState } from "react";
import Navbar from "./components/Navbar";
import axios from "axios";
import FileSaver from "file-saver";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [uploadMessage, setUploadMessage] = useState("");
  const [results, setResults] = useState("");
  const [zipFile, setZipFile] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setZipFile(file);
    if (file) {
      setUploadMessage("File uploaded successfully!");
    } else {
      setUploadMessage("File upload failed.");
    }
  };

  const uploadZipFile = async () => {
    if (!zipFile) return;
    const formData = new FormData();
    formData.append("files", zipFile);

    try {
      const response = await axios.post("http://localhost:5000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setResults(JSON.stringify(response.data, null, 2));
    } catch (error) {
      setResults("Upload failed: " + error.message);
    }
  };

  const callAgent = async (endpoint) => {
    try {
      const response = await axios.post(`http://localhost:5000/${endpoint}`);
      setResults(JSON.stringify(response.data, null, 2));
    } catch (error) {
      setResults(`Error contacting backend: ${error.message}`);
    }
  };

  const submitPrompt = async () => {
    try {
      const response = await axios.post("http://localhost:5000/analyze/prompt", {
        prompt,
      });
      setResults(response.data.result);
    } catch (error) {
      setResults(`Error submitting prompt: ${error.message}`);
    }
  };

  const downloadResult = () => {
    const blob = new Blob([results], { type: "text/plain;charset=utf-8" });
    FileSaver.saveAs(blob, "results.txt");
  };

  const clearResults = () => {
    setPrompt("");
    setResults("");
    setUploadMessage("");
    setZipFile(null);
  };

  return (
    <div>
      <Navbar />
      <div className="container mt-5">
        <h2 className="text-center">SkyBridge</h2>
        <p className="text-center">
          Plan cloud migration for your company, with ease.
        </p>

        <div className="text-center my-4">
          <p>Upload a zip file or individual files to get started.</p>
          <input
            type="file"
            className="form-control"
            onChange={handleFileChange}
            multiple
          />
          <button
            className="btn btn-success mt-2"
            onClick={uploadZipFile}
            disabled={!zipFile}
          >
            Upload
          </button>
          {uploadMessage && (
            <p
              className={`mt-2 text-$
                {uploadMessage.includes("success") ? "success" : "danger"}`}
            >
              {uploadMessage}
            </p>
          )}
        </div>

        <div className="text-center my-4">
          <p><strong>Try One of These Functions:</strong></p>
          <button
            className="btn btn-outline-primary custom me-2 mb-2"
            onClick={() => callAgent("generate-plan")}
          >
            Build a Cloud Migration Plan
          </button>
          <button
            className="btn btn-outline-primary custom me-2 mb-2"
            onClick={() => callAgent("analyze/dependencies")}
          >
            Analyze Application Dependencies
          </button>
          <button
            className="btn btn-outline-primary custom mb-2"
            onClick={() => callAgent("analyze/lease")}
          >
            Analyze Lease Information
          </button>
        </div>

        <div className="my-4">
          <p><strong>Or, Ask A Question About Your Data:</strong></p>
          <textarea
            className="form-control"
            rows="3"
            placeholder="Create a 3 year migration plan for the following data set..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
          <div className="d-flex justify-content-end mt-2">
            <button className="btn btn-secondary me-2" onClick={clearResults}>
              Clear
            </button>
            <button className="btn btn-primary" onClick={submitPrompt}>
              Submit Prompt
            </button>
          </div>
        </div>

        <div className="card mt-4">
          <div className="card-header d-flex justify-content-between align-items-center">
            <strong>Results</strong>
            <div>
              <button
                className="btn btn-outline-secondary btn-sm me-2"
                onClick={downloadResult}
                disabled={!results}
              >
                Download
              </button>
              <button
                className="btn btn-outline-danger btn-sm"
                onClick={clearResults}
              >
                Close Window
              </button>
            </div>
          </div>
          <div className="card-body" style={{ maxHeight: "300px", overflowY: "auto" }}>
            {results || <p className="text-muted">Results text or files go here.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
