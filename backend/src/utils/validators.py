"""
Validation utilities for geospatial data
"""
from typing import Dict, Any, Optional, Tuple
import os


def validate_file_upload(file_path: str, max_size_mb: int = 100) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file
    
    Args:
        file_path: Path to file
        max_size_mb: Maximum file size in MB
    
    Returns:
        (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
    
    if file_size > max_size_mb:
        return False, f"File size ({file_size:.2f} MB) exceeds maximum ({max_size_mb} MB)"
    
    # Check file extension
    valid_extensions = ['.kmz', '.kml', '.geojson', '.shp', '.gpkg']
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext not in valid_extensions:
        return False, f"Unsupported file format: {file_ext}"
    
    return True, None


def validate_property_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate property data structure"""
    required_fields = ['properties', 'geometry']
    
    if 'properties' not in data:
        return False, "Missing 'properties' field"
    
    if not isinstance(data['properties'], list) or len(data['properties']) == 0:
        return False, "Properties list is empty"
    
    for prop in data['properties']:
        if 'geometry' not in prop:
            return False, "Property missing 'geometry' field"
    
    return True, None


def validate_asset_requirements(requirements: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate asset placement requirements"""
    required_fields = ['type', 'dimensions']
    
    for field in required_fields:
        if field not in requirements:
            return False, f"Missing required field: {field}"
    
    dimensions = requirements.get('dimensions', {})
    required_dims = ['length', 'width']
    
    for dim in required_dims:
        if dim not in dimensions:
            return False, f"Missing dimension: {dim}"
        
        if dimensions[dim] <= 0:
            return False, f"Invalid dimension value: {dim} must be > 0"
    
    return True, None

