import { useState } from 'react';

const FIELDS = [
  { name: 'N', label: 'Nitrogen (N)', placeholder: 'e.g. 90', step: '1', hint: 'kg/ha' },
  { name: 'P', label: 'Phosphorus (P)', placeholder: 'e.g. 42', step: '1', hint: 'kg/ha' },
  { name: 'K', label: 'Potassium (K)', placeholder: 'e.g. 43', step: '1', hint: 'kg/ha' },
  { name: 'temperature', label: 'Temperature', placeholder: 'e.g. 20.8', step: '0.1', hint: '°C' },
  { name: 'humidity', label: 'Humidity', placeholder: 'e.g. 82.0', step: '0.1', hint: '%' },
  { name: 'ph', label: 'pH Level', placeholder: 'e.g. 6.5', step: '0.1', hint: '0 – 14' },
];

const INITIAL = { N: '', P: '', K: '', temperature: '', humidity: '', ph: '', rainfall: '' };

function SoilPrediction({ predictCrop }) {
  const [form,    setForm]    = useState(INITIAL);
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState(null);
  const [error,   setError]   = useState(null);

  const handleChange = (e) =>
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await predictCrop({
        soil: true,
        N: Number(form.N),
        P: Number(form.P),
        K: Number(form.K),
        temperature: Number(form.temperature),
        humidity: Number(form.humidity),
        ph: Number(form.ph),
        rainfall: Number(form.rainfall),
        message: `Act as an expert agronomist. Based on soil data: N=${form.N}, P=${form.P}, K=${form.K}, Temp=${form.temperature}°C, Humidity=${form.humidity}%, pH=${form.ph}, Rainfall=${form.rainfall}mm — recommend the best crop. Reply strictly with JSON: {"recommended_crop": string, "confidence_score": number 0-1}.`,
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const d = result?.data ?? {};
  const conf = d.confidence_score != null ? Math.round(d.confidence_score * 100) : null;

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div className="page-header-top">
          <div className="page-icon" style={{ background: '#dcfce7' }}>🌱</div>
          <h2>Crop Recommendation</h2>
        </div>
        <p>
          Enter your soil parameters and environmental conditions.
          Our AI will recommend the best crop to maximize your yield.
        </p>
      </div>

      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            {FIELDS.map(f => (
              <div className="input-group" key={f.name}>
                <label htmlFor={`soil-${f.name}`}>
                  {f.label}
                  <span style={{ marginLeft: 6, fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                    ({f.hint})
                  </span>
                </label>
                <input
                  id={`soil-${f.name}`}
                  type="number"
                  name={f.name}
                  placeholder={f.placeholder}
                  step={f.step}
                  required
                  value={form[f.name]}
                  onChange={handleChange}
                />
              </div>
            ))}

            <div className="input-group full-width">
              <label htmlFor="soil-rainfall">
                Rainfall
                <span style={{ marginLeft: 6, fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>(mm)</span>
              </label>
              <input
                id="soil-rainfall"
                type="number"
                name="rainfall"
                placeholder="e.g. 202.9"
                step="0.1"
                required
                value={form.rainfall}
                onChange={handleChange}
              />
            </div>
          </div>

          <button type="submit" className="submit-btn" disabled={loading} id="predict-crop-btn">
            {loading ? (
              <>
                <div className="loading-spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
                Predicting…
              </>
            ) : (
              <>🌱 Predict Best Crop</>
            )}
          </button>
        </form>

        {/* Error */}
        {error && (
          <div className="error-banner">
            <span className="error-banner-icon">⚠️</span>
            <div className="error-banner-body">
              <div className="error-banner-title">Prediction Failed</div>
              <div className="error-banner-msg">{error}</div>
            </div>
            <button className="error-banner-close" onClick={() => setError(null)}>×</button>
          </div>
        )}
      </div>

      {/* ── Inline Results ─────────────────────── */}
      {result && (
        <div className="result-section">
          <div className="result-header-bar">
            <h3>🌾 Recommendation</h3>
            <button
              className="result-clear-btn"
              onClick={() => { setResult(null); setForm(INITIAL); }}
            >
              ✕ Clear
            </button>
          </div>

          <div className="result-card">
            <div className="result-card-header" style={{ border: 'none' }}>
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--text-muted)', marginBottom: 8 }}>
                  Recommended Crop
                </div>
                <div className="result-crop-name">
                  🌾 {d.recommended_crop || 'Unknown'}
                </div>

              </div>

              <span className="result-pill success">
                <span className="result-pill-dot" />
                Expert Recommendation
              </span>
            </div>

            {/* Soil Summary */}
            <div
              style={{
                padding: '1rem 1.5rem',
                background: 'var(--surface-2)',
                borderTop: '1px solid var(--border)',
              }}
            >
              <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--text-muted)', marginBottom: 10 }}>
                Your Soil Data
              </div>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(4, 1fr)',
                  gap: '10px',
                }}
              >
                {[
                  { label: 'N', value: form.N, unit: 'kg/ha' },
                  { label: 'P', value: form.P, unit: 'kg/ha' },
                  { label: 'K', value: form.K, unit: 'kg/ha' },
                  { label: 'Temp', value: form.temperature, unit: '°C' },
                  { label: 'Humidity', value: form.humidity, unit: '%' },
                  { label: 'pH', value: form.ph, unit: '' },
                  { label: 'Rainfall', value: form.rainfall, unit: 'mm' },
                ].map((item, i) => (
                  <div
                    key={i}
                    style={{
                      background: 'white',
                      borderRadius: '10px',
                      padding: '10px 12px',
                      border: '1px solid var(--border)',
                      textAlign: 'center',
                    }}
                  >
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, marginBottom: 4 }}>{item.label}</div>
                    <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--green-700)' }}>
                      {item.value}{item.unit ? <span style={{ fontSize: '0.7rem', fontWeight: 500, color: 'var(--text-muted)' }}>{item.unit}</span> : null}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SoilPrediction;
