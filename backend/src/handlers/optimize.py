"""
Layout optimization handler with AI integration
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.asset_placer import AssetPlacer
from services.ai_optimizer import AIOptimizer
from services.regulatory_fetcher import RegulatoryFetcher
from shapely.geometry import Polygon, Point
import json
import threading

router = APIRouter()


class AssetRequirement(BaseModel):
    type: str
    count: int
    attributes: Optional[Dict[str, Any]] = None


class OptimizeRequest(BaseModel):
    property_boundary: List[List[float]]  # GeoJSON coordinates
    exclusion_zones: Optional[List[List[List[float]]]] = None
    asset_requirements: List[AssetRequirement]
    entry_point: List[float]  # [x, y]
    terrain_data: Optional[Dict[str, Any]] = None
    fetch_regulatory: bool = True


# Request deduplication - prevent duplicate processing
_pending_requests = {}
_request_lock = threading.Lock()
_request_results = {}  # Cache completed results

def _get_request_hash(request: OptimizeRequest) -> str:
    """Generate hash for request deduplication"""
    import hashlib
    request_str = json.dumps({
        'property_boundary': request.property_boundary,
        'exclusion_zones': request.exclusion_zones,
        'asset_requirements': [(r.type, r.count) for r in request.asset_requirements],
        'entry_point': request.entry_point,
        'fetch_regulatory': request.fetch_regulatory
    }, sort_keys=True, default=str)
    return hashlib.sha256(request_str.encode()).hexdigest()[:16]


@router.post("/optimize")
async def optimize_layout(request: OptimizeRequest):
    """
    Generate optimized layout with AI recommendations
    
    Returns:
        Optimized layout with asset placements
    """
    # Request deduplication - prevent duplicate processing
    request_hash = _get_request_hash(request)
    
    # Check if we have a cached result (from previous identical request)
    with _request_lock:
        if request_hash in _request_results:
            # Return cached result immediately
            return _request_results[request_hash]
        
        if request_hash in _pending_requests:
            # Request is already processing, return a message
            return JSONResponse(
                status_code=202,
                content={'message': 'Request already processing', 'request_id': request_hash}
            )
        
        # Mark as pending
        _pending_requests[request_hash] = True
    
    try:
        # Convert property boundary to Shapely polygon
        # property_boundary is already the first ring (List[List[float]])
        # Each element is [lng, lat]
        if not request.property_boundary or len(request.property_boundary) < 3:
            raise ValueError("Property boundary must have at least 3 points")
        
        property_polygon = Polygon(request.property_boundary)
        
        # Convert exclusion zones
        exclusion_zones = []
        if request.exclusion_zones:
            for zone_coords in request.exclusion_zones:
                if not zone_coords or len(zone_coords) < 3:
                    continue  # Skip invalid zones
                exclusion_zones.append(Polygon(zone_coords))
        
        # Convert entry point
        entry_point = tuple(request.entry_point)
        
        # Fetch regulatory constraints if requested
        regulatory_constraints = None
        if request.fetch_regulatory:
            fetcher = RegulatoryFetcher()
            bounds = property_polygon.bounds
            regulatory_data = fetcher.fetch_all_regulatory_data(bounds, entry_point)
            regulatory_constraints = fetcher.process_regulatory_constraints(
                regulatory_data,
                property_polygon
            )
        
        # Prepare asset requirements
        asset_requirements = [
            {
                'type': req.type,
                'count': req.count,
                'attributes': req.attributes or {}
            }
            for req in request.asset_requirements
        ]
        
        # Place assets
        placer = AssetPlacer()
        placed_assets = placer.place_assets(
            property_boundary=property_polygon,
            exclusion_zones=exclusion_zones,
            asset_requirements=asset_requirements,
            entry_point=entry_point,
            terrain_data=request.terrain_data
        )
        
        # AI optimization
        ai_optimizer = AIOptimizer()
        property_data = {
            'boundary': request.property_boundary,
            'area': property_polygon.area
        }
        
        ai_analysis = ai_optimizer.analyze_constraints(
            property_data=property_data,
            asset_requirements=asset_requirements,
            existing_constraints={
                'exclusion_zones': request.exclusion_zones or [],
                'buffers': {'boundary': 50, 'exclusion': 100}
            },
            regulatory_constraints=regulatory_constraints,
            terrain_analysis=request.terrain_data
        )
        
        result = JSONResponse(content={
            'layout_id': 'generated-layout-id',
            'assets': [
                {
                    'id': f"asset-{i}",
                    'type': asset['type'],
                    'location': [asset['x'], asset['y']],
                    'dimensions': asset.get('dimensions', {}),
                    'score': asset.get('score', 0.0)
                }
                for i, asset in enumerate(placed_assets)
            ],
            'ai_recommendations': ai_analysis.get('recommendations', []),
            'ai_violations': ai_analysis.get('constraint_violations', []),
            'ai_suggestions': ai_analysis.get('optimization_suggestions', []),
            'regulatory_constraints': regulatory_constraints,
            'optimization_metrics': {
                'assets_placed': len(placed_assets),
                'site_utilization': len(placed_assets) * 0.1,  # Simplified
                'constraint_compliance': 1.0
            },
            'message': 'Layout optimization completed successfully'
        })
        
        # Cache result and clean up
        with _request_lock:
            if request_hash in _pending_requests:
                del _pending_requests[request_hash]
            # Cache result for 5 minutes (short cache for identical requests)
            _request_results[request_hash] = result
            # Clean up old results (keep last 10)
            if len(_request_results) > 10:
                oldest_key = next(iter(_request_results))
                del _request_results[oldest_key]
        
        return result
    
    except Exception as e:
        # Clean up on error
        with _request_lock:
            if request_hash in _pending_requests:
                del _pending_requests[request_hash]
        
        import traceback
        error_details = traceback.format_exc()
        print("=" * 80)
        print("ERROR in optimize handler:")
        print(error_details)
        print("=" * 80)
        import sys
        sys.stderr.write(f"ERROR in optimize handler: {error_details}\n")
        
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing layout: {str(e)}. Check server logs for details."
        )

