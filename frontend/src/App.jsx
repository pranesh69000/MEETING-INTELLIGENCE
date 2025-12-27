import { useState, useEffect } from 'react'
import axios from 'axios'
import './index.css'

const API_URL = "http://localhost:8000";

function App() {
  const [status, setStatus] = useState({
    is_recording: false,
    is_processing: false,
    message: "Ready to join meeting",
    last_transcript: ""
  });

  const [meetingLink, setMeetingLink] = useState("");
  const [activeTab, setActiveTab] = useState("summary");
  const [parsedReport, setParsedReport] = useState({
    summary: "No summary available yet.",
    actions: "No action items detected.",
    transcript: "Waiting for recording..."
  });

  useEffect(() => {
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  // Parse the raw markdown into sections when it changes
  useEffect(() => {
    if (status.last_transcript) {
      const text = status.last_transcript;

      // Simple string splitting based on headers
      // Assumes format: # Meeting Intelligence Report ... ## Executive Summary ... ## Action Items ... ## Full Transcript

      const summaryMatch = text.split("## 📝 Executive Summary")[1]?.split("## 🚀 Action Items")[0] || "";
      const actionsMatch = text.split("## 🚀 Action Items & Key Tasks")[1]?.split("## 💬 Full Transcript")[0] || text.split("## 🚀 Action Items")[1]?.split("## 💬 Full Transcript")[0] || "";
      const transcriptMatch = text.split("## 💬 Full Transcript")[1] || text;

      setParsedReport({
        summary: summaryMatch.trim() || "Generating summary...",
        actions: actionsMatch.trim() || "Scanning for tasks...",
        transcript: transcriptMatch.trim() || text
      });

      // Auto-switch to summary when done processing
      if (!status.is_processing && !status.is_recording && text.length > 50) {
        // Keep user on current tab unless it was empty
      }
    }
  }, [status.last_transcript, status.is_processing]);

  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API_URL}/status`);
      setStatus(prev => ({
        ...res.data,
        // Only update message if it changed to avoid jitter
        message: res.data.message
      }));
    } catch (err) {
      console.error("Error fetching status:", err);
    }
  };

  const startRecording = async () => {
    if (meetingLink && !meetingLink.startsWith("http")) {
      alert("Please enter a valid URL (https://...)");
      return;
    }

    if (meetingLink) {
      window.open(meetingLink, '_blank');
    }

    try {
      await axios.post(`${API_URL}/start`);
    } catch (err) {
      alert("Failed to start: " + (err.response?.data?.detail || err.message));
    }
  };

  const stopRecording = async () => {
    try {
      await axios.post(`${API_URL}/stop`);
    } catch (err) {
      alert("Failed to stop: " + (err.response?.data?.detail || err.message));
    }
  };

  const uploadLast = async () => {
    try {
      const res = await axios.post(`${API_URL}/upload_last`);
      alert(res.data.link ? "Uploaded: " + res.data.link : res.data.message);
    } catch (err) {
      alert("Upload failed");
    }
  }

  return (
    <div className="app-container">
      <header>
        <div className="brand">
          <h1>🎙️ Meeting Intelligence</h1>
        </div>
        <div className={`status-badge ${status.is_recording ? 'recording' : status.is_processing ? 'processing' : 'idle'}`}>
          {status.is_recording ? '● Recording' : status.is_processing ? '⚡ Processing' : '● Idle'}
        </div>
      </header>

      <main>
        {/* Sidebar Controls */}
        <aside className="sidebar">
          <div className="card meeting-launcher">
            <h3>Start New Meeting</h3>
            <div className="input-group">
              <input
                type="text"
                placeholder="Paste Zoom/Meet Link here..."
                value={meetingLink}
                onChange={(e) => setMeetingLink(e.target.value)}
              />
            </div>

            {!status.is_recording ? (
              <button className="btn btn-primary" onClick={startRecording}>
                {meetingLink ? "Launch & Record" : "Start Recording"}
              </button>
            ) : (
              <button className="btn btn-danger" onClick={stopRecording}>
                Stop & Process
              </button>
            )}

            <p className="status-message">{status.message}</p>
          </div>

          <div className="card actions">
            <h3>Exports</h3>
            <button className="btn btn-outline" onClick={uploadLast} disabled={!status.last_transcript}>
              ☁️ Re-Sync to Drive
            </button>
          </div>
        </aside>

        {/* Main Content Areas */}
        <section className="content-area">
          <div className="tabs">
            <div
              className={`tab ${activeTab === 'summary' ? 'active' : ''}`}
              onClick={() => setActiveTab('summary')}
            >
              📝 Summary
            </div>
            <div
              className={`tab ${activeTab === 'actions' ? 'active' : ''}`}
              onClick={() => setActiveTab('actions')}
            >
              🚀 Action Items
            </div>
            <div
              className={`tab ${activeTab === 'transcript' ? 'active' : ''}`}
              onClick={() => setActiveTab('transcript')}
            >
              💬 Transcript
            </div>
          </div>

          <div className="tab-content">
            {status.last_transcript ? (
              <>
                {activeTab === 'summary' && (
                  <div className="markdown-body">
                    {parsedReport.summary || <i>No summary availability.</i>}
                  </div>
                )}
                {activeTab === 'actions' && (
                  <div className="markdown-body">
                    <ul>
                      {parsedReport.actions.split('\n').map((line, i) => (
                        line.trim() && <li key={i}>{line.replace('- ', '')}</li>
                      ))}
                    </ul>
                    {parsedReport.actions.includes("No explicit") && <i>No action items detected.</i>}
                  </div>
                )}
                {activeTab === 'transcript' && (
                  <pre>{parsedReport.transcript}</pre>
                )}
              </>
            ) : (
              <div className="empty-state">
                Start a recording to see intelligence insights here.
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
