from fastapi import APIRouter, UploadFile, File, HTTPException
from services.disease_service import disease_service

router = APIRouter()

@router.post("/predict-disease")
async def predict_disease(file: UploadFile = File(...)):
    """
    Receives an uploaded leaf image from the frontend and returns the predicted disease.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
        
    try:
        # Read the file uploaded from the user
        contents = await file.read()
        
        # Pass raw image bytes directly to our PyTorch service in memory
        result = disease_service.predict(contents)
        
        return {
            "success": True,
            "prediction": result["disease"],
            "confidence": result["confidence"],
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
