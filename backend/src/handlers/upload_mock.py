"""
Mock upload handler for demo purposes when GDAL is not available
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import json
import random
from datetime import datetime

router = APIRouter()

def generate_demo_property(property_type: str = "flat") -> dict:
    """Generate realistic demo property data"""
    # Base location (Kansas, USA)
    base_lng = -98.5795
    base_lat = 39.8283
    
    if property_type == "flat":
        # Flat terrain property (~150 acres)
        size = 0.01  # degrees (roughly 150 acres)
        elevations = [1000, 1001, 1000.5, 1001.5, 1000.8]
    elif property_type == "hilly":
        # Hilly terrain property (~250 acres)
        size = 0.015
        elevations = [1000, 1020, 1010, 1030, 1015, 1025, 1005, 1022]
    else:  # constrained
        # Constrained property with exclusion zones (~350 acres)
        size = 0.018
        elevations = [1000, 1015, 1005, 1020, 1010, 1018, 1008, 1012]
    
    minx = base_lng - size/2
    maxx = base_lng + size/2
    miny = base_lat - size/2
    maxy = base_lat + size/2
    
    # Generate property boundary
    property_boundary = {
        "type": "Polygon",
        "coordinates": [[
            [minx, miny],
            [maxx, miny],
            [maxx, maxy],
            [minx, maxy],
            [minx, miny]
        ]]
    }
    
    # Generate exclusion zones
    exclusion_zones = []
    if property_type == "hilly":
        # Add steep slope exclusion zone (common in hilly terrain)
        exclusion_zones.append({
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [base_lng - size*0.2, base_lat - size*0.1],
                    [base_lng - size*0.05, base_lat - size*0.1],
                    [base_lng - size*0.05, base_lat + size*0.1],
                    [base_lng - size*0.2, base_lat + size*0.1],
                    [base_lng - size*0.2, base_lat - size*0.1]
                ]]
            },
            "attributes": {"type": "steep_slope", "max_slope": ">15%"}
        })
        # Add another steep area
        exclusion_zones.append({
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [base_lng + size*0.1, base_lat + size*0.15],
                    [base_lng + size*0.25, base_lat + size*0.15],
                    [base_lng + size*0.25, base_lat + size*0.3],
                    [base_lng + size*0.1, base_lat + size*0.3],
                    [base_lng + size*0.1, base_lat + size*0.15]
                ]]
            },
            "attributes": {"type": "steep_slope", "max_slope": ">12%"}
        })
    elif property_type == "constrained":
        # Add wetland exclusion zone
        exclusion_zones.append({
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [base_lng - size*0.15, base_lat - size*0.15],
                    [base_lng - size*0.05, base_lat - size*0.15],
                    [base_lng - size*0.05, base_lat - size*0.05],
                    [base_lng - size*0.15, base_lat - size*0.05],
                    [base_lng - size*0.15, base_lat - size*0.15]
                ]]
            },
            "attributes": {"type": "wetland"}
        })
        # Add flood zone
        exclusion_zones.append({
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [base_lng + size*0.05, base_lat + size*0.05],
                    [base_lng + size*0.15, base_lat + size*0.05],
                    [base_lng + size*0.15, base_lat + size*0.15],
                    [base_lng + size*0.05, base_lat + size*0.15],
                    [base_lng + size*0.05, base_lat + size*0.05]
                ]]
            },
            "attributes": {"type": "flood_zone"}
        })
    
    # Generate contour lines
    contours = []
    for i, elev in enumerate(elevations):
        x_offset = (i % 4) * size / 4 - size/2
        y_offset = (i // 4) * size / 4 - size/2
        contours.append({
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [base_lng + x_offset - size/8, base_lat + y_offset],
                    [base_lng + x_offset + size/8, base_lat + y_offset]
                ]
            },
            "elevation": elev
        })
    
    return {
        "properties": [{
            "geometry": property_boundary,
            "attributes": {
                "name": f"Demo {property_type.title()} Property",
                "area": 150.0 if property_type == "flat" else (250.0 if property_type == "hilly" else 350.0),
                "type": property_type
            }
        }],
        "exclusion_zones": exclusion_zones,
        "contours": contours
    }

# Default mock property data
MOCK_PROPERTY_DATA = {
    "file_id": "demo-property-001",
    "file_name": "demo_property.kmz",
    "s3_key": "uploads/demo_property.kmz",
    "s3_bucket": "demo-bucket",
    "properties": [
        {
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-98.5795, 39.8283],
                    [-98.5695, 39.8283],
                    [-98.5695, 39.8383],
                    [-98.5795, 39.8383],
                    [-98.5795, 39.8283]
                ]]
            },
            "attributes": {
                "name": "Demo Property",
                "area": 150.0
            }
        }
    ],
    "exclusion_zones": [
        {
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-98.5750, 39.8300],
                    [-98.5720, 39.8300],
                    [-98.5720, 39.8320],
                    [-98.5750, 39.8320],
                    [-98.5750, 39.8300]
                ]]
            },
            "attributes": {
                "type": "wetland"
            }
        }
    ],
    "contours": [
        {
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [-98.5795, 39.8283],
                    [-98.5695, 39.8283]
                ]
            },
            "elevation": 1000.0
        },
        {
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [-98.5795, 39.8383],
                    [-98.5695, 39.8383]
                ]
            },
            "elevation": 1005.0
        }
    ],
    "assets": [],
    "metadata": {
        "uploaded_at": "2025-01-10T12:00:00Z",
        "file_size": 1024000
    }
}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Mock upload handler - returns demo data when GDAL is not available
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content (even though we don't use it, FastAPI requires it)
        try:
            content = await file.read()
            file_size = len(content)
        except Exception as read_error:
            raise HTTPException(
                status_code=400,
                detail=f"Error reading file: {str(read_error)}"
            )
        
        # Better file extension extraction
        import os
        file_ext = os.path.splitext(file.filename)[1].lower()
        valid_extensions = ['.kmz', '.kml', '.geojson']
        
        if file_ext not in valid_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}. Supported: {', '.join(valid_extensions)}"
            )
        
        # Determine property type from filename or use default
        filename_lower = file.filename.lower()
        if 'hilly' in filename_lower or 'hill' in filename_lower:
            property_type = "hilly"
        elif 'constrained' in filename_lower or 'constraint' in filename_lower:
            property_type = "constrained"
        else:
            property_type = "flat"  # default
        
        # Generate demo property
        demo_data = generate_demo_property(property_type)
        
        # Return mock data for demo
        # Merge demo_data with response, avoiding key conflicts
        response_data = {
            'file_id': f"demo-{property_type}-{random.randint(1000, 9999)}",
            'file_name': file.filename,
            's3_key': f"uploads/{file.filename}",
            's3_bucket': 'demo-bucket',
            'properties': demo_data.get('properties', []),
            'exclusion_zones': demo_data.get('exclusion_zones', []),
            'contours': demo_data.get('contours', []),
            'assets': [],
            'metadata': {
                'uploaded_at': datetime.utcnow().isoformat() + 'Z',
                'file_size': file_size,
                'demo_mode': True,
                'property_type': property_type
            },
            'message': f'File uploaded and processed successfully (using {property_type} demo data - GDAL not installed)',
            'note': 'Install GDAL for full KMZ/KML parsing. See backend/GDAL_INSTALL_WINDOWS.md'
        }
        
        return JSONResponse(content=response_data)
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_details = traceback.format_exc()
        print("=" * 80)
        print("ERROR in upload_mock handler:")
        print(error_details)
        print("=" * 80)
        # Also log to stderr for better visibility
        import sys
        sys.stderr.write(f"ERROR in upload_mock handler: {error_details}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing upload: {str(e)}. Check server logs for details."
        )



