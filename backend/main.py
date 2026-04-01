from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import disease_router, crop_router, chat_router

app = FastAPI(
    title="nanoFarms API",
    description="Backend API for the nanoFarms AI Agricultural App",
    version="1.0.0"
)

# Configure CORS to allow your React Vite frontend to talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our ML routers
app.include_router(disease_router.router, prefix="/api", tags=["Disease Detection"])
app.include_router(crop_router.router, prefix="/api", tags=["Crop Recommendation"])
app.include_router(chat_router.router, prefix="/api", tags=["AI Agronomist Chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the NanoFarm API. Go to /docs for Swagger UI API Documentation."}
