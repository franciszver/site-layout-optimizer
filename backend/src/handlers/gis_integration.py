"""
GIS Integration API endpoints for third-party GIS system integration.
Provides REST API endpoints for querying and exporting layouts in GIS-compatible formats.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

router = APIRouter(prefix="/gis", tags=["GIS Integration"])


class LayoutSummary(BaseModel):
    """Summary of a layout for listing endpoints."""
    layout_id: str
    file_id: str
    created_at: str
    asset_count: int
    road_count: int
    property_area: Optional[float] = None


class LayoutDetail(BaseModel):
    """Detailed layout information for GIS systems."""
    layout_id: str
    file_id: str
    created_at: str
    updated_at: str
    properties: List[dict]
    exclusion_zones: List[dict]
    assets: List[dict]
    roads: List[dict]
    terrain_data: Optional[dict] = None
    optimization_metrics: Optional[dict] = None


class SyncRequest(BaseModel):
    """Request to sync layout to GIS system."""
    gis_system: str
    target_layer: Optional[str] = None
    metadata: Optional[dict] = None


class SyncResponse(BaseModel):
    """Response from sync operation."""
    success: bool
    message: str
    sync_id: Optional[str] = None
    timestamp: str


# In-memory storage for demo (replace with database in production)
_layouts_store: dict = {}


@router.get("/layouts", response_model=List[LayoutSummary])
async def list_layouts(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of layouts to return"),
    offset: int = Query(0, ge=0, description="Number of layouts to skip"),
    file_id: Optional[str] = Query(None, description="Filter by file ID"),
):
    """
    List all available layouts with filtering options.
    
    This endpoint allows GIS systems to query available layouts and retrieve summaries.
    Supports pagination and filtering by file ID.
    """
    # In production, this would query the database
    # For demo, return empty list or mock data
    layouts = []
    
    # If we have layouts in store, return them
    for layout_id, layout_data in _layouts_store.items():
        if file_id and layout_data.get("file_id") != file_id:
            continue
        
        layouts.append(LayoutSummary(
            layout_id=layout_id,
            file_id=layout_data.get("file_id", ""),
            created_at=layout_data.get("created_at", datetime.utcnow().isoformat()),
            asset_count=len(layout_data.get("assets", [])),
            road_count=len(layout_data.get("roads", [])),
            property_area=layout_data.get("property_area"),
        ))
    
    # Apply pagination
    return layouts[offset:offset + limit]


@router.get("/layouts/{layout_id}", response_model=LayoutDetail)
async def get_layout(layout_id: str):
    """
    Get detailed layout information by layout ID.
    
    Returns complete layout data including properties, exclusion zones, assets, roads,
    and terrain data in a format suitable for GIS system import.
    """
    if layout_id not in _layouts_store:
        raise HTTPException(status_code=404, detail=f"Layout {layout_id} not found")
    
    layout_data = _layouts_store[layout_id]
    
    return LayoutDetail(
        layout_id=layout_id,
        file_id=layout_data.get("file_id", ""),
        created_at=layout_data.get("created_at", datetime.utcnow().isoformat()),
        updated_at=layout_data.get("updated_at", datetime.utcnow().isoformat()),
        properties=layout_data.get("properties", []),
        exclusion_zones=layout_data.get("exclusion_zones", []),
        assets=layout_data.get("assets", []),
        roads=layout_data.get("roads", []),
        terrain_data=layout_data.get("terrain_data"),
        optimization_metrics=layout_data.get("optimization_metrics"),
    )


@router.get("/layouts/{layout_id}/geojson")
async def get_layout_geojson(
    layout_id: str,
    include_terrain: bool = Query(False, description="Include terrain data in GeoJSON"),
):
    """
    Get layout as GeoJSON FeatureCollection.
    
    Returns the layout in standard GeoJSON format, suitable for direct import
    into most GIS systems (QGIS, ArcGIS, etc.).
    """
    if layout_id not in _layouts_store:
        raise HTTPException(status_code=404, detail=f"Layout {layout_id} not found")
    
    layout_data = _layouts_store[layout_id]
    
    features = []
    
    # Add property boundaries
    for prop in layout_data.get("properties", []):
        if "geometry" in prop:
            features.append({
                "type": "Feature",
                "geometry": prop["geometry"],
                "properties": {
                    "type": "property_boundary",
                    "layout_id": layout_id,
                    **prop.get("attributes", {}),
                },
            })
    
    # Add exclusion zones
    for zone in layout_data.get("exclusion_zones", []):
        if "geometry" in zone:
            features.append({
                "type": "Feature",
                "geometry": zone["geometry"],
                "properties": {
                    "type": "exclusion_zone",
                    "layout_id": layout_id,
                    **zone.get("attributes", {}),
                },
            })
    
    # Add assets as points
    for asset in layout_data.get("assets", []):
        location = asset.get("location", [0, 0])
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": location,
            },
            "properties": {
                "type": "asset",
                "asset_id": asset.get("id"),
                "asset_type": asset.get("type"),
                "layout_id": layout_id,
                **asset.get("dimensions", {}),
            },
        })
    
    # Add roads as LineStrings
    for road in layout_data.get("roads", []):
        centerline = road.get("centerline", [])
        if centerline:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": centerline,
                },
                "properties": {
                    "type": "road",
                    "road_type": road.get("type", "access"),
                    "layout_id": layout_id,
                    "length": road.get("length"),
                },
            })
    
    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "layout_id": layout_id,
            "file_id": layout_data.get("file_id"),
            "created_at": layout_data.get("created_at"),
            "exported_at": datetime.utcnow().isoformat(),
        },
    }
    
    if include_terrain and layout_data.get("terrain_data"):
        geojson["metadata"]["terrain_data"] = layout_data["terrain_data"]
    
    return geojson


@router.post("/layouts/{layout_id}/sync", response_model=SyncResponse)
async def sync_layout_to_gis(
    layout_id: str,
    sync_request: SyncRequest,
):
    """
    Sync layout to a third-party GIS system.
    
    This endpoint initiates a sync operation to push layout data to an external
    GIS system. The actual sync implementation would depend on the target system.
    """
    if layout_id not in _layouts_store:
        raise HTTPException(status_code=404, detail=f"Layout {layout_id} not found")
    
    # In production, this would:
    # 1. Validate GIS system credentials
    # 2. Transform data to target system format
    # 3. Push to GIS system via API
    # 4. Store sync status in database
    
    sync_id = f"sync_{layout_id}_{datetime.utcnow().timestamp()}"
    
    return SyncResponse(
        success=True,
        message=f"Layout {layout_id} synced to {sync_request.gis_system}",
        sync_id=sync_id,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/layouts/{layout_id}/shapefile")
async def export_shapefile(layout_id: str):
    """
    Export layout as Shapefile (ZIP archive).
    
    Returns a ZIP file containing the layout data in Shapefile format,
    suitable for import into GIS systems that require Shapefile format.
    """
    if layout_id not in _layouts_store:
        raise HTTPException(status_code=404, detail=f"Layout {layout_id} not found")
    
    # In production, this would:
    # 1. Convert GeoJSON to Shapefile using geopandas or similar
    # 2. Create ZIP archive with .shp, .shx, .dbf, .prj files
    # 3. Return as file download
    
    raise HTTPException(
        status_code=501,
        detail="Shapefile export not yet implemented. Use GeoJSON endpoint instead.",
    )


# Helper function to register a layout (called from other handlers)
def register_layout(layout_id: str, layout_data: dict):
    """Register a layout in the GIS integration store."""
    _layouts_store[layout_id] = {
        **layout_data,
        "created_at": layout_data.get("created_at", datetime.utcnow().isoformat()),
        "updated_at": datetime.utcnow().isoformat(),
    }

