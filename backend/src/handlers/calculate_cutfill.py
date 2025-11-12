"""
Cut/fill calculation handler
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.cutfill_calculator import CutFillCalculator
from shapely.geometry import Polygon
import numpy as np

router = APIRouter()


class CalculateCutFillRequest(BaseModel):
    dem: List[List[float]]  # 2D array
    bounds: Tuple[float, float, float, float]
    proposed_grades: Dict[str, Any]
    property_boundary: Optional[List[List[float]]] = None
    grid_resolution: float = 10.0


@router.post("/calculate-cutfill")
async def calculate_cutfill(request: CalculateCutFillRequest):
    """
    Calculate cut/fill volumes
    
    Returns:
        Volume reports and maps
    """
    try:
        # Convert DEM to numpy array
        dem = np.array(request.dem)
        
        # Convert property boundary if provided
        property_boundary = None
        if request.property_boundary:
            property_coords = request.property_boundary[0]
            property_boundary = Polygon(property_coords)
        
        # Calculate volumes
        calculator = CutFillCalculator(grid_resolution=request.grid_resolution)
        volumes = calculator.calculate_volumes(
            dem=dem,
            proposed_grades=request.proposed_grades,
            bounds=request.bounds,
            property_boundary=property_boundary
        )
        
        # Generate visualization
        cut_map = np.array(volumes.get('cut_map', []))
        fill_map = np.array(volumes.get('fill_map', []))
        visualization = calculator.generate_visualization_map(
            cut_map, fill_map, request.bounds
        )
        
        return JSONResponse(content={
            'volumes': {
                'cut_yd3': volumes.get('cut_volume_yd3', 0),
                'fill_yd3': volumes.get('fill_volume_yd3', 0),
                'net_yd3': volumes.get('net_volume_yd3', 0),
                'cut_ft3': volumes.get('cut_volume_ft3', 0),
                'fill_ft3': volumes.get('fill_volume_ft3', 0),
                'net_ft3': volumes.get('net_volume_ft3', 0)
            },
            'area_breakdown': volumes.get('area_breakdown', {}),
            'visualization': visualization,
            'cut_map': volumes.get('cut_map', []),
            'fill_map': volumes.get('fill_map', []),
            'message': 'Cut/fill calculation completed successfully'
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating cut/fill: {str(e)}")

