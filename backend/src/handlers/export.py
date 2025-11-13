"""
Export handler for PDF, KMZ, GeoJSON formats
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import tempfile
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import json
import zipfile
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
try:
    from osgeo import ogr, osr
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False
try:
    import boto3
    from config.settings import settings
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )
except Exception:
    # S3 not configured, that's okay for demo
    s3_client = None

router = APIRouter()


class ExportRequest(BaseModel):
    layout_id: str
    format: str  # pdf, kmz, geojson
    layout_data: Optional[Dict[str, Any]] = None  # Full layout data from frontend
    include_layers: Optional[list] = None
    include_statistics: bool = True


@router.post("/export")
async def export_layout(request: ExportRequest):
    """
    Export layout in specified format
    
    Returns:
        Download URL or file
    """
    if not request.layout_data:
        raise HTTPException(status_code=400, detail="No layout data provided")
    
    layout_data = request.layout_data
    
    # Validate layout data structure
    if not isinstance(layout_data, dict):
        raise HTTPException(status_code=400, detail="Invalid layout data format")
    
    # Ensure we have at least a property or assets
    has_properties = layout_data.get('properties') and len(layout_data.get('properties', [])) > 0
    has_assets = layout_data.get('assets') and len(layout_data.get('assets', [])) > 0
    has_roads = layout_data.get('roads') and len(layout_data.get('roads', [])) > 0
    
    if not (has_properties or has_assets or has_roads):
        raise HTTPException(
            status_code=400, 
            detail="Layout data must contain at least properties, assets, or roads"
        )
    
    try:
        format_lower = request.format.lower()
        if format_lower == 'pdf':
            return await _export_pdf(layout_data, request)
        elif format_lower == 'kmz':
            return await _export_kmz(layout_data, request)
        elif format_lower == 'geojson':
            return await _export_geojson(layout_data, request)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print("=" * 80)
        print(f"ERROR in export handler ({request.format}):")
        print(error_details)
        print("=" * 80)
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting {request.format}: {str(e)}. Check server logs for details."
        )


async def _export_pdf(layout_data: Dict[str, Any], request: ExportRequest) -> FileResponse:
    """Export layout as PDF with comprehensive report"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        pdf_path = tmp_file.name
    
    # Create PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 18)
    title = "Site Layout Report"
    title_width = c.stringWidth(title, "Helvetica-Bold", 18)
    c.drawString((width - title_width) / 2, height - 0.75 * inch, title)
    
    c.setFont("Helvetica", 12)
    subtitle = "Pacifico Energy Group - AI-Powered Geospatial Site Layout Optimization for Resources"
    subtitle_width = c.stringWidth(subtitle, "Helvetica", 12)
    c.drawString((width - subtitle_width) / 2, height - 1 * inch, subtitle)
    
    # Layout information
    c.setFont("Helvetica-Bold", 12)
    y_pos = height - 1.5 * inch
    c.drawString(1 * inch, y_pos, "Layout Information")
    
    c.setFont("Helvetica", 10)
    y_pos -= 0.25 * inch
    c.drawString(1 * inch, y_pos, f"Layout ID: {request.layout_id}")
    
    # Property information
    properties = layout_data.get('properties', [])
    if properties:
        y_pos -= 0.3 * inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, y_pos, "Property Details")
        c.setFont("Helvetica", 10)
        y_pos -= 0.25 * inch
        prop = properties[0]
        prop_name = prop.get('attributes', {}).get('name', 'Unnamed Property')
        c.drawString(1 * inch, y_pos, f"Property: {prop_name}")
    
    # Statistics
    if request.include_statistics:
        y_pos -= 0.4 * inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, y_pos, "Statistics")
        c.setFont("Helvetica", 10)
        
        # Assets
        assets = layout_data.get('assets', [])
        y_pos -= 0.25 * inch
        c.drawString(1 * inch, y_pos, f"Assets Placed: {len(assets)}")
        
        # Roads
        roads = layout_data.get('roads', [])
        if roads:
            y_pos -= 0.25 * inch
            total_length = sum(r.get('length', 0) for r in roads)
            # Convert from degrees to feet (approximate)
            total_length_ft = total_length * 364000.0
            total_length_miles = total_length_ft / 5280.0
            c.drawString(1 * inch, y_pos, f"Road Network: {len(roads)} segments, {total_length_miles:.2f} miles")
        
        # Exclusion zones
        exclusion_zones = layout_data.get('exclusion_zones', [])
        if exclusion_zones:
            y_pos -= 0.25 * inch
            c.drawString(1 * inch, y_pos, f"Exclusion Zones: {len(exclusion_zones)}")
        
        # Terrain data
        terrain_data = layout_data.get('terrain_data', {})
        if terrain_data:
            y_pos -= 0.3 * inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1 * inch, y_pos, "Terrain Analysis")
            c.setFont("Helvetica", 10)
            elevation_stats = terrain_data.get('elevation_stats', {})
            if elevation_stats:
                y_pos -= 0.25 * inch
                min_elev = elevation_stats.get('min', 0)
                max_elev = elevation_stats.get('max', 0)
                mean_elev = elevation_stats.get('mean', 0)
                c.drawString(1 * inch, y_pos, f"Elevation: {min_elev:.1f} - {max_elev:.1f} ft (mean: {mean_elev:.1f} ft)")
    
    # Asset breakdown
    if assets:
        y_pos -= 0.4 * inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, y_pos, "Asset Placement")
        c.setFont("Helvetica", 10)
        
        # Group assets by type
        asset_types = {}
        for asset in assets:
            asset_type = asset.get('type', 'Unknown')
            asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
        
        for asset_type, count in asset_types.items():
            y_pos -= 0.25 * inch
            if y_pos < 1 * inch:  # New page if needed
                c.showPage()
                y_pos = height - 1 * inch
            c.drawString(1.5 * inch, y_pos, f"{asset_type}: {count}")
    
    # Footer
    c.setFont("Helvetica", 8)
    footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Pacifico Energy Group"
    footer_width = c.stringWidth(footer_text, "Helvetica", 8)
    c.drawString((width - footer_width) / 2, 0.5 * inch, footer_text)
    
    c.save()
    
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f"layout_{request.layout_id}.pdf"
    )


def _escape_xml(text: str) -> str:
    """Escape XML special characters"""
    if not text:
        return ''
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))


async def _export_kmz(layout_data: Dict[str, Any], request: ExportRequest) -> FileResponse:
    """Export layout as KMZ with all features"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.kmz') as tmp_file:
        kmz_path = tmp_file.name
    
    # Build KML content
    kml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    kml_parts.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    kml_parts.append('<Document>')
    layout_name = _escape_xml(f'Layout {request.layout_id}')
    kml_parts.append(f'<name>{layout_name}</name>')
    kml_parts.append('<description>Site Layout Export - Pacifico Energy Group</description>')
    
    # Property boundary
    properties = layout_data.get('properties', [])
    if properties:
        prop = properties[0]
        geometry = prop.get('geometry', {})
        if geometry.get('type') == 'Polygon' and geometry.get('coordinates'):
            coords = geometry['coordinates'][0]  # First ring
            coord_string = ' '.join([f"{coord[0]},{coord[1]},0" for coord in coords])
            kml_parts.append('<Placemark>')
            kml_parts.append('<name>Property Boundary</name>')
            kml_parts.append('<description>Property boundary polygon</description>')
            kml_parts.append('<Polygon>')
            kml_parts.append('<outerBoundaryIs>')
            kml_parts.append('<LinearRing>')
            kml_parts.append(f'<coordinates>{coord_string}</coordinates>')
            kml_parts.append('</LinearRing>')
            kml_parts.append('</outerBoundaryIs>')
            kml_parts.append('</Polygon>')
            kml_parts.append('<Style>')
            kml_parts.append('<LineStyle><color>ff0000ff</color><width>3</width></LineStyle>')
            kml_parts.append('<PolyStyle><color>400000ff</color></PolyStyle>')
            kml_parts.append('</Style>')
            kml_parts.append('</Placemark>')
    
    # Exclusion zones
    exclusion_zones = layout_data.get('exclusion_zones', [])
    for idx, zone in enumerate(exclusion_zones):
        zone_geom = zone.get('geometry', {})
        if zone_geom.get('type') == 'Polygon' and zone_geom.get('coordinates'):
            coords = zone_geom['coordinates'][0]
            coord_string = ' '.join([f"{coord[0]},{coord[1]},0" for coord in coords])
            kml_parts.append('<Placemark>')
            kml_parts.append(f'<name>Exclusion Zone {idx + 1}</name>')
            kml_parts.append('<description>Area to avoid during development</description>')
            kml_parts.append('<Polygon>')
            kml_parts.append('<outerBoundaryIs>')
            kml_parts.append('<LinearRing>')
            kml_parts.append(f'<coordinates>{coord_string}</coordinates>')
            kml_parts.append('</LinearRing>')
            kml_parts.append('</outerBoundaryIs>')
            kml_parts.append('</Polygon>')
            kml_parts.append('<Style>')
            kml_parts.append('<LineStyle><color>ff00ffff</color><width>2</width></LineStyle>')
            kml_parts.append('<PolyStyle><color>4000ffff</color></PolyStyle>')
            kml_parts.append('</Style>')
            kml_parts.append('</Placemark>')
    
    # Assets
    assets = layout_data.get('assets', [])
    for asset in assets:
        location = asset.get('location', [asset.get('x', 0), asset.get('y', 0)])
        asset_type = asset.get('type', 'Asset')
        asset_id = asset.get('id', 'unknown')
        kml_parts.append('<Placemark>')
        asset_name = _escape_xml(f'{asset_type} - {asset_id}')
        kml_parts.append(f'<name>{asset_name}</name>')
        kml_parts.append(f'<description>Asset: {asset_type}</description>')
        kml_parts.append(f'<Point><coordinates>{location[0]},{location[1]},0</coordinates></Point>')
        kml_parts.append('<Style>')
        kml_parts.append('<IconStyle>')
        kml_parts.append('<color>ffff00ff</color>')
        kml_parts.append('<scale>1.2</scale>')
        kml_parts.append('<Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>')
        kml_parts.append('</IconStyle>')
        kml_parts.append('</Style>')
        kml_parts.append('</Placemark>')
    
    # Roads
    roads = layout_data.get('roads', [])
    for idx, road in enumerate(roads):
        centerline = road.get('centerline', [])
        if centerline:
            coord_string = ' '.join([f"{coord[0]},{coord[1]},0" for coord in centerline])
            road_type = road.get('type', 'road')
            kml_parts.append('<Placemark>')
            road_name = _escape_xml(f'Road {idx + 1} - {road_type}')
            kml_parts.append(f'<name>{road_name}</name>')
            kml_parts.append(f'<description>Road segment: {road_type}, Width: {road.get("width", 20)}ft</description>')
            kml_parts.append('<LineString>')
            kml_parts.append(f'<coordinates>{coord_string}</coordinates>')
            kml_parts.append('</LineString>')
            kml_parts.append('<Style>')
            kml_parts.append('<LineStyle>')
            kml_parts.append('<color>ff0066ff</color>')  # Orange/red
            kml_parts.append(f'<width>{road.get("width", 20) / 2}</width>')
            kml_parts.append('</LineStyle>')
            kml_parts.append('</Style>')
            kml_parts.append('</Placemark>')
    
    kml_parts.append('</Document>')
    kml_parts.append('</kml>')
    
    kml_content = '\n'.join(kml_parts)
    
    # Create KMZ file
    with zipfile.ZipFile(kmz_path, 'w', zipfile.ZIP_DEFLATED) as kmz:
        kmz.writestr('doc.kml', kml_content)
    
    return FileResponse(
        kmz_path,
        media_type='application/vnd.google-earth.kmz',
        filename=f"layout_{request.layout_id}.kmz"
    )


async def _export_geojson(layout_data: Dict[str, Any], request: ExportRequest) -> JSONResponse:
    """Export layout as GeoJSON with all features"""
    features = []
    
    # Property boundary
    properties = layout_data.get('properties', [])
    for prop in properties:
        geometry = prop.get('geometry', {})
        if geometry:
            features.append({
                'type': 'Feature',
                'geometry': geometry,
                'properties': {
                    'name': prop.get('attributes', {}).get('name', 'Property Boundary'),
                    'type': 'property',
                    'layout_id': request.layout_id
                }
            })
    
    # Exclusion zones
    exclusion_zones = layout_data.get('exclusion_zones', [])
    for idx, zone in enumerate(exclusion_zones):
        zone_geom = zone.get('geometry', {})
        if zone_geom:
            features.append({
                'type': 'Feature',
                'geometry': zone_geom,
                'properties': {
                    'name': f'Exclusion Zone {idx + 1}',
                    'type': 'exclusion_zone',
                    'layout_id': request.layout_id
                }
            })
    
    # Assets
    assets = layout_data.get('assets', [])
    for asset in assets:
        location = asset.get('location', [asset.get('x', 0), asset.get('y', 0)])
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': location
            },
            'properties': {
                'id': asset.get('id', 'unknown'),
                'type': asset.get('type', 'asset'),
                'dimensions': asset.get('dimensions', {}),
                'layout_id': request.layout_id
            }
        })
    
    # Roads
    roads = layout_data.get('roads', [])
    for idx, road in enumerate(roads):
        centerline = road.get('centerline', [])
        if centerline:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': centerline
                },
                'properties': {
                    'id': f'road-{idx}',
                    'type': road.get('type', 'road'),
                    'width': road.get('width', 20),
                    'length': road.get('length', 0),
                    'layout_id': request.layout_id
                }
            })
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features,
        'metadata': {
            'layout_id': request.layout_id,
            'exported_at': datetime.now().isoformat(),
            'feature_count': len(features),
            'asset_count': len(assets),
            'road_count': len(roads),
            'exclusion_zone_count': len(exclusion_zones)
        }
    }
    
    return JSONResponse(
        content=geojson,
        headers={
            'Content-Disposition': f'attachment; filename="layout_{request.layout_id}.geojson"'
        }
    )

