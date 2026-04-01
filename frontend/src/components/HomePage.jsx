function HomePage({ onNavigate }) {
  return (
    <div className="homepage">
      {/* ── Hero ────────────────────────────────────────────── */}
      <section className="hero">
        <div className="hero-text">
          <div className="hero-eyebrow">
            <span className="hero-eyebrow-dot" />
            AI-Powered Agriculture
          </div>

          <h1>
            Smart Farming
            <br />
            Starts with <span className="gradient-text">AI Insight</span>
          </h1>

          <p className="hero-subtitle">
            nanoFarms combines deep learning and vision AI to detect
            crop diseases, recommend the best crops for your soil, and give you
            expert agronomist advice — instantly, offline-first.
          </p>

          <div className="hero-cta-group">
            <button className="btn-primary" onClick={() => onNavigate('/disease')} id="hero-cta-disease">
              <span>🔬</span>
              Diagnose a Crop
            </button>
            <button className="btn-secondary" onClick={() => onNavigate('/chat')} id="hero-cta-chat">
              <span>💬</span>
              Ask AI Agronomist
            </button>
          </div>
        </div>

        {/* Live Demo Card */}
        <div className="hero-visual">
          <div className="hero-card-stack">
            <div className="hero-card hero-card-back2" />
            <div className="hero-card hero-card-back1" />
            <div className="hero-card hero-card-main">
              <div className="hero-card-label">Live Diagnosis</div>
              <div className="hero-card-disease">🌾 Wheat Leaf Rust</div>
              <div className="hero-card-conf" style={{ visibility: 'hidden' }}>
                <span style={{ color: '#22a05a', fontWeight: 700 }}>●</span>
                AI Processing
              </div>

              <div className="hero-card-progress-fill-wrap">
                <div className="hero-card-progress">
                  <div
                    className="hero-card-progress-fill"
                    style={{ width: '94%' }}
                  />
                </div>
              </div>

              <div style={{ marginTop: '14px' }}>
                <div className="hero-card-label" style={{ marginBottom: '8px' }}>AI Treatment Plan</div>
                {[
                  'Apply fungicide (propiconazole)',
                  'Remove and burn infected leaves',
                  'Improve field drainage',
                ].map((step, i) => (
                  <div key={i} className="hero-card-step">
                    <span className="step-num">{i + 1}</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats ────────────────────────────────────────────── */}
      <section className="stats-bar">
        {[
          { number: '9+',    label: 'Crop Disease Classes' },
          { number: '4',     label: 'Datasets Merged' },
          { number: '∞',     label: 'AI Fallback' },
        ].map((s, i) => (
          <div className="stat-item" key={i}>
            <div className="stat-number">{s.number}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </section>

      {/* ── Features Grid ─────────────────────────────────────── */}
      <section className="features-section">
        <div className="section-header">
          <h2>Everything your farm needs</h2>
          <p>Three AI tools, one seamless platform</p>
        </div>

        <div className="features-grid">
          <button
            className="feature-card"
            onClick={() => onNavigate('/disease')}
            id="feature-disease"
          >
            <div
              className="feature-icon-wrap"
              style={{ background: '#fee2e2' }}
            >
              🔬
            </div>
            <h3>Disease Detection</h3>
            <p>
              Upload a leaf photo. Our offline MobileNetV3 model instantly
              identifies wheat rust, cotton disease, rice blight, and more.
              Low-confidence cases escalate to Vision AI automatically.
            </p>
            <div className="feature-arrow">
              Diagnose now <span>→</span>
            </div>
          </button>

          <button
            className="feature-card"
            onClick={() => onNavigate('/soil')}
            id="feature-soil"
          >
            <div
              className="feature-icon-wrap"
              style={{ background: '#dcfce7' }}
            >
              🌱
            </div>
            <h3>Crop Recommendation</h3>
            <p>
              Enter your soil's NPK, temperature, humidity and pH. Our AI
              recommends the most suitable crop with a confidence score to
              maximize your yield.
            </p>
            <div className="feature-arrow">
              Predict crop <span>→</span>
            </div>
          </button>

          <button
            className="feature-card"
            onClick={() => onNavigate('/chat')}
            id="feature-chat"
          >
            <div
              className="feature-icon-wrap"
              style={{ background: '#dbeafe' }}
            >
              💬
            </div>
            <h3>AI Agronomist Chat</h3>
            <p>
              Ask any farming question in natural language. Get expert advice on
              planting schedules, pest control, irrigation, and sustainable
              farming practices.
            </p>
            <div className="feature-arrow">
              Start chatting <span>→</span>
            </div>
          </button>
        </div>
      </section>

      {/* ── How It Works ─────────────────────────────────────── */}
      <section className="features-section" style={{ paddingTop: 0 }}>
        <div className="section-header">
          <h2>How it works</h2>
          <p>From field to insight in seconds</p>
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          {[
            {
              step: '01',
              icon: '📸',
              title: 'Capture',
              desc: 'Take or upload a photo of your crop leaf from any device.',
            },
            {
              step: '02',
              icon: '🧠',
              title: 'AI Analyzes',
              desc: 'Our offline PyTorch model runs instantly. Vision AI steps in for edge cases.',
            },
            {
              step: '03',
              icon: '💊',
              title: 'Get Treatment',
              desc: 'Receive a 3-step organic treatment plan tailored to your crop and condition.',
            },
          ].map((item, i) => (
            <div
              key={i}
              style={{
                flex: 1,
                background: 'white',
                borderRadius: '20px',
                padding: '1.75rem',
                border: '1px solid var(--border)',
                boxShadow: 'var(--shadow-sm)',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  top: '12px',
                  right: '16px',
                  fontSize: '3rem',
                  fontWeight: 900,
                  color: 'var(--green-100)',
                  letterSpacing: '-2px',
                  lineHeight: 1,
                }}
              >
                {item.step}
              </div>
              <div style={{ fontSize: '2rem', marginBottom: '12px' }}>{item.icon}</div>
              <h3 style={{ fontWeight: 800, color: 'var(--green-900)', marginBottom: '8px', fontSize: '1.1rem' }}>
                {item.title}
              </h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default HomePage;
