import { useState } from 'react';
import { Routes, Route, NavLink, useNavigate, useLocation } from 'react-router-dom';
import './index.css';
import SoilPrediction from './components/SoilPrediction';
import DiseaseDetection from './components/DiseaseDetection';
import AIExpertChat from './components/AIExpertChat';
import HomePage from './components/HomePage';

const FAST_API_BASE = 'http://localhost:8000/api';

const NAV_ITEMS = [
  { id: 'home',    path: '/',         icon: '🏡', label: 'Home',          badge: null },
  { id: 'disease', path: '/disease',    icon: '🔬', label: 'Disease Detect', badge: 'AI' },
  { id: 'soil',    path: '/soil',       icon: '🌱', label: 'Crop Predict',   badge: null },
  { id: 'chat',    path: '/chat',       icon: '💬', label: 'AI Agronomist',  badge: null },
];

function App() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  /** ─── Soil / Crop Prediction via FastAPI ───────────────────────────── */
  const predictCrop = async (payload) => {
    const res = await fetch(`${FAST_API_BASE}/predict-crop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  };

  /** ─── Disease Detection via FastAPI ─────────────────────────────────── */
  const detectDisease = async (formData) => {
    const res = await fetch(`${FAST_API_BASE}/predict-disease`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  };

  /** ─── AI Chat via FastAPI ───────────────────────────────────────────── */
  const sendChat = async (text, history = []) => {
    const res = await fetch(`${FAST_API_BASE}/chat-agronomist`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, history }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    if (data.status === 'success' && data.type === 'chatbot_response') {
      return data.data.chatbot_response;
    }
    return JSON.stringify(data);
  };

  const goTo = (page) => navigate(page);

  return (
    <>
      {/* Ambient Background */}
      <div className="bg-ambient">
        <div className="bg-blob bg-blob-1" />
        <div className="bg-blob bg-blob-2" />
        <div className="bg-blob bg-blob-3" />
      </div>

      <div className={`app-shell ${isCollapsed ? 'collapsed' : ''}`}>
        {/* ── Desktop Sidebar ─────────────────────────────────── */}
        <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
          <div className="sidebar-brand" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            <div className="brand-icon">🌿</div>
            {!isCollapsed && (
              <div className="brand-text">
                <h1>nanoFarms</h1>
                <span>AI Agriculture</span>
              </div>
            )}
          </div>

          <button 
            className="sidebar-toggle" 
            onClick={() => setIsCollapsed(!isCollapsed)}
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? '»' : '«'}
          </button>

          {!isCollapsed && <p className="nav-section-label" style={{ marginBottom: '10px' }}>Navigation</p>}

          <nav className="nav-links">
            {NAV_ITEMS.map(item => (
              <NavLink
                key={item.id}
                to={item.path}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                id={`nav-${item.id}`}
                title={isCollapsed ? item.label : ''}
              >
                <div className="nav-icon-wrap">{item.icon}</div>
                {!isCollapsed && <span className="nav-label-text">{item.label}</span>}
                {!isCollapsed && item.badge && <span className="nav-badge">{item.badge}</span>}
              </NavLink>
            ))}
          </nav>

          <div className="sidebar-footer">
            <div className={`ai-badge ${isCollapsed ? 'mini' : ''}`}>
              <div className="ai-badge-dot" />
              {!isCollapsed && (
                <div className="ai-badge-text">
                  <strong>Models Online</strong>
                  MobileNetV3 • AI Vision
                </div>
              )}
            </div>
          </div>
        </aside>

        {/* ── Mobile Header ───────────────────────────────────── */}
        <div className="mobile-header">
          <div className="mobile-header-brand" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            <div className="brand-icon">🌿</div>
            <h1>nanoFarms</h1>
          </div>
        </div>

        {/* ── Main Content ────────────────────────────────────── */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage onNavigate={goTo} />} />
            <Route path="/disease" element={<DiseaseDetection detectDisease={detectDisease} />} />
            <Route path="/soil" element={<SoilPrediction predictCrop={predictCrop} />} />
            <Route path="/chat" element={<AIExpertChat sendChat={sendChat} />} />
          </Routes>
        </main>

        {/* ── Mobile Bottom Nav ─────────────────────────────────── */}
        <nav className="mobile-nav">
          {NAV_ITEMS.map(item => (
            <NavLink
              key={item.id}
              to={item.path}
              className={({ isActive }) => `mobile-nav-item ${isActive ? 'active' : ''}`}
            >
              <div className="nav-icon-wrap">{item.icon}</div>
              <span className="mobile-nav-label">{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </>
  );
}

export default App;
