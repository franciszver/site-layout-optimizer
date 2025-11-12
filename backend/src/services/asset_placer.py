"""
Asset placement engine with constraint checking and multi-criteria ranking
"""
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config_loader import ConfigLoader
from services.terrain_analyzer import TerrainAnalyzer


class AssetPlacer:
    """Place assets within property boundaries respecting constraints"""
    
    def __init__(self):
        self.config_loader = ConfigLoader()
        self.terrain_analyzer = TerrainAnalyzer()
    
    def generate_candidate_locations(
        self,
        property_boundary: Polygon,
        exclusion_zones: List[Polygon],
        grid_resolution: float = 10.0,
        buffer_boundary: float = 50.0,
        buffer_exclusion: float = 100.0
    ) -> List[Tuple[float, float]]:
        """
        Generate grid of candidate placement locations
        
        Args:
            property_boundary: Property boundary polygon
            exclusion_zones: List of exclusion zone polygons
            grid_resolution: Grid spacing in feet (will be converted to degrees)
            buffer_boundary: Buffer distance from boundary in feet (will be converted to degrees)
            buffer_exclusion: Buffer distance from exclusion zones in feet (will be converted to degrees)
        
        Returns:
            List of (x, y) candidate locations
        """
        # Convert feet to degrees (approximate: 1 degree ≈ 111,000 meters ≈ 364,000 feet)
        # For more accuracy, we'd need to use a proper projection, but for demo this works
        FEET_TO_DEGREES = 1.0 / 364000.0
        
        buffer_boundary_deg = buffer_boundary * FEET_TO_DEGREES
        buffer_exclusion_deg = buffer_exclusion * FEET_TO_DEGREES
        grid_resolution_deg = grid_resolution * FEET_TO_DEGREES
        
        # Create buffered boundary (interior buffer)
        # Use a smaller buffer to avoid collapsing small polygons
        try:
            buffered_boundary = property_boundary.buffer(-buffer_boundary_deg)
            if buffered_boundary.is_empty or not buffered_boundary.is_valid:
                # If buffer collapses polygon, use original with smaller buffer
                buffered_boundary = property_boundary.buffer(-buffer_boundary_deg * 0.1)
                if buffered_boundary.is_empty:
                    buffered_boundary = property_boundary  # Fallback to original
        except Exception as e:
            print(f"Warning: Buffer failed, using original boundary: {e}")
            buffered_boundary = property_boundary
        
        # Create buffered exclusion zones
        buffered_exclusions = []
        for zone in exclusion_zones:
            try:
                buffered_exclusions.append(zone.buffer(buffer_exclusion_deg))
            except Exception:
                buffered_exclusions.append(zone)
        
        # Combine exclusion zones
        if buffered_exclusions:
            try:
                exclusion_union = unary_union(buffered_exclusions)
            except Exception:
                exclusion_union = None
        else:
            exclusion_union = None
        
        # Get bounding box
        try:
            minx, miny, maxx, maxy = buffered_boundary.bounds
        except Exception:
            minx, miny, maxx, maxy = property_boundary.bounds
        
        # Calculate approximate area to limit candidates
        bbox_width_deg = maxx - minx
        bbox_height_deg = maxy - miny
        estimated_points = int((bbox_width_deg / grid_resolution_deg) * (bbox_height_deg / grid_resolution_deg))
        
        # Limit to reasonable number of candidates (max 10,000 for performance)
        MAX_CANDIDATES = 10000
        if estimated_points > MAX_CANDIDATES:
            # Increase grid resolution to reduce candidates
            scale_factor = (estimated_points / MAX_CANDIDATES) ** 0.5
            grid_resolution_deg = grid_resolution_deg * scale_factor
            print(f"Adjusted grid resolution to {grid_resolution_deg * 364000:.1f}ft to limit candidates (estimated {estimated_points} points)")
        
        # Generate grid points
        candidates = []
        x = minx
        while x <= maxx:
            y = miny
            while y <= maxy:
                point = Point(x, y)
                
                # Check if point is within buffered boundary
                try:
                    if buffered_boundary.contains(point):
                        # Check if point is not in exclusion zones
                        if exclusion_union is None or not exclusion_union.contains(point):
                            candidates.append((x, y))
                            
                            # Safety limit check
                            if len(candidates) >= MAX_CANDIDATES:
                                print(f"Reached maximum candidate limit ({MAX_CANDIDATES}), stopping grid generation")
                                return candidates
                except Exception:
                    pass  # Skip invalid points
                
                y += grid_resolution_deg
            x += grid_resolution_deg
        
        print(f"Generated {len(candidates)} candidate locations")
        return candidates
    
    def check_constraints(
        self,
        location: Tuple[float, float],
        asset_type: Dict[str, Any],
        property_boundary: Polygon,
        exclusion_zones: List[Polygon],
        placed_assets: List[Dict[str, Any]],
        constraints: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Check if location satisfies all constraints
        
        Returns:
            (is_valid, violation_messages)
        """
        violations = []
        x, y = location
        
        # Get asset dimensions (in feet, convert to degrees)
        FEET_TO_DEGREES = 1.0 / 364000.0
        dims = asset_type.get('dimensions', {})
        length_ft = dims.get('length', 0)
        width_ft = dims.get('width', 0)
        
        # Convert to degrees
        length_deg = length_ft * FEET_TO_DEGREES
        width_deg = width_ft * FEET_TO_DEGREES
        
        # Create asset footprint
        half_length = length_deg / 2
        half_width = width_deg / 2
        asset_footprint = box(
            x - half_length, y - half_width,
            x + half_length, y + half_width
        )
        
        # Check boundary constraint
        buffer_boundary = constraints.get('buffer_boundary', 50)
        buffer_boundary_deg = buffer_boundary * FEET_TO_DEGREES
        try:
            buffered_boundary = property_boundary.buffer(-buffer_boundary_deg)
            if buffered_boundary.is_empty:
                buffered_boundary = property_boundary
        except Exception:
            buffered_boundary = property_boundary
        
        if not buffered_boundary.contains(asset_footprint):
            violations.append("Asset extends beyond property boundary buffer")
        
        # Check exclusion zone constraint
        buffer_exclusion = constraints.get('buffer_exclusion', 100)
        buffer_exclusion_deg = buffer_exclusion * FEET_TO_DEGREES
        for zone in exclusion_zones:
            try:
                buffered_zone = zone.buffer(buffer_exclusion_deg)
                if buffered_zone.intersects(asset_footprint):
                    violations.append("Asset violates exclusion zone buffer")
            except Exception:
                # If buffering fails, check intersection with original zone
                if zone.intersects(asset_footprint):
                    violations.append("Asset violates exclusion zone buffer")
        
        # Check spacing constraint
        min_spacing = constraints.get('min_spacing', 50)
        min_spacing_deg = min_spacing * FEET_TO_DEGREES
        for placed in placed_assets:
            placed_x = placed.get('x', 0)
            placed_y = placed.get('y', 0)
            distance = Point(x, y).distance(Point(placed_x, placed_y))
            if distance < min_spacing_deg:
                violations.append(f"Asset too close to existing asset (distance: {distance*364000:.1f}ft)")
        
        return len(violations) == 0, violations
    
    def calculate_location_score(
        self,
        location: Tuple[float, float],
        asset_type: Dict[str, Any],
        property_boundary: Polygon,
        entry_point: Tuple[float, float],
        terrain_data: Optional[Dict[str, Any]] = None,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate multi-criteria score for a location (0-1, higher is better)
        
        Args:
            location: (x, y) coordinates
            asset_type: Asset type configuration
            property_boundary: Property boundary
            entry_point: Property entry point
            terrain_data: Terrain analysis data (optional)
            weights: Scoring weights (optional)
        
        Returns:
            Combined suitability score (0-1)
        """
        if weights is None:
            weights = {
                'terrain_suitability': 0.4,
                'distance_to_entry': 0.2,
                'constraint_compliance': 0.3,
                'spacing_optimization': 0.1
            }
        
        scores = {}
        
        # Terrain suitability score
        if terrain_data:
            slope = terrain_data.get('slope', None)
            aspect = terrain_data.get('aspect', None)
            dem = terrain_data.get('dem', None)
            bounds = terrain_data.get('bounds', None)
            resolution = terrain_data.get('dem_resolution', 10.0)
            
            # Check if terrain arrays are available (handle None for large arrays)
            if all([slope is not None, aspect is not None, dem is not None, bounds]):
                # Convert to numpy arrays if they're lists
                slope_arr = np.array(slope) if isinstance(slope, list) else slope
                aspect_arr = np.array(aspect) if isinstance(aspect, list) else aspect
                dem_arr = np.array(dem) if isinstance(dem, list) else dem
                
                terrain_score = self.terrain_analyzer.get_terrain_suitability_score(
                    location, slope_arr, aspect_arr,
                    dem_arr, bounds, resolution
                )
            else:
                terrain_score = 0.5  # Default if terrain data unavailable (large arrays not serialized)
        else:
            terrain_score = 0.5
        
        scores['terrain_suitability'] = terrain_score
        
        # Distance to entry score (closer is better, but normalize)
        max_distance = property_boundary.bounds[2] - property_boundary.bounds[0]  # Approximate
        distance = Point(location).distance(Point(entry_point))
        distance_score = 1.0 - min(distance / max_distance, 1.0)
        scores['distance_to_entry'] = distance_score
        
        # Constraint compliance (assume valid if we're checking this location)
        scores['constraint_compliance'] = 1.0
        
        # Spacing optimization (will be calculated with other assets)
        scores['spacing_optimization'] = 0.5
        
        # Weighted combination
        total_score = sum(weights[key] * scores[key] for key in weights)
        
        return total_score
    
    def place_assets(
        self,
        property_boundary: Polygon,
        exclusion_zones: List[Polygon],
        asset_requirements: List[Dict[str, Any]],
        entry_point: Tuple[float, float],
        terrain_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Place assets using greedy algorithm with multi-criteria ranking
        
        Args:
            property_boundary: Property boundary polygon
            exclusion_zones: List of exclusion zone polygons
            asset_requirements: List of asset requirements (type, count, etc.)
            entry_point: Property entry point
            terrain_data: Terrain analysis data
        
        Returns:
            List of placed assets with locations and metadata
        """
        placed_assets = []
        constraints = self.config_loader.get_constraints()
        
        # Get default constraints
        buffer_boundary = constraints.get('boundary_constraints', {}).get('buffer_distance', 50)
        buffer_exclusion = constraints.get('exclusion_zone_constraints', {}).get('buffer_distance', 100)
        min_spacing = constraints.get('spacing_constraints', {}).get('min_asset_spacing', 50)
        
        constraint_config = {
            'buffer_boundary': buffer_boundary,
            'buffer_exclusion': buffer_exclusion,
            'min_spacing': min_spacing
        }
        
        # Process each asset requirement
        for req in asset_requirements:
            asset_name = req.get('type')
            count = req.get('count', 1)
            
            print(f"Processing asset requirement: {asset_name} x {count}")
            
            # Get asset type configuration
            asset_type = self.config_loader.get_asset_type(asset_name)
            if not asset_type:
                print(f"Warning: Unknown asset type '{asset_name}', skipping")
                continue  # Skip unknown asset types
            
            # Generate candidate locations
            candidates = self.generate_candidate_locations(
                property_boundary,
                exclusion_zones,
                grid_resolution=10.0,
                buffer_boundary=buffer_boundary,
                buffer_exclusion=buffer_exclusion
            )
            
            print(f"Found {len(candidates)} candidate locations for {asset_name}")
            
            if len(candidates) == 0:
                print(f"Warning: No candidate locations found for {asset_name}")
                # Fallback: place at property center if no candidates
                try:
                    center = property_boundary.centroid
                    candidates = [(center.x, center.y)]
                    print(f"Using property center as fallback: {candidates[0]}")
                except Exception as e:
                    print(f"Error getting property center: {e}")
                    continue
            
            # Score and rank candidates
            scored_candidates = []
            for candidate in candidates:
                # Check constraints
                is_valid, violations = self.check_constraints(
                    candidate, asset_type, property_boundary,
                    exclusion_zones, placed_assets, constraint_config
                )
                
                if is_valid:
                    # Calculate score
                    score = self.calculate_location_score(
                        candidate, asset_type, property_boundary,
                        entry_point, terrain_data
                    )
                    scored_candidates.append((candidate, score))
            
            print(f"Found {len(scored_candidates)} valid candidates for {asset_name}")
            
            # Sort by score (highest first)
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            
            # Place assets (greedy selection)
            placed_count = 0
            for candidate, score in scored_candidates:
                if placed_count >= count:
                    break
                
                x, y = candidate
                placed_assets.append({
                    'type': asset_name,
                    'x': x,
                    'y': y,
                    'score': score,
                    'dimensions': asset_type.get('dimensions', {}),
                    'attributes': asset_type.get('attributes', {})
                })
                placed_count += 1
                print(f"Placed {asset_name} at ({x:.6f}, {y:.6f}) with score {score:.3f}")
        
        print(f"Total assets placed: {len(placed_assets)}")
        return placed_assets

