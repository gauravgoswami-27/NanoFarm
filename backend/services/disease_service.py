import torch
import torch.nn as nn
from torchvision.models import mobilenet_v3_small
import torchvision.transforms as transforms
from PIL import Image
import io
import os

# --- Model Architecture Definition ---
# We keep a copy in the backend so it runs independently on the production server
class DiseaseClassificationModel(nn.Module):
    def __init__(self, num_classes: int):
        super(DiseaseClassificationModel, self).__init__()
        self.base_model = mobilenet_v3_small(weights=None) # We load custom weights instead
        in_features = self.base_model.classifier[-1].in_features
        self.base_model.classifier[-1] = nn.Linear(in_features, num_classes)
        
    def forward(self, x):
        return self.base_model(x)

# --- Inference Logic ---
class DiseaseInferenceService:
    def __init__(self):
        # Determine the best available hardware
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self.device = torch.device('mps')
        else:
            self.device = torch.device('cpu')
            
        print(f"Disease Inference Service initialized on: {self.device}")
        
        # Load classes
        # In production, these paths should absolute or properly dynamic. 
        # For now, we assume the backend is run from the backend/ directory
        self.classes_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'classes.txt')
        self.model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'best_model.pth')
        
        self.class_names = []
        self.model = None
        
        # Try to load model immediately on server startup (Soft fail if not trained yet)
        try:
            self.load_model()
        except Exception as e:
            print(f"Warning: Model not loaded automatically. Please put best_model.pth in backend/models/. Error: {e}")

    def load_model(self):
        with open(self.classes_path, "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]
            
        self.model = DiseaseClassificationModel(num_classes=len(self.class_names))
        state_dict = torch.load(self.model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()
        
        # Exact same transforms used in train.py (CRITICAL for accuracy)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image_bytes: bytes):
        if self.model is None:
            raise RuntimeError("Model is not loaded. Ensure best_model.pth is in backend/models folder.")
            
        # Read image from raw bytes received via API
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            
            top_prob, top_catid = torch.topk(probabilities, 1)
            
        disease_name = self.class_names[top_catid[0].item()]
        confidence = top_prob[0].item() * 100
        
        return {
            "disease": disease_name,
            "confidence": round(confidence, 2)
        }

# Instantiate a global service so it stays in memory after the first API ping
disease_service = DiseaseInferenceService()
