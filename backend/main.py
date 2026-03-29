from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import disease_router

app = FastAPI(
    title="NanoFarm API",
    description="Backend API for the Neural Farms Edge AI Agricultural App",
    version="1.0.0"
)

# Configure CORS to allow your React Vite frontend to talk to the API
# In production, change "*" to your actual deployed frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our ML routers
app.include_router(disease_router.router, prefix="/api", tags=["Machine Learning"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the NanoFarm API. Go to /docs for Swagger UI API Documentation."}
