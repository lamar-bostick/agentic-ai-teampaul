import React, { useState } from 'react';
import axios from 'axios';

function AgentDashboard() {
  const [files, setFiles] = useState([]);
  const [leaseResults, setLeaseResults] = useState(null);
  const [dependencyResults, setDependencyResults] = useState(null);
  const [planResults, setPlanResults] = useState(null);
  const [promptText, setPromptText] = useState('');

  const handleUpload = async (e) => {
    const fileList = e.target.files;
    const formData = new FormData();
    for (let file of fileList) {
      formData.append('files', file);
    }
    try {
      const res = await axios.post('http://localhost:5000/upload', formData);
      alert('Files uploaded and processed!');
      console.log(res.data);
    } catch (err) {
      alert('Upload failed.');
      console.error(err);
    }
  };

  const handleLeaseAnalysis = async () => {
    const res = await axios.get('http://localhost:5000/analyze/lease');
    setLeaseResults(res.data);
  };

  const handleDependencyAnalysis = async () => {
    const res = await axios.get('http://localhost:5000/analyze/dependencies');
    setDependencyResults(res.data);
  };

  const handleGeneratePlan = async () => {
    const res = await axios.post('http://localhost:5000/generate-plan', {
      prompt: promptText
    });
    setPlanResults(res.data);
  };

  return (
    <div className="flex flex-col items-center py-10 px-4 max-w-2xl mx-auto">
      <h1 className="text-4xl font-semibold mb-1">SkyBridge</h1>
      <h2 className="text-xl mb-6 text-gray-600">Your Cloud Migration Companion</h2>

      <p className="text-center mb-4 text-gray-700">
        Interested in migrating your company’s data to a cloud platform? I’m your dedicated companion.<br />
        Upload a zip file or individual files to get started.
      </p>

      <input
        type="file"
        multiple
        onChange={handleUpload}
        className="mb-8 p-2 border border-gray-300 rounded-md"
      />

      <div className="text-gray-700 font-medium mb-2">Ask a Question, or Give Me a Task:</div>

      <div className="flex flex-wrap justify-center gap-3 mb-6">
        <button onClick={handleGeneratePlan} className="border border-gray-400 px-4 py-2 rounded-md hover:bg-gray-100">Build a Cloud Migration Plan</button>
        <button onClick={handleDependencyAnalysis} className="border border-gray-400 px-4 py-2 rounded-md hover:bg-gray-100">Analyze Application Dependencies</button>
        <button onClick={handleLeaseAnalysis} className="border border-gray-400 px-4 py-2 rounded-md hover:bg-gray-100">Analyze Lease ROI</button>
      </div>

      <textarea
        className="border border-gray-300 rounded-md w-full p-3 mb-4"
        rows="3"
        value={promptText}
        onChange={(e) => setPromptText(e.target.value)}
        placeholder="Create a 5 year migration plan for the following data.."
      ></textarea>
      <button onClick={handleGeneratePlan} className="px-6 py-2 bg-gray-300 hover:bg-gray-400 text-sm rounded-md">Submit Prompt</button>

      <div className="mt-10 text-left w-full">
        {leaseResults && <pre className="bg-gray-50 border p-4 rounded-md overflow-x-auto">Lease Analysis: {JSON.stringify(leaseResults, null, 2)}</pre>}
        {dependencyResults && <pre className="bg-gray-50 border p-4 rounded-md overflow-x-auto mt-4">Dependency Analysis: {JSON.stringify(dependencyResults, null, 2)}</pre>}
        {planResults && <pre className="bg-gray-50 border p-4 rounded-md overflow-x-auto mt-4">Migration Plan: {JSON.stringify(planResults, null, 2)}</pre>}
      </div>
    </div>
  );
}

export default AgentDashboard;
