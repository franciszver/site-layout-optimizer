from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to Python path
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import handlers
# Check if GDAL is available before importing upload handler
try:
    from utils.kml_parser import GDAL_AVAILABLE
    if not GDAL_AVAILABLE:
        raise ImportError("GDAL not available")
    from handlers.upload import router as upload_router
    print("Using full upload handler with GDAL support.")
except (ImportError, ModuleNotFoundError):
    # Fallback to mock upload if GDAL not available
    try:
        from handlers.upload_mock import router as upload_router
        print("Note: Using mock upload handler. Install GDAL for full KMZ/KML support.")
    except (ImportError, ModuleNotFoundError) as e:
        print(f"Error importing upload handlers: {e}")
        # Create a minimal router as last resort
        from fastapi import APIRouter
        upload_router = APIRouter()
        @upload_router.post("/upload")
        async def mock_upload():
            return {"message": "Upload handler not available"}

from handlers.analyze import router as analyze_router
from handlers.optimize import router as optimize_router
from handlers.generate_roads import router as roads_router
from handlers.calculate_cutfill import router as cutfill_router
from handlers.export import router as export_router
from handlers.constraints import router as constraints_router

load_dotenv()

app = FastAPI(
    title="Site Layout Optimizer API",
    description="AI-powered geospatial site layout optimization for real estate due diligence",
    version="0.1.0"
)

# CORS middleware
# Get allowed origins from environment or use defaults
allowed_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
]

# Filter out empty strings
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.amplifyapp\.com|https://.*\.awsapprunner\.com",  # Amplify and App Runner patterns
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    from middleware.rate_limit import check_rate_limit
    if not check_rate_limit(request):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Please wait before making another request.",
                "error": "rate_limit_exceeded"
            }
        )
    response = await call_next(request)
    return response

# Include routers
app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(analyze_router, prefix="/api", tags=["analyze"])
app.include_router(optimize_router, prefix="/api", tags=["optimize"])
app.include_router(roads_router, prefix="/api", tags=["roads"])
app.include_router(cutfill_router, prefix="/api", tags=["cutfill"])
app.include_router(export_router, prefix="/api", tags=["export"])
app.include_router(constraints_router, prefix="/api", tags=["constraints"])

@app.get("/")
async def root():
    return {"message": "Site Layout Optimizer API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

