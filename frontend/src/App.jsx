import { useState, useEffect } from 'react';
import './App.css';
import SoilPrediction from './components/SoilPrediction';
import DiseaseDetection from './components/DiseaseDetection';
import AIExpertChat from './components/AIExpertChat';

function App() {
  const [activeTab, setActiveTab] = useState('soil');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const webhookUrl = import.meta.env.VITE_N8N_WEBHOOK_URL;

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setResult(null);
    setError(null);
  };

  const executeWebhook = async (payload, isFormData = false) => {
    if (!webhookUrl) {
      setError("Webhook URL is missing. Please configure VITE_N8N_WEBHOOK_URL in your .env file.");
      return null;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const options = { method: 'POST' };
      if (isFormData) {
        options.body = payload;
      } else {
        options.headers = { 'Content-Type': 'application/json' };
        options.body = JSON.stringify(payload);
      }

      const response = await fetch(webhookUrl, options);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'error') {
        setError(data.message);
        return null;
      }
      
      // Fix for Langchain AI Agent outputs in Disease Detection
      if (data.status === 'success' && data.type === 'chatbot_response') {
        try {
          let str = data.data.chatbot_response;
          if (str.includes('```json')) {
            str = str.split('```json')[1].split('```')[0].trim();
          } else if (str.includes('```')) {
            str = str.split('```')[1].split('```')[0].trim();
          }
          const parsed = JSON.parse(str);
          if (parsed.disease_name || parsed.disease || parsed.treatment) {
             data.type = 'disease_detection';
             data.data = {
               disease_name: parsed.disease_name || parsed.disease || 'Unknown',
               treatment: parsed.treatment || 'Consult agronomist.'
             };
          } else if (parsed.recommended_crop || parsed.crop) {
             data.type = 'crop_prediction';
             data.data = {
               recommended_crop: parsed.recommended_crop || parsed.crop || 'Unknown',
               confidence_score: parsed.confidence_score || null
             };
          }
        } catch(e) {
          console.warn("Could not parse LLM output as JSON", e);
        }
      }

      setResult(data);
      return data;
      
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pwa-layout">
      {/* Dynamic Background */}
      <div className="background-elements">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
      </div>

      {/* Mobile Header */}
      <header className="mobile-header mobile-only">
        <span className="icon">🌿</span>
        <h1>AgriAI</h1>
      </header>

      {/* Navigation (Sidebar on Desktop, Bottom bar on Mobile) */}
      <nav className="pwa-nav">
        <div className="nav-brand desktop-only">
          <span className="icon">🌿</span>
          <h1>AgriAI Solutions</h1>
          <p className="subtitle">Empowering farmers with AI</p>
        </div>
        
        <div className="nav-links">
          <button 
            className={`nav-item ${activeTab === 'soil' ? 'active' : ''}`}
            onClick={() => handleTabChange('soil')}
          >
            <span className="nav-icon">🌱</span>
            <span className="nav-label">Crop Predict</span>
          </button>
          <button 
            className={`nav-item ${activeTab === 'disease' ? 'active' : ''}`}
            onClick={() => handleTabChange('disease')}
          >
            <span className="nav-icon">🐞</span>
            <span className="nav-label">Disease Detect</span>
          </button>
          <button 
            className={`nav-item ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => handleTabChange('chat')}
          >
            <span className="nav-icon">💬</span>
            <span className="nav-label">AI Chat</span>
          </button>
        </div>
      </nav>

      <main className="pwa-main">
        <div className="content-wrapper">
          {/* Tab Render Area */}
          <div className={`tab-panel ${activeTab === 'soil' ? 'active-panel' : ''}`}>
            {activeTab === 'soil' && <SoilPrediction executeWebhook={executeWebhook} />}
          </div>
          
          <div className={`tab-panel ${activeTab === 'disease' ? 'active-panel' : ''}`}>
            {activeTab === 'disease' && <DiseaseDetection executeWebhook={executeWebhook} />}
          </div>
          
          <div className={`tab-panel ${activeTab === 'chat' ? 'active-panel' : ''}`}>
            {activeTab === 'chat' && <AIExpertChat webhookUrl={webhookUrl} />}
          </div>
        </div>

        {/* Global Loading Overlay */}
        {loading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
            <p className="pulse-text">Analyzing data with AI...</p>
          </div>
        )}

        {/* Global Error Toast */}
        {error && (
          <div className="error-toast">
            <div className="error-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22ZM12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12 4C7.58172 4 4 7.58172 4 12C4 16.4183 7.58172 20 12 20ZM11 15H13V17H11V15ZM11 7H13V13H11V7Z" fill="currentColor"/>
              </svg>
            </div>
            <div className="error-content">
              <strong>Something went wrong</strong>
              <p>{error}</p>
            </div>
            <button className="error-close" onClick={() => setError(null)}>×</button>
          </div>
        )}

        {/* Global Result Display for Soil & Disease */}
        {result && !error && activeTab !== 'chat' && (
          <div className="result-overlay">
            <div className="result-container">
            <div className="result-header">
              <h3>Analysis Result</h3>
              <button className="close-btn" onClick={() => setResult(null)}>×</button>
            </div>
            <div className="result-content">
              {result?.type === 'crop_prediction' ? (
                <div className="result-card">
                  <div className="result-field">
                    <strong>Recommended Crop</strong>
                    <span style={{ fontSize: '1.8rem', color: 'var(--primary-dark)', display: 'block', marginTop: '4px' }}>
                      🌱 {result.data.recommended_crop} 
                      {result.data.confidence_score && ` (${(result.data.confidence_score * 100).toFixed(1)}%)`}
                    </span>
                  </div>
                </div>
              ) : result?.type === 'disease_detection' ? (
                <div className="result-card">
                  <div className="result-field">
                    <strong>Detected Disease</strong>
                    <span style={{ fontSize: '1.4rem', color: 'var(--danger)', display: 'block', marginTop: '4px' }}>
                      🐞 {result.data.disease_name}
                    </span>
                  </div>
                  <div className="result-field">
                    <strong>Recommended Treatment</strong>
                    <span style={{ fontSize: '1.1rem', display: 'block', marginTop: '4px' }}>
                      {result.data.treatment}
                    </span>
                  </div>
                </div>
              ) : result?.type === 'chatbot_response' ? (
                <div className="result-card">
                  <div className="result-field">
                    <strong>AI Analysis Response</strong>
                    <span style={{ fontSize: '1.1rem', display: 'block', marginTop: '4px', whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>
                      {result.data.chatbot_response.replace(/```json|```/g, '').trim()}
                    </span>
                  </div>
                </div>
              ) : (
                <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word', background: '#f5f5f5', padding: '1rem', borderRadius: '8px' }}>
                  {JSON.stringify(result, null, 2)}
                </pre>
              )}
            </div>
          </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
