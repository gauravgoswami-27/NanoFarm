import joblib
import pandas as pd
import argparse

def predict_crop(n, p, k, temp, humidity, ph, rainfall, model_path="rf_crop_model.pkl"):
    try:
        model = joblib.load(model_path)
    except FileNotFoundError:
        print(f"Error: Model not found at {model_path}. Please run train_rf.py first.")
        return
        
    # The model expects a 2D array / DataFrame with the exact feature names
    input_data = pd.DataFrame([[n, p, k, temp, humidity, ph, rainfall]], 
                              columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
    
    # Optional: You can also extract probabilities using predict_proba if you want to show "Top 3 choices"
    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]
    
    # Get top 3 predictions
    top_indices = probabilities.argsort()[-3:][::-1]
    classes = model.classes_
    
    print("\n--- Crop Recommendation Results ---")
    print(f"Absolute Best Match: {prediction.upper()}\n")
    print("Top 3 Candidates:")
    for idx in top_indices:
        print(f"- {classes[idx]}: {probabilities[idx] * 100:.1f}% Match")
        
    return prediction

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict best crop based on soil/weather")
    parser.add_argument("--n", type=float, required=True, help="Nitrogen ratio")
    parser.add_argument("--p", type=float, required=True, help="Phosphorous ratio")
    parser.add_argument("--k", type=float, required=True, help="Potassium ratio")
    parser.add_argument("--temp", type=float, required=True, help="Temperature in Celsius")
    parser.add_argument("--humidity", type=float, required=True, help="Humidity percentage")
    parser.add_argument("--ph", type=float, required=True, help="Soil pH (0-14)")
    parser.add_argument("--rain", type=float, required=True, help="Rainfall in mm")
    parser.add_argument("--model", type=str, default="rf_crop_model.pkl", help="Path to trained model")
    
    args = parser.parse_args()
    predict_crop(args.n, args.p, args.k, args.temp, args.humidity, args.ph, args.rain, model_path=args.model)
