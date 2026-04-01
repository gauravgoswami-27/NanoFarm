import { useState, useRef } from 'react';

// Simple markdown parser for bold, lists, and newlines
function parseMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^Step (\d+): (.+)$/gm, '<div class="treatment-step"><span class="step-badge">$1</span> $2</div>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/\n/g, '<br/>');
}

function DiseaseDetection({ detectDisease }) {
  const [file, setFile]         = useState(null);
  const [preview, setPreview]   = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState(null);
  const [error, setError]       = useState(null);
  const fileInputRef = useRef(null);

  const acceptFile = (f) => {
    if (!f || !f.type.startsWith('image/')) {
      setError('Please upload a JPG, PNG, or WebP image file.');
      return;
    }
    setError(null);
    setResult(null);
    setFile(f);
    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result);
    reader.readAsDataURL(f);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) acceptFile(f);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const fd = new FormData();
      fd.append('file', file);
      const data = await detectDisease(fd);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const d = result?.data ?? {};
  const conf = d.confidence ?? 0;

  // Pick result pill variant
  const pillVariant =
    !result ? null
    : conf >= 80 ? 'success'
    : conf >= 55 ? 'warning'
    : 'info';

  const pillLabel =
    !result ? null
    : conf < 55 ? 'Cloud AI Diagnosis'
    : 'Identified';

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div className="page-header-top">
          <div className="page-icon" style={{ background: '#fee2e2' }}>🔬</div>
          <h2>Disease Detection</h2>
        </div>
        <p>
          Upload a leaf photo. Our offline AI instantly diagnoses diseases across
          wheat, cotton, rice, and more. Uncertain cases are escalated to Cloud AI.
        </p>
      </div>

      <div className="form-card">
        <form onSubmit={handleSubmit}>
          {/* Upload or Preview */}
          {!file ? (
            <div
              className={`upload-zone ${dragging ? 'drag-over' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              onClick={() => fileInputRef.current?.click()}
              id="upload-zone"
            >
              <span className="upload-zone-icon">🌿</span>
              <h3>Drop your leaf image here</h3>
              <p>Supports JPG, PNG, WebP</p>
              <label className="upload-btn-inline" onClick={(e) => e.stopPropagation()}>
                📂 Browse Files
                <input
                  type="file"
                  accept="image/*"
                  ref={fileInputRef}
                  style={{ display: 'none' }}
                  onChange={(e) => { if (e.target.files[0]) acceptFile(e.target.files[0]); }}
                />
              </label>
            </div>
          ) : (
            <div className="preview-container" style={{ marginBottom: '1.5rem' }}>
              <div className="preview-header">
                <span className="preview-filename">📎 {file.name}</span>
                <button type="button" className="preview-change-btn" onClick={reset}>
                  ✕ Remove
                </button>
              </div>
              <img src={preview} alt="Leaf preview" className="preview-image" />
            </div>
          )}

          <button
            type="submit"
            className="submit-btn"
            disabled={!file || loading}
            id="analyze-btn"
          >
            {loading ? (
              <>
                <div className="loading-spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
                Analyzing…
              </>
            ) : (
              <>🔬 Analyze Leaf</>
            )}
          </button>
        </form>

        {/* Error */}
        {error && (
          <div className="error-banner" style={{ marginTop: '1rem' }}>
            <span className="error-banner-icon">⚠️</span>
            <div className="error-banner-body">
              <div className="error-banner-title">Analysis Failed</div>
              <div className="error-banner-msg">{error}</div>
            </div>
            <button className="error-banner-close" onClick={() => setError(null)}>×</button>
          </div>
        )}
      </div>

      {/* ── Inline Results ───────────────────────────── */}
      {result && (
        <div className="result-section">
          <div className="result-header-bar">
            <h3>📊 Analysis Results</h3>
            <button className="result-clear-btn" onClick={reset}>✕ Start over</button>
          </div>

          <div className="result-grid">
            {/* Disease / Condition Card */}
            <div className="result-card">
              <div className="result-card-header">
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--text-muted)', marginBottom: 8 }}>
                    Detected Condition
                  </div>
                  <div className="result-disease-name">
                    {d.disease_name || 'Unknown'}
                  </div>

                  {/* Confidence Bar */}
                  <div className="result-conf-bar-wrap">
                    <div className="result-conf-label">
                      <span>Confidence</span>
                      <span style={{ color: 'var(--green-600)', fontWeight: 800 }}>{conf}%</span>
                    </div>
                    <div className="result-conf-bar">
                      <div className="result-conf-fill" style={{ width: `${conf}%` }} />
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 6, align: 'flex-end' }}>
                  {pillVariant && (
                    <span className={`result-pill ${pillVariant}`}>
                      <span className="result-pill-dot" />
                      {pillLabel}
                    </span>
                  )}
                  {d.gemini_used && (
                    <span className="ai-badge-inline">✨ AI Analysis</span>
                  )}
                </div>
              </div>

              {/* Top-3 predictions */}
              {d.top_3?.length > 0 && (
                <div className="result-top3">
                  {d.top_3.map((p, i) => (
                    <div className="top3-item" key={i}>
                      <div className="top3-label">#{i + 1} Guess</div>
                      <div className="top3-name">{p.label}</div>
                      <div className="top3-bar">
                        <div className="top3-bar-fill" style={{ width: `${p.confidence}%` }} />
                      </div>
                      <div className="top3-pct">{p.confidence}%</div>
                    </div>
                  ))}
                </div>
              )}

              {/* Treatment */}
              {d.treatment && (
                <div className="result-treatment">
                  <div className="result-treatment-label">
                    💊 Recommended Treatment
                  </div>
                  <div 
                    className="result-treatment-text"
                    dangerouslySetInnerHTML={{ __html: parseMarkdown(d.treatment) }}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DiseaseDetection;
