"""
Road network generator using A* pathfinding with terrain cost weighting
"""
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
import heapq


class RoadGenerator:
    """Generate road networks connecting entry point to assets"""
    
    def __init__(self):
        self.max_grade = 8.0  # percent
        self.min_width_access = 20.0  # feet
        self.min_width_secondary = 12.0  # feet
        self.min_turning_radius = 25.0  # feet
        self.avoid_slope_above = 15.0  # percent
    
    def calculate_grade(
        self,
        point1: Tuple[float, float, float],
        point2: Tuple[float, float, float]
    ) -> float:
        """
        Calculate road grade between two points
        
        Args:
            point1: (x, y, elevation)
            point2: (x, y, elevation)
        
        Returns:
            Grade in percent
        """
        x1, y1, z1 = point1
        x2, y2, z2 = point2
        
        # Calculate horizontal distance
        horizontal_dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        if horizontal_dist == 0:
            return 0.0
        
        # Calculate vertical change
        vertical_change = z2 - z1
        
        # Grade as percent
        grade = (vertical_change / horizontal_dist) * 100.0
        
        return grade
    
    def get_elevation_at_point(
        self,
        point: Tuple[float, float],
        dem: np.ndarray,
        bounds: Tuple[float, float, float, float],
        resolution: float
    ) -> float:
        """Get elevation at a point from DEM"""
        minx, miny, maxx, maxy = bounds
        x, y = point
        
        # Convert to grid indices
        i = int((y - miny) / resolution)
        j = int((x - minx) / resolution)
        
        if i < 0 or i >= dem.shape[0] or j < 0 or j >= dem.shape[1]:
            return 0.0
        
        return float(dem[i, j])
    
    def a_star_pathfinding(
        self,
        start: Tuple[float, float],
        goal: Tuple[float, float],
        property_boundary: Polygon,
        exclusion_zones: List[Polygon],
        dem: Optional[np.ndarray] = None,
        bounds: Optional[Tuple[float, float, float, float]] = None,
        resolution: float = 10.0
    ) -> Optional[List[Tuple[float, float]]]:
        """
        A* pathfinding with terrain cost weighting
        
        Args:
            start: Start point (x, y)
            goal: Goal point (x, y)
            property_boundary: Property boundary
            exclusion_zones: Exclusion zones to avoid
            dem: Digital elevation model (optional)
            bounds: DEM bounds (optional)
            resolution: Grid resolution
        
        Returns:
            Path as list of (x, y) points, or None if no path found
        """
        # Convert resolution from feet to degrees if needed
        # If resolution is very small (< 0.001), assume it's already in degrees
        # Otherwise, assume it's in feet and convert
        FEET_TO_DEGREES = 1.0 / 364000.0
        if resolution > 0.001:
            # Likely in feet, convert to degrees
            grid_size = resolution * FEET_TO_DEGREES
        else:
            # Already in degrees
            grid_size = resolution
        
        # Create grid for pathfinding
        minx, miny, maxx, maxy = property_boundary.bounds
        
        # Heuristic function (Euclidean distance)
        def heuristic(a: Tuple[float, float], b: Tuple[float, float]) -> float:
            return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
        
        # Cost function with terrain weighting
        def cost(current: Tuple[float, float], next_point: Tuple[float, float]) -> float:
            # Base distance cost
            distance = heuristic(current, next_point)
            
            # Check if point is in exclusion zones
            point = Point(next_point)
            for zone in exclusion_zones:
                if zone.contains(point):
                    return float('inf')  # Infinite cost for exclusion zones
            
            # Terrain cost (if DEM available)
            terrain_cost = 1.0
            if dem is not None and bounds is not None:
                # Get elevation at both points
                elev_current = self.get_elevation_at_point(current, dem, bounds, resolution)
                elev_next = self.get_elevation_at_point(next_point, dem, bounds, resolution)
                
                # Calculate grade
                grade = self.calculate_grade(
                    (*current, elev_current),
                    (*next_point, elev_next)
                )
                
                # Penalize steep grades
                if abs(grade) > self.max_grade:
                    terrain_cost = 10.0  # High penalty
                elif abs(grade) > self.avoid_slope_above:
                    terrain_cost = 5.0  # Medium penalty
                else:
                    # Slight penalty for any grade
                    terrain_cost = 1.0 + abs(grade) / 10.0
            
            return distance * terrain_cost
        
        # Validate start and goal are within boundary
        if not property_boundary.contains(Point(start)):
            print(f"WARNING: Start point {start} is not within property boundary")
            # Try to find nearest point within boundary
            start_point = Point(start)
            if not property_boundary.contains(start_point):
                # Use boundary centroid as fallback
                start = tuple(property_boundary.centroid.coords[0])
                print(f"Using boundary centroid as start: {start}")
        
        if not property_boundary.contains(Point(goal)):
            print(f"WARNING: Goal point {goal} is not within property boundary")
            # Try to find nearest point within boundary
            goal_point = Point(goal)
            if not property_boundary.contains(goal_point):
                # Use boundary centroid as fallback
                goal = tuple(property_boundary.centroid.coords[0])
                print(f"Using boundary centroid as goal: {goal}")
        
        print(f"A* pathfinding: start={start}, goal={goal}, grid_size={grid_size}")
        
        # A* algorithm
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        
        visited = set()
        max_iterations = 10000  # Prevent infinite loops
        iterations = 0
        
        while open_set and iterations < max_iterations:
            iterations += 1
            current_f, current = heapq.heappop(open_set)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            # Check if reached goal (use a larger threshold for small grid sizes)
            goal_threshold = max(grid_size * 2, 0.0001)  # At least 0.0001 degrees
            if heuristic(current, goal) < goal_threshold:
                # Reconstruct path
                path = [goal]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                print(f"Path found after {iterations} iterations, {len(path)} points")
                return path
            
            # Explore neighbors
            for dx in [-grid_size, 0, grid_size]:
                for dy in [-grid_size, 0, grid_size]:
                    if dx == 0 and dy == 0:
                        continue
                    
                    neighbor = (current[0] + dx, current[1] + dy)
                    
                    # Check if neighbor is within boundary
                    if not property_boundary.contains(Point(neighbor)):
                        continue
                    
                    # Calculate tentative g_score
                    tentative_g = g_score[current] + cost(current, neighbor)
                    
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        print(f"WARNING: No path found after {iterations} iterations. Visited {len(visited)} nodes.")
        return None  # No path found
    
    def generate_road_network(
        self,
        entry_point: Tuple[float, float],
        assets: List[Dict[str, Any]],
        property_boundary: Polygon,
        exclusion_zones: List[Polygon],
        dem: Optional[np.ndarray] = None,
        bounds: Optional[Tuple[float, float, float, float]] = None,
        resolution: float = 10.0
    ) -> Dict[str, Any]:
        """
        Generate road network connecting entry to all assets
        
        Args:
            entry_point: Property entry point (x, y)
            assets: List of placed assets
            property_boundary: Property boundary
            exclusion_zones: Exclusion zones
            dem: Digital elevation model
            bounds: DEM bounds
            resolution: Grid resolution
        
        Returns:
            Road network with centerlines and right-of-way
        """
        road_segments = []
        road_network = []
        
        # Generate paths from entry to each asset
        print(f"Generating roads from entry point {entry_point} to {len(assets)} assets")
        for asset in assets:
            asset_location = (asset['x'], asset['y'])
            print(f"Finding path to asset {asset.get('id', 'unknown')} at {asset_location}")
            
            # Find path
            path = self.a_star_pathfinding(
                entry_point,
                asset_location,
                property_boundary,
                exclusion_zones,
                dem,
                bounds,
                resolution
            )
            
            if path:
                print(f"Path found: {len(path)} points")
                # Create road segment
                road_segments.append({
                    'type': 'access' if len(road_network) == 0 else 'secondary',
                    'path': path,
                    'asset_id': asset.get('id'),
                    'width': self.min_width_access if len(road_network) == 0 else self.min_width_secondary
                })
            else:
                print(f"WARNING: No path found to asset {asset.get('id', 'unknown')} at {asset_location}")
        
        # Optimize network (merge overlapping segments)
        optimized_segments = self._optimize_road_network(road_segments)
        
        # Generate right-of-way polygons
        print(f"Processing {len(optimized_segments)} optimized road segments")
        for idx, segment in enumerate(optimized_segments):
            try:
                path = segment['path']
                width = segment['width']
                
                if not path or len(path) < 2:
                    print(f"WARNING: Segment {idx} has invalid path: {path}")
                    continue
                
                # Create centerline
                try:
                    centerline = LineString(path)
                    if not centerline.is_valid:
                        print(f"WARNING: Segment {idx} created invalid LineString, trying to fix...")
                        centerline = centerline.buffer(0)  # Try to fix invalid geometry
                except Exception as e:
                    print(f"ERROR creating LineString for segment {idx}: {e}")
                    print(f"Path: {path}")
                    continue
                
                # Create right-of-way buffer
                # Convert width from feet to degrees
                FEET_TO_DEGREES = 1.0 / 364000.0
                width_deg = width * FEET_TO_DEGREES
                
                try:
                    right_of_way = centerline.buffer(width_deg / 2)
                    if right_of_way.is_empty:
                        print(f"WARNING: Segment {idx} buffer is empty")
                        right_of_way_coords = []
                    else:
                        if hasattr(right_of_way, 'exterior'):
                            right_of_way_coords = list(right_of_way.exterior.coords)
                        else:
                            right_of_way_coords = []
                except Exception as e:
                    print(f"WARNING: Could not create buffer for segment {idx}: {e}")
                    right_of_way_coords = []
                
                # Convert centerline coordinates to list format
                centerline_coords = list(centerline.coords)
                
                # Ensure coordinates are in [lng, lat] format (not [x, y])
                # Shapely LineString.coords returns (x, y) tuples, which should be (lng, lat) for GeoJSON
                formatted_centerline = [[float(coord[0]), float(coord[1])] for coord in centerline_coords]
                
                road_network.append({
                    'type': segment['type'],
                    'centerline': formatted_centerline,
                    'right_of_way': right_of_way_coords,
                    'width': width,
                    'length': centerline.length
                })
                
                print(f"Road {len(road_network)-1}: {len(formatted_centerline)} points, length={centerline.length:.6f}")
            except Exception as e:
                print(f"ERROR processing segment {idx}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        if len(road_network) == 0:
            print("WARNING: No roads generated! This might be because:")
            print(f"  - Entry point: {entry_point}")
            print(f"  - Assets: {len(assets)}")
            print(f"  - Road segments found: {len(road_segments)}")
            print(f"  - Optimized segments: {len(optimized_segments)}")
            # Return empty network instead of failing
            return {
                'roads': [],
                'total_length': 0.0,
                'entry_point': entry_point,
                'warning': 'No roads could be generated. Check that entry point and assets are within property boundary.'
            }
        
        total_length = sum(r['length'] for r in road_network) if road_network else 0.0
        print(f"Road network complete: {len(road_network)} roads, total length={total_length:.6f} degrees")
        
        return {
            'roads': road_network,
            'total_length': total_length,
            'entry_point': entry_point
        }
    
    def _optimize_road_network(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize road network by merging overlapping segments"""
        # Simple optimization: remove duplicate paths
        seen_paths = set()
        optimized = []
        
        for segment in segments:
            path_key = tuple(segment['path'])
            if path_key not in seen_paths:
                seen_paths.add(path_key)
                optimized.append(segment)
        
        return optimized

