import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import argparse
import os

def train_crop_model(data_path: str, save_path: str = "rf_crop_model.pkl", output_dir: str = "."):
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Please download the Kaggle Crop Recommendation dataset.")
        
    print(f"Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    
    # Standard Kaggle dataset columns: N, P, K, temperature, humidity, ph, rainfall, label
    expected_features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    
    # Verify dataset structure
    for col in expected_features:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}. Ensure you are using the correct Kaggle dataset.")
            
    # 1. Prepare Data
    X = df[expected_features]
    y = df['label'] # The target crop name
    
    # 2. Train-Test Split (80% training, 20% validation)
    print("Splitting data into 80% train and 20% test...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 3. Initialize & Train the Random Forest
    # 100 trees is a good balance between speed, size, and accuracy
    print("Training Random Forest Classifier (100 estimators)...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    
    # 4. Evaluate the Model
    print("\n--- Model Evaluation ---")
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Overall Accuracy: {acc * 100:.2f}%")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # 5. Export Model for the FastAPI Backend
    full_save_path = os.path.join(output_dir, save_path)
    joblib.dump(clf, full_save_path)
    print(f"\nModel strictly saved to: {full_save_path} (Size: ~{os.path.getsize(full_save_path) / 1024:.2f} KB)")
    
    # 6. Generate Feature Importance Graph for the Research Paper
    try:
        plot_feature_importance(clf, expected_features, output_dir)
    except Exception as e:
        print(f"Could not generate feature importance graph: {e}")

def plot_feature_importance(model, feature_names, output_dir):
    """Generates a bar chart showing which soil/weather metrics matter the most."""
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    sorted_features = [feature_names[i] for i in indices]
    sorted_importances = importances[indices]
    
    plt.figure(figsize=(10, 6))
    plt.title("Random Forest Feature Importance for Crop Recommendation")
    plt.bar(range(len(importances)), sorted_importances, align="center", color="skyblue")
    plt.xticks(range(len(importances)), sorted_features, rotation=45)
    plt.xlim([-1, len(importances)])
    plt.ylabel("Importance Metric")
    plt.xlabel("Environmental Features")
    plt.tight_layout()
    
    graph_path = os.path.join(output_dir, "feature_importance.png")
    plt.savefig(graph_path)
    print(f"-> Research Graph saved to: {graph_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Random Forest Crop Recommendation Model")
    parser.add_argument("--data", type=str, default="Crop_recommendation.csv", help="Path to the CSV dataset")
    parser.add_argument("--output", type=str, default=".", help="Directory to save the .pkl and graphs")
    
    args = parser.parse_args()
    train_crop_model(args.data, output_dir=args.output)
