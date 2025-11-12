"""
Geospatial data processor for KMZ/KML files
"""
import os
import boto3
from typing import Dict, Any, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.kml_parser import KMLParser
from utils.validators import validate_file_upload, validate_property_data
import json


class GeospatialProcessor:
    """Process and validate geospatial files"""
    
    def __init__(self, s3_client=None, bucket_name: str = None):
        self.parser = KMLParser()
        self.s3_client = s3_client or boto3.client('s3')
        self.bucket_name = bucket_name
    
    def process_upload(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """
        Process uploaded geospatial file
        
        Args:
            file_path: Local path to uploaded file
            file_name: Original file name
        
        Returns:
            Dictionary with processing results and S3 location
        """
        # Validate file
        is_valid, error = validate_file_upload(file_path)
        if not is_valid:
            raise ValueError(error)
        
        # Parse file
        parsed_data = self.parser.parse_file(file_path)
        
        # Validate parsed data
        is_valid, error = validate_property_data(parsed_data)
        if not is_valid:
            raise ValueError(error)
        
        # Validate geometries
        for prop in parsed_data.get('properties', []):
            geom = prop.get('geometry')
            if geom:
                is_valid, error = self.parser.validate_geometry(geom)
                if not is_valid:
                    raise ValueError(f"Invalid geometry: {error}")
        
        # Upload to S3
        s3_key = f"uploads/{file_name}"
        if self.bucket_name:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
        
        # Store metadata
        result = {
            'file_name': file_name,
            's3_key': s3_key,
            's3_bucket': self.bucket_name,
            'properties': parsed_data.get('properties', []),
            'exclusion_zones': parsed_data.get('exclusion_zones', []),
            'contours': parsed_data.get('contours', []),
            'assets': parsed_data.get('assets', []),
            'metadata': parsed_data.get('metadata', {})
        }
        
        return result
    
    def extract_property_boundaries(self, parsed_data: Dict[str, Any]) -> list:
        """Extract property boundaries from parsed data"""
        boundaries = []
        for prop in parsed_data.get('properties', []):
            geom = prop.get('geometry')
            if geom and geom.get('type') == 'Polygon':
                boundaries.append(geom)
        return boundaries
    
    def extract_exclusion_zones(self, parsed_data: Dict[str, Any]) -> list:
        """Extract exclusion zones from parsed data"""
        zones = []
        for zone in parsed_data.get('exclusion_zones', []):
            geom = zone.get('geometry')
            if geom:
                zones.append(geom)
        return zones
    
    def extract_contours(self, parsed_data: Dict[str, Any]) -> list:
        """Extract contour lines from parsed data"""
        contours = []
        for contour in parsed_data.get('contours', []):
            geom = contour.get('geometry')
            attrs = contour.get('attributes', {})
            if geom and geom.get('type') == 'LineString':
                contours.append({
                    'geometry': geom,
                    'elevation': attrs.get('elevation', attrs.get('ELEVATION', None))
                })
        return contours

