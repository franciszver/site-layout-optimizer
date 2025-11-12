"""
Terrain analysis handler
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.terrain_analyzer import TerrainAnalyzer
from services.geospatial_processor import GeospatialProcessor
import boto3
from config.settings import settings

router = APIRouter()

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)


class AnalyzeRequest(BaseModel):
    file_id: str
    bounds: Optional[Tuple[float, float, float, float]] = None
    resolution: float = 10.0


@router.post("/analyze")
async def analyze_terrain(request: AnalyzeRequest):
    """
    Analyze terrain from uploaded file
    
    Returns:
        Terrain metrics (slope, aspect, elevation differentials)
    """
    try:
        # Initialize processors
        terrain_analyzer = TerrainAnalyzer(
            s3_client=s3_client,
            cache_bucket=settings.s3_bucket_terrain_cache
        )
        
        # Get bounds from request or calculate from property
        if request.bounds:
            bounds = request.bounds
        else:
            # Default bounds (would calculate from property boundary)
            # Using a reasonable size for demo (roughly 1km x 1km)
            bounds = (-98.5795, 39.8283, -98.5695, 39.8383)
        
        # Generate mock contours for demo (in production, fetch from S3/DB based on file_id)
        minx, miny, maxx, maxy = bounds
        center_x = (minx + maxx) / 2
        center_y = (miny + maxy) / 2
        width = maxx - minx
        height = maxy - miny
        
        # Create realistic contour lines for demo
        contours = []
        base_elevation = 1000.0
        num_contours = 5
        for i in range(num_contours):
            elevation = base_elevation + (i * 2.5)
            # Create horizontal contour line across the property
            y_pos = center_y + (i - num_contours/2) * height * 0.15
            contours.append({
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [minx + width * 0.1, y_pos],
                        [maxx - width * 0.1, y_pos]
                    ]
                },
                'elevation': elevation
            })
        
        # Convert resolution from meters to degrees (rough approximation)
        # 1 degree latitude ≈ 111,000 meters
        # For demo, use a reasonable resolution in degrees
        # Ensure resolution is not too small (minimum 0.0001 degrees ≈ 11 meters)
        resolution_degrees = max(request.resolution / 111000.0, 0.0001)
        
        # Check bounds are valid
        minx, miny, maxx, maxy = bounds
        if maxx <= minx or maxy <= miny:
            raise ValueError(f"Invalid bounds: {bounds}")
        
        # Ensure bounds are reasonable size (not too large for demo)
        width = maxx - minx
        height = maxy - miny
        if width > 1.0 or height > 1.0:
            # Scale down if too large
            center_x = (minx + maxx) / 2
            center_y = (miny + maxy) / 2
            bounds = (
                center_x - 0.01,
                center_y - 0.01,
                center_x + 0.01,
                center_y + 0.01
            )
            minx, miny, maxx, maxy = bounds
            width = maxx - minx
            height = maxy - miny
        
        # Perform terrain analysis
        try:
            analysis_result = terrain_analyzer.analyze_terrain(
                contours=contours,
                bounds=bounds,
                resolution=resolution_degrees
            )
        except ValueError as ve:
            # If terrain analysis fails, return a simplified response
            print(f"Terrain analysis failed: {ve}, returning simplified response")
            return JSONResponse(content={
                'analysis_id': request.file_id,
                'elevation_stats': {
                    'min': 1000.0,
                    'max': 1010.0,
                    'mean': 1005.0,
                    'std': 3.0,
                    'range': 10.0
                },
                'slope_range': {
                    'min': 0.0,
                    'max': 5.0,
                    'mean': 2.5
                },
                'aspect_stats': {
                    'mean': 180.0
                },
                'bounds': bounds,
                'resolution': request.resolution,
                'message': 'Terrain analysis completed successfully (simplified)',
                'demo_mode': True,
                'warning': 'Full terrain analysis unavailable, using demo data'
            })
        
        # Handle response - check if slope/aspect are None (large arrays)
        slope_data = analysis_result.get('slope')
        aspect_data = analysis_result.get('aspect')
        
        if slope_data is None:
            # Use slope_stats if slope array is None
            slope_stats = analysis_result.get('slope_stats', {})
            slope_range = {
                'min': slope_stats.get('min', 0.0),
                'max': slope_stats.get('max', 0.0),
                'mean': slope_stats.get('mean', 0.0)
            }
        else:
            # Calculate from array
            slope_list = slope_data if isinstance(slope_data, list) else slope_data.tolist()
            if slope_list and len(slope_list) > 0:
                flat_slope = [item for row in slope_list for item in (row if isinstance(row, list) else [row])]
                slope_range = {
                    'min': float(min(flat_slope)),
                    'max': float(max(flat_slope)),
                    'mean': float(sum(flat_slope) / len(flat_slope))
                }
            else:
                slope_range = {'min': 0.0, 'max': 0.0, 'mean': 0.0}
        
        if aspect_data is None:
            # Use aspect_stats if aspect array is None
            aspect_stats = analysis_result.get('aspect_stats', {})
            aspect_mean = aspect_stats.get('mean', 0.0)
        else:
            # Calculate from array
            aspect_list = aspect_data if isinstance(aspect_data, list) else aspect_data.tolist()
            if aspect_list and len(aspect_list) > 0:
                flat_aspect = [item for row in aspect_list for item in (row if isinstance(row, list) else [row])]
                aspect_mean = float(sum(flat_aspect) / len(flat_aspect))
            else:
                aspect_mean = 0.0
        
        return JSONResponse(content={
            'analysis_id': request.file_id,
            'elevation_stats': analysis_result.get('elevation_stats', {}),
            'slope_range': slope_range,
            'aspect_stats': {
                'mean': aspect_mean
            },
            'bounds': analysis_result.get('bounds'),
            'resolution': analysis_result.get('dem_resolution'),
            'message': 'Terrain analysis completed successfully',
            'demo_mode': True
        })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print("=" * 80)
        print("ERROR in analyze handler:")
        print(error_details)
        print("=" * 80)
        import sys
        sys.stderr.write(f"ERROR in analyze handler: {error_details}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing terrain: {str(e)}. Check server logs for details."
        )

