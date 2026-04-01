"""
disease_router.py (Consolidated Groq Migration)
-----------------
Pipeline:
  1. Upload leaf image → local MobileNetV3 (PyTorch, offline)
  2a. If confidence ≥ 60%:
        Groq (Llama 3.3)  →  treatment plan
  2b. If confidence < 60%:
        Groq Vision (Llama 3.2)  →  identify disease from image,
        then Groq (Llama 3.3)  →  generate treatment plan 
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from services.disease_service import disease_service
from services.chat_service import chat_service 

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
router = APIRouter()

# ─────────────────────────────────────────────────────────────────────────────
# Helper: Groq Vision (Identify disease)
# ─────────────────────────────────────────────────────────────────────────────
async def _groq_vision_identify(image_bytes: bytes, content_type: str) -> str:
    """
    Send the image to Groq Llama 3.2 Vision to identify the crop and disease.
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_key_here":
        return "Groq API Key not configured."
    
    # identify_disease_vision is implemented in GroqAIService
    return await chat_service.identify_disease_vision(image_bytes, content_type)

# ─────────────────────────────────────────────────────────────────────────────
# Helper: Groq Treatment Plan
# ─────────────────────────────────────────────────────────────────────────────
async def _generate_treatment_plan(disease: str, confidence: float = None) -> str:
    """
    Generate a 3-step action plan using Groq (Llama 3.3).
    """
    prompt = (
        f"Act as an expert agronomist. The user's crop has been diagnosed with '{disease}'.\n"
        f"{f'(Confidence: {confidence:.1f}%)' if confidence else ''}\n\n"
        "Provide a concise 3-step action plan using local organic treatments. "
        "Each step should be actionable and brief."
    )
    # get_chat_response is implemented in GroqAIService
    return await chat_service.get_chat_response(prompt)

# ─────────────────────────────────────────────────────────────────────────────
# Route
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/predict-disease")
async def predict_disease(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

    try:
        contents = await file.read()
        result   = disease_service.predict(contents)

        local_disease = result["disease"]
        confidence    = result["confidence"]
        needs_fallback = result["needs_fallback"] # Flag for AI fallback
        top3          = result["top3"]

        treatment_plan = None
        analysis_source = "PyTorch Local Model"
        final_disease   = local_disease

        # ── Consolidated Groq Fallback ────────────────────────────────
        if needs_fallback:
            analysis_source = "Groq Vision (AI Fallback)"
            final_disease = await _groq_vision_identify(contents, file.content_type)
            treatment_plan = await _generate_treatment_plan(final_disease)
        else:
            treatment_plan = await _generate_treatment_plan(local_disease, confidence)

        # ── Response ──────────────────────────────────────────────────
        return {
            "status": "success",
            "type":   "disease_detection",
            "data": {
                "disease_name":  final_disease,
                "confidence":    confidence,
                "source":        analysis_source,
                "top_3":         top3,
                "treatment":     treatment_plan,
            },
        }

    except Exception as e:
        print(f"❌ Disease Prediction Pipeline Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
