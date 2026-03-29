from fastapi import APIRouter, UploadFile, File, HTTPException
from services.disease_service import disease_service

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

router = APIRouter()

@router.post("/predict-disease")
async def predict_disease(file: UploadFile = File(...)):
    """
    Receives an uploaded leaf image from the frontend, uses PyTorch offline, 
    and then pings Gemini natively for a contextual treatment plan.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
        
    try:
        # 1. Read the file and pass raw image bytes directly to PyTorch
        contents = await file.read()
        result = disease_service.predict(contents)
        
        disease = result["disease"]
        conf = result["confidence"]
        
        # 2. Ping Gemini Natively in Python
        treatment_plan = "AI Error - Gemini Failed. Please consult agronomist."
        try:
            if API_KEY:
                model = genai.GenerativeModel("gemini-2.5-flash")
                prompt = f"""Act as an expert agronomist. Our PyTorch AI detected '{disease}' with {conf}% confidence. 
                Write a concise 3-step action plan using local organic treatments. Keep it brief and highly practical."""
                
                response = model.generate_content(prompt)
                treatment_plan = response.text
            else:
                treatment_plan = f"PyTorch Offline Analysis - Confidence: {conf}%. Gemini API key missing."
        except Exception as e:
            print(f"Gemini API Error: {e}")
            treatment_plan = f"PyTorch Offline Analysis - Confidence: {conf}%. Gemini API Error."
            
        # 3. Return the exact JSON structure React expects
        return {
            "status": "success",
            "type": "disease_detection",
            "data": {
                "disease_name": disease,
                "treatment": treatment_plan
            }
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
