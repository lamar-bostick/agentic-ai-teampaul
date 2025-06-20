import React, { useState } from "react";
import Navbar from "./components/Navbar";
import axios from "axios";
import FileSaver from "file-saver";
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
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

  const callAgent = async (endpoint, promptText = null) => {
    try {
      let response;
      if (promptText) {
        response = await axios.post(
          `http://localhost:5000/${endpoint}`,
          { prompt: promptText },
          { headers: { "Content-Type": "application/json" } }
        );
      } else {
        response = await axios.post(`http://localhost:5000/${endpoint}`);
      }
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

  const formatResponse = (results) => {
    try {
      const parsed = JSON.parse(results);
      const text = parsed.response;

      return text
        .replace(/\n###\s*/g, "<h5 class='mt-3'>")
        .replace(/\n\d+\.\s/g, "<br /><strong>•</strong> ")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\n/g, "<br />");
    } catch {
      return results;
    }
  };

  return (
    <div>
      <Navbar />
      <div className="container mt-3">
        <h1 className="text-center mb-1">SkyBridge</h1>
        <p className="text-center mt-2 fw-bold">
          Plan cloud migration for your company, with ease.
        </p>

        <div className="text-center my-3">
          <p className="fs-6">Upload a zip file or individual files to get started.</p>
          <div className="d-flex justify-content-center align-items-end gap-1">
            <input
              type="file"
              className="form-control shadow-subtle"
              onChange={handleFileChange}
              multiple
              style={{ maxWidth: "600px" }}
            />
            <button
              className="btn btn-primary mt-0 mb-3"
              onClick={uploadZipFile}
              disabled={!zipFile}
            >
              Upload
            </button>
          </div>
          {uploadMessage && (
            <p
              className={`mt-2 ${
                uploadMessage.includes("success") ? "text-success" : "text-danger"
              }`}
            >
              {uploadMessage}
            </p>
          )}
        </div>

        <div className="text-center my-4">
          <p><strong>Try One of These Functions:</strong></p>
          <div className="d-flex justify-content-center flex-wrap gap-1">
            <button
              className="btn btn-outline-primary custom shadow-subtle"
              onClick={() => callAgent("generate-plan")}
            >
              Build a Cloud Migration Plan
            </button>
            <button
              className="btn btn-outline-primary custom shadow-subtle"
              onClick={() => callAgent("analyze/dependencies")}
            >
              Analyze Application Dependencies
            </button>
            <button
              className="btn btn-outline-primary custom shadow-subtle"
              onClick={() => callAgent("analyze/lease", "Please provide important lease information for all leases")}
            >
              Analyze Lease Information
            </button>
          </div>
        </div>

        <div className="my-4">
          <p><strong>Or, Ask A Question About Your Data:</strong></p>
          <textarea
            className="form-control shadow-subtle"
            rows="3"
            placeholder="Create a 3 year migration plan for the following data set..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
          <div className="d-flex justify-content-end mt-2">
            <button className="btn btn-outline-secondary me-2" onClick={clearResults}>
              Clear
            </button>
            <button className="btn btn-primary" onClick={submitPrompt}>
              Submit Prompt
            </button>
          </div>
        </div>

        <div className="card mt-4 shadow-subtle">
          <div className="card-header d-flex justify-content-between align-items-center bg-light">
            <strong>Results</strong>
            <div>
              <button
                className="btn btn-outline-secondary btn-sm me-2"
                onClick={downloadResult}
                disabled={!results}
              >
                <i className="bi bi-download me-1"></i> Download
              </button>
              <button
                className="btn btn-outline-danger btn-sm"
                onClick={clearResults}
              >
                <i className="bi bi-x-circle me-1"></i> Clear Window
              </button>
            </div>
          </div>
          <div
            className="card-body"
            style={{ maxHeight: "1200px", overflowY: "auto", whiteSpace: "pre-wrap" }}
          >
            {results ? (
              <div
                dangerouslySetInnerHTML={{
                  __html: formatResponse(results),
                }}
              />
            ) : (
              <p className="text-muted fs-6">Results text or files go here.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
