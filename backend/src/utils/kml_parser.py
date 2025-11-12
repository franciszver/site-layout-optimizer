"""
KMZ/KML file parser using GDAL/OGR
"""
import os
import zipfile
import tempfile
from typing import Dict, List, Any, Optional, Tuple
import json

# Try to import GDAL, but handle gracefully if not available
try:
    from osgeo import ogr, osr
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False
    print("Warning: GDAL not available. KMZ/KML parsing will be limited.")

try:
    from shapely.geometry import shape, mapping
    from shapely.ops import transform
    import pyproj
except ImportError:
    pass


class KMLParser:
    """Parser for KMZ/KML files with geometry validation and reprojection"""
    
    def __init__(self):
        if not GDAL_AVAILABLE:
            raise ImportError("GDAL is required for KML parsing. Please install GDAL.")
        self.driver_kml = ogr.GetDriverByName('KML')
        self.driver_geojson = ogr.GetDriverByName('GeoJSON')
    
    def parse_file(self, file_path: str, target_crs: str = 'EPSG:4326') -> Dict[str, Any]:
        """
        Parse KMZ/KML file and extract geometries
        
        Args:
            file_path: Path to KMZ/KML file
            target_crs: Target coordinate reference system (default: WGS84)
        
        Returns:
            Dictionary with parsed geometries and metadata
        """
        # Handle KMZ (zipped KML)
        if file_path.endswith('.kmz'):
            return self._parse_kmz(file_path, target_crs)
        elif file_path.endswith('.kml'):
            return self._parse_kml(file_path, target_crs)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    def _parse_kmz(self, file_path: str, target_crs: str) -> Dict[str, Any]:
        """Parse KMZ file (zipped KML)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract KMZ
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
            
            # Find KML file in extracted contents
            kml_file = None
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    if file.endswith('.kml'):
                        kml_file = os.path.join(root, file)
                        break
                if kml_file:
                    break
            
            if not kml_file:
                raise ValueError("No KML file found in KMZ archive")
            
            return self._parse_kml(kml_file, target_crs)
    
    def _parse_kml(self, file_path: str, target_crs: str) -> Dict[str, Any]:
        """Parse KML file"""
        datasource = self.driver_kml.Open(file_path, 0)
        if datasource is None:
            raise ValueError(f"Could not open file: {file_path}")
        
        result = {
            'properties': [],
            'exclusion_zones': [],
            'contours': [],
            'assets': [],
            'metadata': {}
        }
        
        layer_count = datasource.GetLayerCount()
        
        for i in range(layer_count):
            layer = datasource.GetLayer(i)
            layer_name = layer.GetName()
            
            # Process features in layer
            layer.ResetReading()
            feature = layer.GetNextFeature()
            
            while feature:
                geometry = feature.GetGeometryRef()
                if geometry:
                    geom_dict = self._geometry_to_dict(geometry, target_crs)
                    attributes = self._get_feature_attributes(feature)
                    
                    # Categorize based on layer name or attributes
                    if 'property' in layer_name.lower() or 'boundary' in layer_name.lower():
                        result['properties'].append({
                            'geometry': geom_dict,
                            'attributes': attributes
                        })
                    elif 'exclusion' in layer_name.lower() or 'constraint' in layer_name.lower():
                        result['exclusion_zones'].append({
                            'geometry': geom_dict,
                            'attributes': attributes
                        })
                    elif 'contour' in layer_name.lower() or 'elevation' in layer_name.lower():
                        result['contours'].append({
                            'geometry': geom_dict,
                            'attributes': attributes
                        })
                    elif 'asset' in layer_name.lower() or 'building' in layer_name.lower():
                        result['assets'].append({
                            'geometry': geom_dict,
                            'attributes': attributes
                        })
                    else:
                        # Default to property if unclear
                        result['properties'].append({
                            'geometry': geom_dict,
                            'attributes': attributes
                        })
                
                feature = layer.GetNextFeature()
        
        datasource = None
        return result
    
    def _geometry_to_dict(self, geometry, target_crs: str) -> Dict[str, Any]:
        """Convert OGR geometry to GeoJSON-like dict with reprojection"""
        # Get source CRS from geometry (if available)
        source_srs = geometry.GetSpatialReference()
        
        if source_srs is None:
            # Assume WGS84 if no CRS specified
            source_srs = osr.SpatialReference()
            source_srs.ImportFromEPSG(4326)
        
        # Convert to WKT for Shapely
        wkt = geometry.ExportToWkt()
        shapely_geom = ogr.CreateGeometryFromWkt(wkt)
        
        # Reproject if needed
        target_srs = osr.SpatialReference()
        target_srs.ImportFromEPSG(int(target_crs.split(':')[1]))
        
        if not source_srs.IsSame(target_srs):
            transform_obj = osr.CoordinateTransformation(source_srs, target_srs)
            shapely_geom.Transform(transform_obj)
        
        # Convert to GeoJSON
        geojson_str = shapely_geom.ExportToJson()
        return json.loads(geojson_str)
    
    def _get_feature_attributes(self, feature) -> Dict[str, Any]:
        """Extract attributes from OGR feature"""
        attributes = {}
        field_count = feature.GetFieldCount()
        
        for i in range(field_count):
            field_defn = feature.GetFieldDefnRef(i)
            field_name = field_defn.GetName()
            field_value = feature.GetField(i)
            attributes[field_name] = field_value
        
        return attributes
    
    def validate_geometry(self, geometry_dict: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate geometry for common issues
        
        Returns:
            (is_valid, error_message)
        """
        try:
            geom = shape(geometry_dict)
            
            # Check if geometry is valid
            if not geom.is_valid:
                return False, f"Invalid geometry: {geom.validity_reason}"
            
            # Check for self-intersections
            if geom.geom_type in ['Polygon', 'MultiPolygon']:
                if not geom.is_simple:
                    return False, "Geometry has self-intersections"
            
            return True, None
        except Exception as e:
            return False, str(e)

