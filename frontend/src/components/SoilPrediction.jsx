import { useState } from 'react';

function SoilPrediction({ executeWebhook }) {
  const [formData, setFormData] = useState({
    N: '', P: '', K: '', temperature: '', humidity: '', ph: '', rainfall: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      soil: true,
      N: Number(formData.N),
      P: Number(formData.P),
      K: Number(formData.K),
      temperature: Number(formData.temperature),
      humidity: Number(formData.humidity),
      ph: Number(formData.ph),
      rainfall: Number(formData.rainfall),
      message: `Act as an expert agronomist. Based on this soil data: Nitrogen=${formData.N}, Phosphorus=${formData.P}, Potassium=${formData.K}, Temperature=${formData.temperature}°C, Humidity=${formData.humidity}%, pH=${formData.ph}, Rainfall=${formData.rainfall}mm, recommend the best crop to plant. Reply strictly with JSON containing "recommended_crop" (string) and "confidence_score" (number 0.0-1.0).`
    };
    await executeWebhook(payload, false);
  };

  return (
    <div className="tab-content">
      <h2>Soil Analysis & Crop Prediction</h2>
      <p className="tab-description">Enter your soil and environmental parameters to get AI-recommended crops.</p>
      
      <form onSubmit={handleSubmit} className="dynamic-form">
        <div className="form-grid">
          <div className="input-group">
            <label>Nitrogen (N)</label>
            <input type="number" name="N" required placeholder="e.g., 90" value={formData.N} onChange={handleChange} />
          </div>
          <div className="input-group">
            <label>Phosphorus (P)</label>
            <input type="number" name="P" required placeholder="e.g., 42" value={formData.P} onChange={handleChange} />
          </div>
          <div className="input-group">
            <label>Potassium (K)</label>
            <input type="number" name="K" required placeholder="e.g., 43" value={formData.K} onChange={handleChange} />
          </div>
          <div className="input-group">
            <label>Temperature (°C)</label>
            <input type="number" step="0.1" name="temperature" required placeholder="e.g., 20.8" value={formData.temperature} onChange={handleChange} />
          </div>
          <div className="input-group">
            <label>Humidity (%)</label>
            <input type="number" step="0.1" name="humidity" required placeholder="e.g., 82.0" value={formData.humidity} onChange={handleChange} />
          </div>
          <div className="input-group">
            <label>pH Level</label>
            <input type="number" step="0.1" name="ph" required placeholder="e.g., 6.5" value={formData.ph} onChange={handleChange} />
          </div>
          <div className="input-group full-width">
            <label>Rainfall (mm)</label>
            <input type="number" step="0.1" name="rainfall" required placeholder="e.g., 202.9" value={formData.rainfall} onChange={handleChange} />
          </div>
        </div>
        <button type="submit" className="submit-btn">Predict Crop</button>
      </form>
    </div>
  );
}

export default SoilPrediction;
