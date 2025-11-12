"""
Regulatory constraint fetcher for FEMA, EPA, and USGS APIs
"""
import httpx
from typing import Dict, Any, List, Optional, Tuple
from shapely.geometry import Polygon, Point
import json


class RegulatoryFetcher:
    """Fetch regulatory constraints from external APIs"""
    
    def __init__(self):
        self.fema_base_url = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer"
        self.epa_wetlands_url = "https://www.fws.gov/wetlands/arcgis/rest/services/Wetlands/MapServer"
        self.usgs_base_url = "https://elevation.nationalmap.gov/arcgis/rest/services"
    
    def fetch_flood_zones(
        self,
        bounds: Tuple[float, float, float, float],
        property_location: Optional[Tuple[float, float]] = None
    ) -> Dict[str, Any]:
        """
        Fetch FEMA flood zone data
        
        Args:
            bounds: Bounding box (minx, miny, maxx, maxy)
            property_location: Property center point (optional)
        
        Returns:
            Flood zone data
        """
        minx, miny, maxx, maxy = bounds
        
        # FEMA NFHL query
        query_url = f"{self.fema_base_url}/28/query"
        
        params = {
            'geometry': f"{minx},{miny},{maxx},{maxy}",
            'geometryType': 'esriGeometryEnvelope',
            'spatialRel': 'esriSpatialRelIntersects',
            'returnGeometry': 'true',
            'f': 'geojson',
            'outFields': '*'
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(query_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    'flood_zones': data.get('features', []),
                    'source': 'FEMA',
                    'bounds': bounds
                }
        except Exception as e:
            # Return empty if API fails
            return {
                'flood_zones': [],
                'source': 'FEMA',
                'error': str(e),
                'bounds': bounds
            }
    
    def fetch_wetlands(
        self,
        bounds: Tuple[float, float, float, float]
    ) -> Dict[str, Any]:
        """
        Fetch EPA/USFWS wetlands data
        
        Args:
            bounds: Bounding box
        
        Returns:
            Wetlands data
        """
        minx, miny, maxx, maxy = bounds
        
        query_url = f"{self.epa_wetlands_url}/0/query"
        
        params = {
            'geometry': f"{minx},{miny},{maxx},{maxy}",
            'geometryType': 'esriGeometryEnvelope',
            'spatialRel': 'esriSpatialRelIntersects',
            'returnGeometry': 'true',
            'f': 'geojson',
            'outFields': '*'
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(query_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    'wetlands': data.get('features', []),
                    'source': 'USFWS',
                    'bounds': bounds
                }
        except Exception as e:
            return {
                'wetlands': [],
                'source': 'USFWS',
                'error': str(e),
                'bounds': bounds
            }
    
    def fetch_topographic_data(
        self,
        bounds: Tuple[float, float, float, float]
    ) -> Dict[str, Any]:
        """
        Fetch USGS topographic data if not in uploaded file
        
        Args:
            bounds: Bounding box
        
        Returns:
            Topographic data
        """
        # USGS 3DEP Elevation service
        service_url = f"{self.usgs_base_url}/3DEPElevation/ImageServer"
        
        minx, miny, maxx, maxy = bounds
        
        params = {
            'bbox': f"{minx},{miny},{maxx},{maxy}",
            'size': '500,500',
            'format': 'tiff',
            'f': 'json'
        }
        
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(service_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    'topographic_data': data,
                    'source': 'USGS',
                    'bounds': bounds
                }
        except Exception as e:
            return {
                'topographic_data': None,
                'source': 'USGS',
                'error': str(e),
                'bounds': bounds
            }
    
    def fetch_all_regulatory_data(
        self,
        bounds: Tuple[float, float, float, float],
        property_location: Optional[Tuple[float, float]] = None
    ) -> Dict[str, Any]:
        """
        Fetch all available regulatory constraint data (with caching)
        
        Returns:
            Combined regulatory data
        """
        # Check cache first (cache by bounds - same location = cached)
        from utils.cache import get_cached, set_cached, generate_cache_key, CACHE_TTL_REGULATORY
        cache_key = generate_cache_key("regulatory_data", bounds, property_location)
        cached_result = get_cached(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Fetch data
        flood_zones = self.fetch_flood_zones(bounds, property_location)
        wetlands = self.fetch_wetlands(bounds)
        topographic = self.fetch_topographic_data(bounds)
        
        result = {
            'flood_zones': flood_zones,
            'wetlands': wetlands,
            'topographic': topographic,
            'bounds': bounds
        }
        
        # Cache for 24 hours (regulatory data changes rarely)
        set_cached(cache_key, result, ttl=CACHE_TTL_REGULATORY)
        return result
    
    def process_regulatory_constraints(
        self,
        regulatory_data: Dict[str, Any],
        property_boundary: Polygon
    ) -> Dict[str, Any]:
        """
        Process regulatory data into constraint polygons
        
        Args:
            regulatory_data: Fetched regulatory data
            property_boundary: Property boundary
        
        Returns:
            Processed constraints
        """
        constraints = {
            'flood_zones': [],
            'wetlands': [],
            'zoning': []
        }
        
        # Process flood zones
        flood_features = regulatory_data.get('flood_zones', {}).get('flood_zones', [])
        for feature in flood_features:
            geom = feature.get('geometry', {})
            props = feature.get('properties', {})
            
            # Convert to constraint
            constraints['flood_zones'].append({
                'geometry': geom,
                'type': props.get('FLD_ZONE', 'Unknown'),
                'severity': 'high' if 'A' in props.get('FLD_ZONE', '') or 'V' in props.get('FLD_ZONE', '') else 'medium',
                'buffer_distance': 200  # feet
            })
        
        # Process wetlands
        wetland_features = regulatory_data.get('wetlands', {}).get('wetlands', [])
        for feature in wetland_features:
            geom = feature.get('geometry', {})
            props = feature.get('properties', {})
            
            constraints['wetlands'].append({
                'geometry': geom,
                'type': props.get('WETLAND_TYPE', 'Unknown'),
                'severity': 'high',
                'buffer_distance': 300  # feet
            })
        
        return constraints

