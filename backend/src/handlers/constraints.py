"""
Regulatory constraints handler
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Tuple, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.regulatory_fetcher import RegulatoryFetcher

router = APIRouter()


class ConstraintsRequest(BaseModel):
    bounds: Tuple[float, float, float, float]
    property_location: Optional[Tuple[float, float]] = None


@router.post("/constraints")
async def get_constraints(request: ConstraintsRequest):
    """
    Fetch regulatory constraints for property location
    
    Returns:
        Constraint data for visualization
    """
    try:
        fetcher = RegulatoryFetcher()
        
        regulatory_data = fetcher.fetch_all_regulatory_data(
            bounds=request.bounds,
            property_location=request.property_location
        )
        
        return JSONResponse(content={
            'flood_zones': regulatory_data.get('flood_zones', {}),
            'wetlands': regulatory_data.get('wetlands', {}),
            'topographic': regulatory_data.get('topographic', {}),
            'bounds': request.bounds,
            'message': 'Regulatory constraints fetched successfully'
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching constraints: {str(e)}")

