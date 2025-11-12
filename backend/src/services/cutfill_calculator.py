"""
Cut/fill volume calculator using grid method
"""
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from shapely.geometry import Polygon, Point
import json


class CutFillCalculator:
    """Calculate earthwork volumes (cut, fill, net)"""
    
    def __init__(self, grid_resolution: float = 10.0):
        # grid_resolution is in feet, but we'll convert to degrees when working with coordinates
        self.grid_resolution = grid_resolution  # feet
        self.FEET_TO_DEGREES = 1.0 / 364000.0
    
    def calculate_volumes(
        self,
        dem: np.ndarray,
        proposed_grades: Dict[str, Any],
        bounds: Tuple[float, float, float, float],
        property_boundary: Optional[Polygon] = None
    ) -> Dict[str, Any]:
        """
        Calculate cut/fill volumes using grid method
        
        Args:
            dem: Existing elevation model (2D array)
            proposed_grades: Proposed grade elevations
            bounds: DEM bounds (minx, miny, maxx, maxy)
            property_boundary: Property boundary (optional, for masking)
        
        Returns:
            Dictionary with volume calculations and breakdowns
        """
        minx, miny, maxx, maxy = bounds
        
        # Create proposed elevation grid
        proposed_dem = self._create_proposed_dem(
            proposed_grades,
            dem.shape,
            bounds
        )
        
        # Calculate cut and fill for each grid cell
        cut_volumes = np.zeros_like(dem)
        fill_volumes = np.zeros_like(dem)
        
        for i in range(dem.shape[0]):
            for j in range(dem.shape[1]):
                existing_elev = dem[i, j]
                proposed_elev = proposed_dem[i, j]
                
                # Check if point is within property boundary
                # Convert grid_resolution from feet to degrees
                if property_boundary:
                    grid_res_deg = self.grid_resolution * self.FEET_TO_DEGREES
                    x = minx + j * grid_res_deg
                    y = miny + i * grid_res_deg
                    if not property_boundary.contains(Point(x, y)):
                        continue
                
                # Calculate cut (material to remove)
                if proposed_elev < existing_elev:
                    cut_volumes[i, j] = existing_elev - proposed_elev
                
                # Calculate fill (material to add)
                elif proposed_elev > existing_elev:
                    fill_volumes[i, j] = proposed_elev - existing_elev
        
        # Calculate volumes (cubic feet)
        cell_area = self.grid_resolution * self.grid_resolution  # square feet
        total_cut = np.sum(cut_volumes) * cell_area  # cubic feet
        total_fill = np.sum(fill_volumes) * cell_area  # cubic feet
        net_volume = total_cut - total_fill  # cubic feet
        
        # Convert to cubic yards (standard unit)
        total_cut_yd3 = total_cut / 27.0
        total_fill_yd3 = total_fill / 27.0
        net_volume_yd3 = net_volume / 27.0
        
        # Calculate by area (if property boundary provided)
        area_breakdown = {}
        if property_boundary:
            total_area = property_boundary.area  # square feet
            area_breakdown = {
                'total_area_sqft': total_area,
                'total_area_acres': total_area / 43560.0,
                'cut_per_acre_yd3': total_cut_yd3 / (total_area / 43560.0) if total_area > 0 else 0,
                'fill_per_acre_yd3': total_fill_yd3 / (total_area / 43560.0) if total_area > 0 else 0
            }
        
        return {
            'cut_volume_ft3': float(total_cut),
            'fill_volume_ft3': float(total_fill),
            'net_volume_ft3': float(net_volume),
            'cut_volume_yd3': float(total_cut_yd3),
            'fill_volume_yd3': float(total_fill_yd3),
            'net_volume_yd3': float(net_volume_yd3),
            'area_breakdown': area_breakdown,
            'cut_map': cut_volumes.tolist(),
            'fill_map': fill_volumes.tolist(),
            'grid_resolution': self.grid_resolution,
            'bounds': bounds
        }
    
    def _create_proposed_dem(
        self,
        proposed_grades: Dict[str, Any],
        dem_shape: Tuple[int, int],
        bounds: Tuple[float, float, float, float]
    ) -> np.ndarray:
        """
        Create proposed elevation model from layout
        
        Args:
            proposed_grades: Proposed grade elevations (assets, roads, pads)
            dem_shape: Shape of existing DEM
            bounds: DEM bounds
        
        Returns:
            Proposed DEM array
        """
        proposed_dem = np.zeros(dem_shape)
        minx, miny, maxx, maxy = bounds
        
        # Default proposed elevation (match existing or specified)
        default_elevation = proposed_grades.get('default_elevation', None)
        if default_elevation:
            proposed_dem.fill(default_elevation)
        else:
            # Use existing DEM as baseline
            proposed_dem = proposed_grades.get('baseline_dem', proposed_dem)
        
        # Apply asset pad elevations
        assets = proposed_grades.get('assets', [])
        for asset in assets:
            x = asset.get('x', 0)
            y = asset.get('y', 0)
            pad_elevation = asset.get('pad_elevation', None)
            pad_size = asset.get('pad_size', 50)  # feet
            
            if pad_elevation:
                # Set elevation in area around asset
                # Convert grid_resolution and pad_size from feet to degrees
                grid_res_deg = self.grid_resolution * self.FEET_TO_DEGREES
                pad_size_deg = pad_size * self.FEET_TO_DEGREES
                i = int((y - miny) / grid_res_deg)
                j = int((x - minx) / grid_res_deg)
                pad_radius = int(pad_size_deg / grid_res_deg)
                
                for di in range(-pad_radius, pad_radius + 1):
                    for dj in range(-pad_radius, pad_radius + 1):
                        ni, nj = i + di, j + dj
                        if 0 <= ni < dem_shape[0] and 0 <= nj < dem_shape[1]:
                            proposed_dem[ni, nj] = pad_elevation
        
        # Apply road grades
        roads = proposed_grades.get('roads', [])
        for road in roads:
            centerline = road.get('centerline', [])
            road_width = road.get('width', 20)
            road_elevations = road.get('elevations', [])
            
            # Interpolate road elevations along centerline
            for idx, point in enumerate(centerline):
                x, y = point
                if idx < len(road_elevations):
                    elevation = road_elevations[idx]
                else:
                    elevation = default_elevation if default_elevation else 0
                
                # Set elevation in road right-of-way
                # Convert grid_resolution and road_width from feet to degrees
                grid_res_deg = self.grid_resolution * self.FEET_TO_DEGREES
                road_width_deg = road_width * self.FEET_TO_DEGREES
                i = int((y - miny) / grid_res_deg)
                j = int((x - minx) / grid_res_deg)
                road_radius = int(road_width_deg / (2 * grid_res_deg))
                
                for di in range(-road_radius, road_radius + 1):
                    for dj in range(-road_radius, road_radius + 1):
                        ni, nj = i + di, j + dj
                        if 0 <= ni < dem_shape[0] and 0 <= nj < dem_shape[1]:
                            proposed_dem[ni, nj] = elevation
        
        return proposed_dem
    
    def generate_visualization_map(
        self,
        cut_map: np.ndarray,
        fill_map: np.ndarray,
        bounds: Tuple[float, float, float, float]
    ) -> Dict[str, Any]:
        """
        Generate visualization map for cut/fill areas
        
        Returns:
            Dictionary with visualization data
        """
        # Create color-coded map
        # 0 = no change, 1 = cut, 2 = fill, 3 = balanced
        visualization = np.zeros_like(cut_map)
        
        cut_areas = cut_map > 0
        fill_areas = fill_map > 0
        
        visualization[cut_areas] = 1  # Cut areas
        visualization[fill_areas] = 2  # Fill areas
        
        # Balanced areas (where cut and fill are similar)
        balanced_threshold = 0.1  # feet
        balanced = np.abs(cut_map - fill_map) < balanced_threshold
        visualization[balanced] = 3
        
        return {
            'visualization': visualization.tolist(),
            'bounds': bounds,
            'legend': {
                '0': 'No change',
                '1': 'Cut area',
                '2': 'Fill area',
                '3': 'Balanced area'
            }
        }

