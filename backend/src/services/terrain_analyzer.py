"""
Terrain analysis service for computing slope, aspect, and elevation metrics
"""
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
from shapely.geometry import Point, Polygon
import boto3
import json

# Optional rasterio import (requires GDAL)
try:
    import rasterio
    from rasterio.transform import from_bounds
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    rasterio = None
    from_bounds = None


class TerrainAnalyzer:
    """Analyze terrain from contour data"""
    
    def __init__(self, s3_client=None, cache_bucket: str = None):
        self.s3_client = s3_client or boto3.client('s3')
        self.cache_bucket = cache_bucket
    
    def generate_dem_from_contours(
        self,
        contours: List[Dict[str, Any]],
        bounds: Tuple[float, float, float, float],
        resolution: float = 10.0
    ) -> np.ndarray:
        """
        Generate Digital Elevation Model (DEM) from contour lines
        
        Args:
            contours: List of contour geometries with elevation data
            bounds: (minx, miny, maxx, maxy) bounding box
            resolution: Grid resolution in meters (default: 10m)
        
        Returns:
            2D numpy array representing DEM
        """
        minx, miny, maxx, maxy = bounds
        
        # Extract points from contours
        points = []
        values = []
        
        for contour in contours:
            geom = contour.get('geometry', {})
            elevation = contour.get('elevation')
            
            if elevation is None:
                continue
            
            if geom.get('type') == 'LineString':
                coords = geom.get('coordinates', [])
                for coord in coords:
                    points.append([coord[0], coord[1]])
                    values.append(elevation)
        
        if len(points) == 0:
            raise ValueError("No valid contour points found")
        
        points = np.array(points)
        values = np.array(values)
        
        # Create grid
        x = np.arange(minx, maxx, resolution)
        y = np.arange(miny, maxy, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Interpolate using cubic interpolation
        grid_points = np.column_stack([X.ravel(), Y.ravel()])
        Z = griddata(points, values, grid_points, method='cubic', fill_value=np.nan)
        Z = Z.reshape(X.shape)
        
        # Fill NaN values with nearest neighbor
        nan_mask = np.isnan(Z)
        if np.any(nan_mask):
            Z[nan_mask] = griddata(
                points, values,
                np.column_stack([X[nan_mask], Y[nan_mask]]),
                method='nearest'
            )
        
        # Smooth with Gaussian filter
        Z = gaussian_filter(Z, sigma=1.0)
        
        return Z, (minx, miny, maxx, maxy), resolution
    
    def calculate_slope(self, dem: np.ndarray, resolution: float) -> np.ndarray:
        """
        Calculate slope in degrees from DEM
        
        Args:
            dem: Digital elevation model array
            resolution: Grid resolution in same units as DEM (degrees or meters)
        
        Returns:
            Slope array in degrees
        """
        # Calculate gradients
        # If resolution is very small (< 0.001), assume it's in degrees and convert to meters
        # 1 degree ≈ 111,000 meters
        if resolution < 0.001:
            resolution_meters = resolution * 111000.0
        else:
            resolution_meters = resolution
        
        dy, dx = np.gradient(dem, resolution_meters)
        
        # Calculate slope in degrees
        slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
        slope_deg = np.degrees(slope_rad)
        
        return slope_deg
    
    def calculate_aspect(self, dem: np.ndarray, resolution: float) -> np.ndarray:
        """
        Calculate aspect (direction of steepest slope) in degrees
        
        Args:
            dem: Digital elevation model array
            resolution: Grid resolution in same units as DEM (degrees or meters)
        
        Returns:
            Aspect array in degrees (0-360, where 0 is North)
        """
        # Calculate gradients
        # If resolution is very small (< 0.001), assume it's in degrees and convert to meters
        # 1 degree ≈ 111,000 meters
        if resolution < 0.001:
            resolution_meters = resolution * 111000.0
        else:
            resolution_meters = resolution
        
        dy, dx = np.gradient(dem, resolution_meters)
        
        # Calculate aspect
        aspect_rad = np.arctan2(-dx, dy)
        aspect_deg = np.degrees(aspect_rad)
        
        # Convert to 0-360 range
        aspect_deg = np.where(aspect_deg < 0, aspect_deg + 360, aspect_deg)
        
        return aspect_deg
    
    def calculate_elevation_differentials(self, dem: np.ndarray) -> Dict[str, float]:
        """
        Calculate elevation statistics
        
        Args:
            dem: Digital elevation model array
        
        Returns:
            Dictionary with elevation statistics
        """
        return {
            'min': float(np.nanmin(dem)),
            'max': float(np.nanmax(dem)),
            'mean': float(np.nanmean(dem)),
            'std': float(np.nanstd(dem)),
            'range': float(np.nanmax(dem) - np.nanmin(dem))
        }
    
    def generate_hillshade(
        self,
        dem: np.ndarray,
        azimuth: float = 315.0,
        altitude: float = 45.0,
        resolution: float = 10.0
    ) -> np.ndarray:
        """
        Generate hillshade for visualization
        
        Args:
            dem: Digital elevation model array
            azimuth: Light source azimuth in degrees (default: 315 = NW)
            altitude: Light source altitude in degrees (default: 45)
            resolution: Grid resolution in meters (default: 10.0)
        
        Returns:
            Hillshade array (0-255)
        """
        # Calculate gradients
        # If resolution is very small (< 0.001), assume it's in degrees and convert to meters
        if resolution < 0.001:
            resolution_meters = resolution * 111000.0
        else:
            resolution_meters = resolution
        dy, dx = np.gradient(dem, resolution_meters)
        
        # Convert azimuth and altitude to radians
        azimuth_rad = np.radians(azimuth)
        altitude_rad = np.radians(altitude)
        
        # Calculate hillshade
        slope = np.arctan(np.sqrt(dx**2 + dy**2))
        aspect = np.arctan2(-dx, dy)
        
        hillshade = np.sin(altitude_rad) * np.sin(slope) + \
                   np.cos(altitude_rad) * np.cos(slope) * \
                   np.cos(azimuth_rad - aspect)
        
        # Normalize to 0-255
        hillshade = (hillshade + 1) / 2 * 255
        hillshade = np.clip(hillshade, 0, 255)
        
        return hillshade.astype(np.uint8)
    
    def analyze_terrain(
        self,
        contours: List[Dict[str, Any]],
        bounds: Tuple[float, float, float, float],
        resolution: float = 10.0
    ) -> Dict[str, Any]:
        """
        Complete terrain analysis
        
        Args:
            contours: List of contour geometries
            bounds: Bounding box (minx, miny, maxx, maxy)
            resolution: Grid resolution in meters
        
        Returns:
            Dictionary with all terrain metrics
        """
        # Generate DEM
        dem, dem_bounds, dem_resolution = self.generate_dem_from_contours(
            contours, bounds, resolution
        )
        
        # Calculate metrics
        slope = self.calculate_slope(dem, dem_resolution)
        aspect = self.calculate_aspect(dem, dem_resolution)
        elevation_stats = self.calculate_elevation_differentials(dem)
        hillshade = self.generate_hillshade(dem, resolution=dem_resolution)
        
        # For large arrays, only return stats and references
        # Store full arrays in S3 if needed (for demo, return summary only)
        dem_size = dem.shape
        slope_size = slope.shape
        
        # Only serialize if arrays are small (< 100x100), otherwise return stats only
        if dem_size[0] * dem_size[1] < 10000:  # 100x100 = 10k points
            return {
                'dem': dem.tolist(),
                'dem_bounds': dem_bounds,
                'dem_resolution': dem_resolution,
                'slope': slope.tolist(),
                'aspect': aspect.tolist(),
                'elevation_stats': elevation_stats,
                'hillshade': hillshade.tolist(),
                'bounds': bounds
            }
        else:
            # Large arrays - return summary only, store full data in S3
            return {
                'dem': None,  # Too large, stored in S3
                'dem_bounds': dem_bounds,
                'dem_resolution': dem_resolution,
                'slope': None,  # Too large
                'aspect': None,  # Too large
                'elevation_stats': elevation_stats,
                'slope_stats': {
                    'min': float(np.nanmin(slope)),
                    'max': float(np.nanmax(slope)),
                    'mean': float(np.nanmean(slope))
                },
                'aspect_stats': {
                    'mean': float(np.nanmean(aspect))
                },
                'hillshade': None,  # Too large
                'bounds': bounds,
                'note': 'Large arrays stored in S3 - use /terrain-data/{file_id} to fetch'
            }
    
    def get_terrain_suitability_score(
        self,
        point: Tuple[float, float],
        slope: np.ndarray,
        aspect: np.ndarray,
        dem: np.ndarray,
        bounds: Tuple[float, float, float, float],
        resolution: float
    ) -> float:
        """
        Calculate terrain suitability score for a point (0-1, higher is better)
        
        Args:
            point: (x, y) coordinates
            slope: Slope array
            aspect: Aspect array
            dem: DEM array
            bounds: Bounding box
            resolution: Grid resolution
        
        Returns:
            Suitability score (0-1)
        """
        minx, miny, maxx, maxy = bounds
        x, y = point
        
        # Check if point is within bounds
        if not (minx <= x <= maxx and miny <= y <= maxy):
            return 0.0
        
        # Convert point to grid indices
        i = int((y - miny) / resolution)
        j = int((x - minx) / resolution)
        
        if i < 0 or i >= slope.shape[0] or j < 0 or j >= slope.shape[1]:
            return 0.0
        
        # Get terrain values at point
        point_slope = slope[i, j]
        point_aspect = aspect[i, j]
        
        # Score based on slope (prefer flatter areas, max 15% slope)
        if point_slope > 15:
            slope_score = 0.0
        else:
            slope_score = 1.0 - (point_slope / 15.0)
        
        # Aspect score (prefer south-facing for energy, but less critical)
        # Normalize to 0-1 (south = 180 degrees)
        aspect_diff = abs(point_aspect - 180)
        if aspect_diff > 180:
            aspect_diff = 360 - aspect_diff
        aspect_score = 1.0 - (aspect_diff / 180.0)
        
        # Combined score (slope is more important)
        suitability = 0.8 * slope_score + 0.2 * aspect_score
        
        return float(suitability)

