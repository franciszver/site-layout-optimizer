"""
Generate demo property data for testing and demonstration
"""
import json
import random
from typing import Dict, Any, List, Tuple
from shapely.geometry import Polygon, Point, LineString
import numpy as np


class DemoDataGenerator:
    """Generate realistic demo properties"""
    
    def generate_flat_terrain_property(
        self,
        center: Tuple[float, float] = (-98.5795, 39.8283),
        size_acres: float = 150.0
    ) -> Dict[str, Any]:
        """Generate flat terrain property (100-200 acres)"""
        # Convert acres to approximate square feet
        size_ft = np.sqrt(size_acres * 43560)  # Approximate side length
        
        # Create square property
        half_size = size_ft / 2 / 111000  # Rough conversion to degrees
        minx = center[0] - half_size
        maxx = center[0] + half_size
        miny = center[1] - half_size
        maxy = center[1] + half_size
        
        boundary = [
            [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]]
        ]
        
        # Generate flat terrain contours
        base_elevation = 1000.0
        contours = []
        for i in range(5):
            for j in range(5):
                x = minx + (maxx - minx) * i / 4
                y = miny + (maxy - miny) * j / 4
                elevation = base_elevation + random.uniform(-2, 2)
                contours.append({
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [
                            [x - 0.001, y],
                            [x + 0.001, y]
                        ]
                    },
                    'elevation': elevation
                })
        
        return {
            'name': 'Flat Terrain Property',
            'description': 'Demo property with relatively flat terrain',
            'boundary': boundary,
            'contours': contours,
            'exclusion_zones': [],
            'entry_point': [center[0], center[1] - half_size * 0.8],
            'size_acres': size_acres
        }
    
    def generate_hilly_terrain_property(
        self,
        center: Tuple[float, float] = (-98.5795, 39.8283),
        size_acres: float = 250.0
    ) -> Dict[str, Any]:
        """Generate hilly terrain property (200-300 acres)"""
        size_ft = np.sqrt(size_acres * 43560)
        half_size = size_ft / 2 / 111000
        
        minx = center[0] - half_size
        maxx = center[0] + half_size
        miny = center[1] - half_size
        maxy = center[1] + half_size
        
        boundary = [
            [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]]
        ]
        
        # Generate hilly terrain contours with elevation variation
        base_elevation = 1000.0
        contours = []
        for i in range(8):
            for j in range(8):
                x = minx + (maxx - minx) * i / 7
                y = miny + (maxy - miny) * j / 7
                # Create elevation variation (hills)
                elevation = base_elevation + 50 * np.sin(i * np.pi / 4) * np.cos(j * np.pi / 4) + random.uniform(-5, 5)
                contours.append({
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [
                            [x - 0.001, y],
                            [x + 0.001, y]
                        ]
                    },
                    'elevation': elevation
                })
        
        # Add some exclusion zones (steep slopes)
        exclusion_zones = [
            {
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[
                        [center[0] - half_size * 0.3, center[1] - half_size * 0.3],
                        [center[0] - half_size * 0.2, center[1] - half_size * 0.3],
                        [center[0] - half_size * 0.2, center[1] - half_size * 0.2],
                        [center[0] - half_size * 0.3, center[1] - half_size * 0.2],
                        [center[0] - half_size * 0.3, center[1] - half_size * 0.3]
                    ]]
                },
                'type': 'steep_slope'
            }
        ]
        
        return {
            'name': 'Hilly Terrain Property',
            'description': 'Demo property with varied terrain and elevation changes',
            'boundary': boundary,
            'contours': contours,
            'exclusion_zones': exclusion_zones,
            'entry_point': [center[0], center[1] - half_size * 0.8],
            'size_acres': size_acres
        }
    
    def generate_constrained_property(
        self,
        center: Tuple[float, float] = (-98.5795, 39.8283),
        size_acres: float = 350.0
    ) -> Dict[str, Any]:
        """Generate constrained property with exclusion zones and regulatory constraints"""
        size_ft = np.sqrt(size_acres * 43560)
        half_size = size_ft / 2 / 111000
        
        minx = center[0] - half_size
        maxx = center[0] + half_size
        miny = center[1] - half_size
        maxy = center[1] + half_size
        
        boundary = [
            [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]]
        ]
        
        # Generate terrain with constraints
        base_elevation = 1000.0
        contours = []
        for i in range(10):
            for j in range(10):
                x = minx + (maxx - minx) * i / 9
                y = miny + (maxy - miny) * j / 9
                elevation = base_elevation + 30 * np.sin(i * np.pi / 5) + random.uniform(-3, 3)
                contours.append({
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [
                            [x - 0.001, y],
                            [x + 0.001, y]
                        ]
                    },
                    'elevation': elevation
                })
        
        # Multiple exclusion zones
        exclusion_zones = [
            {
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[
                        [center[0] - half_size * 0.4, center[1] - half_size * 0.4],
                        [center[0] - half_size * 0.2, center[1] - half_size * 0.4],
                        [center[0] - half_size * 0.2, center[1] - half_size * 0.2],
                        [center[0] - half_size * 0.4, center[1] - half_size * 0.2],
                        [center[0] - half_size * 0.4, center[1] - half_size * 0.4]
                    ]]
                },
                'type': 'wetland'
            },
            {
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[
                        [center[0] + half_size * 0.2, center[1] + half_size * 0.2],
                        [center[0] + half_size * 0.4, center[1] + half_size * 0.2],
                        [center[0] + half_size * 0.4, center[1] + half_size * 0.4],
                        [center[0] + half_size * 0.2, center[1] + half_size * 0.4],
                        [center[0] + half_size * 0.2, center[1] + half_size * 0.2]
                    ]]
                },
                'type': 'flood_zone'
            }
        ]
        
        return {
            'name': 'Constrained Property',
            'description': 'Demo property with multiple exclusion zones and regulatory constraints',
            'boundary': boundary,
            'contours': contours,
            'exclusion_zones': exclusion_zones,
            'entry_point': [center[0], center[1] - half_size * 0.8],
            'size_acres': size_acres,
            'regulatory_constraints': {
                'flood_zones': True,
                'wetlands': True,
                'zoning': 'Industrial'
            }
        }

