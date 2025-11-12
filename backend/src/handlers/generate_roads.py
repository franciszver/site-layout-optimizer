"""
Road network generation handler
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.road_generator import RoadGenerator
from shapely.geometry import Polygon
import numpy as np

router = APIRouter()


class GenerateRoadsRequest(BaseModel):
    entry_point: List[float]  # [x, y]
    assets: List[Dict[str, Any]]
    property_boundary: List[List[float]]
    exclusion_zones: Optional[List[List[List[float]]]] = None
    terrain_data: Optional[Dict[str, Any]] = None


@router.post("/generate-roads")
async def generate_roads(request: GenerateRoadsRequest):
    """
    Generate road network connecting entry to assets
    
    Returns:
        Road network geometry
    """
    try:
        # Convert to Shapely geometries
        # property_boundary is already the first ring (List[List[float]])
        if not request.property_boundary or len(request.property_boundary) < 3:
            raise ValueError("Property boundary must have at least 3 points")
        
        property_polygon = Polygon(request.property_boundary)
        
        exclusion_zones = []
        if request.exclusion_zones:
            for zone_coords in request.exclusion_zones:
                if not zone_coords or len(zone_coords) < 3:
                    continue  # Skip invalid zones
                exclusion_zones.append(Polygon(zone_coords))
        
        entry_point = tuple(request.entry_point)
        
        # Prepare terrain data
        dem = None
        bounds = None
        resolution = 10.0
        
        if request.terrain_data:
            dem_data = request.terrain_data.get('dem', None)
            # Handle None (for large arrays that weren't serialized)
            if dem_data is not None and len(dem_data) > 0:
                dem = np.array(dem_data)
            else:
                dem = None  # Large array not available, road generator will use fallback
            bounds = tuple(request.terrain_data.get('bounds', (0, 0, 0, 0)))
            resolution = request.terrain_data.get('dem_resolution', 10.0)
        
        # Ensure assets have x, y format (not location)
        formatted_assets = []
        for asset in request.assets:
            # Handle both formats: {x, y} or {location: [x, y]}
            if 'x' in asset and 'y' in asset:
                formatted_assets.append(asset)
            elif 'location' in asset and isinstance(asset['location'], list) and len(asset['location']) >= 2:
                formatted_assets.append({
                    'id': asset.get('id'),
                    'type': asset.get('type'),
                    'x': asset['location'][0],
                    'y': asset['location'][1],
                    'dimensions': asset.get('dimensions', {}),
                })
            else:
                # Skip invalid assets
                continue
        
        if len(formatted_assets) == 0:
            raise ValueError("No valid assets provided for road generation")
        
        # Generate road network
        print(f"Generating road network for {len(formatted_assets)} assets")
        print(f"Entry point: {entry_point}")
        print(f"Property boundary bounds: {property_polygon.bounds}")
        
        road_generator = RoadGenerator()
        try:
            road_network = road_generator.generate_road_network(
                entry_point=entry_point,
                assets=formatted_assets,
                property_boundary=property_polygon,
                exclusion_zones=exclusion_zones,
                dem=dem,
                bounds=bounds,
                resolution=resolution
            )
            
            print(f"Road network generated: {len(road_network.get('roads', []))} roads")
            
            return JSONResponse(content={
                'road_network': road_network,
                'total_length_ft': road_network.get('total_length', 0),
                'road_count': len(road_network.get('roads', [])),
                'message': road_network.get('warning', 'Road network generated successfully')
            })
        except Exception as e:
            print(f"ERROR in road_generator.generate_road_network: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    except ValueError as e:
        # Validation errors
        import traceback
        error_details = traceback.format_exc()
        print("=" * 80)
        print("VALIDATION ERROR in generate_roads handler:")
        print(error_details)
        print("=" * 80)
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except Exception as e:
        # Other errors
        import traceback
        error_details = traceback.format_exc()
        print("=" * 80)
        print("ERROR in generate_roads handler:")
        print(error_details)
        print("=" * 80)
        raise HTTPException(status_code=500, detail=f"Error generating roads: {str(e)}")

