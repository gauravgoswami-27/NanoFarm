import torch
import torch.nn as nn
from torchvision.models import mobilenet_v3_small
import torchvision.transforms as transforms
from PIL import Image
import io
import os

# ─────────────────────────────────────────────────────────────────────────────
# Model Architecture  (mirrors ml_models/disease_vision/model.py)
# ─────────────────────────────────────────────────────────────────────────────
class DiseaseClassificationModel(nn.Module):
    def __init__(self, num_classes: int):
        super().__init__()
        self.base_model = mobilenet_v3_small(weights=None)
        in_features = self.base_model.classifier[-1].in_features
        self.base_model.classifier[-1] = nn.Linear(in_features, num_classes)

    def forward(self, x):
        return self.base_model(x)


# ─────────────────────────────────────────────────────────────────────────────
# Confidence threshold for AI fallback
# If the local MobileNetV3 is less than X% sure, we escalate to Cloud AI.
# ─────────────────────────────────────────────────────────────────────────────
LOW_CONFIDENCE_THRESHOLD = 60.0   # percent


class DiseaseInferenceService:
    def __init__(self):
        # Best available hardware
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        print(f"Disease Inference Service initialised on: {self.device}")

        # Paths — relative to this file so they work regardless of CWD
        _here = os.path.dirname(__file__)
        self.classes_path = os.path.join(_here, "..", "models", "classes.txt")
        self.model_path   = os.path.join(_here, "..", "models", "best_model.pth")

        self.class_names: list[str] = []
        self.model = None

        # Soft-fail so the server still boots even when the model isn't trained yet
        try:
            self._load_model()
        except Exception as e:
            print(
                f"⚠️  WARNING: Model not loaded. "
                f"Copy best_model.pth + classes.txt into backend/models/. Error: {e}"
            )

    # ── Private helpers ────────────────────────────────────────────────────────

    def _load_model(self):
        with open(self.classes_path) as f:
            self.class_names = [l.strip() for l in f if l.strip()]

        self.model = DiseaseClassificationModel(num_classes=len(self.class_names))
        state = torch.load(self.model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state)
        self.model.to(self.device)
        self.model.eval()

        # MUST match the transforms used in training
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])
        print(f"✅ Loaded model with {len(self.class_names)} classes.")

    # ── Public API ─────────────────────────────────────────────────────────────

    def predict(self, image_bytes: bytes) -> dict:
        """
        Run local MobileNetV3 inference.

        Returns
        -------
        {
            "disease":    str,   # predicted class name
            "confidence": float, # top-1 confidence in %
            "needs_fallback": bool # True when confidence < LOW_CONFIDENCE_THRESHOLD
        }
        """
        if self.model is None:
            raise RuntimeError(
                "Model not loaded. Place best_model.pth + classes.txt in backend/models/."
            )

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)
            probs  = torch.nn.functional.softmax(logits[0], dim=0)
            top_prob, top_idx = torch.topk(probs, 3)

        disease    = self.class_names[top_idx[0].item()]
        confidence = top_prob[0].item() * 100

        return {
            "disease":      disease,
            "confidence":   round(confidence, 2),
            "needs_fallback": confidence < LOW_CONFIDENCE_THRESHOLD,
            # Top-3 predictions for richer context if AI is called
            "top3": [
                {
                    "label":      self.class_names[top_idx[i].item()],
                    "confidence": round(top_prob[i].item() * 100, 2),
                }
                for i in range(top_prob.size(0))
            ],
        }


# Singleton — stays in GPU/CPU memory for the whole server lifetime
disease_service = DiseaseInferenceService()
