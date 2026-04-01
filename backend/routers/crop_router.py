from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.crop_service import crop_service

router = APIRouter()

class CropRequest(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

@router.post("/predict-crop")
async def predict_crop(req: CropRequest):
    try:
        result = crop_service.predict(
            n=req.N,
            p=req.P,
            k=req.K,
            temp=req.temperature,
            humidity=req.humidity,
            ph=req.ph,
            rainfall=req.rainfall
        )
        return {
            "status": "success",
            "type": "crop_prediction",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
