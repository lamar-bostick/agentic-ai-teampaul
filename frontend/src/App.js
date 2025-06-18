import React from 'react';
import './App.css';
import AgentDashboard from './components/AgentDashboard';

function App() {
  return (
    <div className="min-h-screen font-sans">
      <nav className="flex justify-end bg-purple-200 py-2 px-6 shadow-sm text-sm">
        <ul className="flex space-x-6">
          <li className="hover:underline cursor-pointer">Get Started</li>
          <li className="hover:underline cursor-pointer">About</li>
          <li className="hover:underline cursor-pointer">Contact</li>
        </ul>
      </nav>
      <AgentDashboard />
    </div>
  );
}

export default App;
