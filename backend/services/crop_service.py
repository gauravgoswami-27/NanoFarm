import joblib
import pandas as pd
import os

class CropRecommendationService:
    def __init__(self):
        _here = os.path.dirname(__file__)
        self.model_path = os.path.join(_here, "..", "models", "rf_crop_model.pkl")
        self.model = None
        
        try:
            self._load_model()
        except Exception as e:
            print(f"⚠️  WARNING: Crop Recommendation model not loaded: {e}")

    def _load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            print(f"✅ Loaded Crop Recommendation model (Random Forest).")
        else:
            raise FileNotFoundError(f"Model file not found at {self.model_path}")

    def predict(self, n: float, p: float, k: float, temp: float, humidity: float, ph: float, rainfall: float) -> dict:
        if self.model is None:
            raise RuntimeError("Crop Recommendation model is not loaded.")

        # Prepare input exactly as training (N, P, K, temperature, humidity, ph, rainfall)
        input_df = pd.DataFrame(
            [[n, p, k, temp, humidity, ph, rainfall]],
            columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        )

        prediction = self.model.predict(input_df)[0]
        probabilities = self.model.predict_proba(input_df)[0]
        
        # Get top 3
        classes = self.model.classes_
        top_indices = probabilities.argsort()[-3:][::-1]
        
        top_3 = [
            {"label": classes[idx], "confidence": round(float(probabilities[idx] * 100), 1)}
            for idx in top_indices
        ]

        return {
            "recommended_crop": prediction,
            "confidence_score": round(float(probabilities[top_indices[0]] * 100), 1),
            "top_3": top_3
        }

# Singleton instance
crop_service = CropRecommendationService()
