import pandas as pd
import os
from typing import Dict, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class GTFSLoader:
    """Loads and processes GTFS (General Transit Feed Specification) data files."""
    
    def __init__(self, gtfs_path: str = "../"):
        """
        Initialize GTFS loader with path to GTFS files.
        
        Args:
            gtfs_path: Path to directory containing GTFS .txt files
        """
        self.gtfs_path = Path(gtfs_path)
        self.routes = pd.DataFrame()
        self.stops = pd.DataFrame()
        self.trips = pd.DataFrame()
        self.stop_times = pd.DataFrame()
        self.shapes = pd.DataFrame()
        self.calendar = pd.DataFrame()
        self.calendar_dates = pd.DataFrame()
        self.agency = pd.DataFrame()
        self.fare_attributes = pd.DataFrame()
        self.fare_rules = pd.DataFrame()
        
    def load_all(self) -> bool:
        """
        Load all GTFS files.
        
        Returns:
            bool: True if loading was successful, False otherwise
        """
        try:
            logger.info(f"Loading GTFS data from {self.gtfs_path}")
            
            # Required files
            self.routes = self._load_file("routes.txt")
            self.stops = self._load_file("stops.txt")
            self.trips = self._load_file("trips.txt")
            self.stop_times = self._load_file("stop_times.txt")
            
            # Optional files
            self.shapes = self._load_file("shapes.txt", required=False)
            self.calendar = self._load_file("calendar.txt", required=False)
            self.calendar_dates = self._load_file("calendar_dates.txt", required=False)
            self.agency = self._load_file("agency.txt", required=False)
            
            # Additional optional files
            self.fare_attributes = self._load_file("fare_attributes.txt", required=False)
            self.fare_rules = self._load_file("fare_rules.txt", required=False)
            
            # Log loaded data statistics
            logger.info(f"Loaded {len(self.routes)} routes")
            logger.info(f"Loaded {len(self.stops)} stops")
            logger.info(f"Loaded {len(self.trips)} trips")
            logger.info(f"Loaded {len(self.stop_times)} stop times")
            
            if not self.shapes.empty:
                logger.info(f"Loaded {len(self.shapes)} shape points")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading GTFS data: {e}")
            return False
    
    def _load_file(self, filename: str, required: bool = True) -> pd.DataFrame:
        """
        Load a single GTFS file.
        
        Args:
            filename: Name of the GTFS file to load
            required: Whether the file is required (will raise error if missing)
            
        Returns:
            pd.DataFrame: Loaded data or empty DataFrame if file not found and not required
        """
        file_path = self.gtfs_path / filename
        
        if not file_path.exists():
            if required:
                raise FileNotFoundError(f"Required GTFS file not found: {file_path}")
            else:
                logger.warning(f"Optional GTFS file not found: {file_path}")
                return pd.DataFrame()
        
        try:
            # Load with error handling for different encodings
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='latin-1')
            
            logger.debug(f"Loaded {filename}: {len(df)} records")
            return df
            
        except Exception as e:
            if required:
                raise Exception(f"Error loading {filename}: {e}")
            else:
                logger.warning(f"Error loading optional file {filename}: {e}")
                return pd.DataFrame()
    
    def get_routes(self) -> List[Dict]:
        """Get all routes as list of dictionaries."""
        if self.routes.empty:
            return []
        
        routes = []
        for _, route in self.routes.iterrows():
            routes.append({
                'route_id': route.get('route_id', ''),
                'route_short_name': route.get('route_short_name', ''),
                'route_long_name': route.get('route_long_name', ''),
                'route_type': route.get('route_type', 3),  # Default to bus
                'route_color': route.get('route_color', 'FFFFFF'),
                'route_text_color': route.get('route_text_color', '000000')
            })
        
        return routes
    
    def get_stops(self) -> List[Dict]:
        """Get all stops as list of dictionaries."""
        if self.stops.empty:
            return []
        
        stops = []
        for _, stop in self.stops.iterrows():
            try:
                stops.append({
                    'stop_id': str(stop.get('stop_id', '')),
                    'stop_name': str(stop.get('stop_name', '')),
                    'stop_lat': float(stop.get('stop_lat', 0.0)) if pd.notna(stop.get('stop_lat')) else 0.0,
                    'stop_lon': float(stop.get('stop_lon', 0.0)) if pd.notna(stop.get('stop_lon')) else 0.0,
                    'stop_code': str(stop.get('stop_code', '')),
                    'stop_desc': str(stop.get('stop_desc', '')),
                    'zone_id': str(stop.get('zone_id', '')),
                    'stop_url': str(stop.get('stop_url', '')),
                    'location_type': int(stop.get('location_type', 0)) if pd.notna(stop.get('location_type')) else 0,
                    'parent_station': str(stop.get('parent_station', ''))
                })
            except Exception as e:
                logger.error(f"Error processing stop {stop.get('stop_id', 'unknown')}: {e}")
                continue
        
        return stops
    
    def get_trips_for_route(self, route_id: str) -> List[Dict]:
        """Get all trips for a specific route."""
        if self.trips.empty:
            return []
        
        route_trips = self.trips[self.trips['route_id'] == route_id]
        
        trips = []
        for _, trip in route_trips.iterrows():
            trips.append({
                'trip_id': trip.get('trip_id', ''),
                'route_id': trip.get('route_id', ''),
                'service_id': trip.get('service_id', ''),
                'trip_headsign': trip.get('trip_headsign', ''),
                'trip_short_name': trip.get('trip_short_name', ''),
                'direction_id': int(trip.get('direction_id', 0)),
                'block_id': trip.get('block_id', ''),
                'shape_id': trip.get('shape_id', '')
            })
        
        return trips
    
    def get_stop_times_for_trip(self, trip_id: str) -> List[Dict]:
        """Get all stop times for a specific trip."""
        if self.stop_times.empty:
            return []
        
        trip_stop_times = self.stop_times[self.stop_times['trip_id'] == trip_id].sort_values('stop_sequence')
        
        stop_times = []
        for _, stop_time in trip_stop_times.iterrows():
            stop_times.append({
                'trip_id': stop_time.get('trip_id', ''),
                'arrival_time': stop_time.get('arrival_time', ''),
                'departure_time': stop_time.get('departure_time', ''),
                'stop_id': stop_time.get('stop_id', ''),
                'stop_sequence': int(stop_time.get('stop_sequence', 0)),
                'stop_headsign': stop_time.get('stop_headsign', ''),
                'pickup_type': int(stop_time.get('pickup_type', 0)),
                'drop_off_type': int(stop_time.get('drop_off_type', 0)),
                'shape_dist_traveled': float(stop_time.get('shape_dist_traveled', 0.0))
            })
        
        return stop_times
    
    def get_shape_points(self, shape_id: str) -> List[Dict]:
        """Get all shape points for a specific shape."""
        if self.shapes.empty or not shape_id:
            return []
        
        shape_points = self.shapes[self.shapes['shape_id'] == shape_id].sort_values('shape_pt_sequence')
        
        points = []
        for _, point in shape_points.iterrows():
            points.append({
                'shape_id': point.get('shape_id', ''),
                'shape_pt_lat': float(point.get('shape_pt_lat', 0.0)),
                'shape_pt_lon': float(point.get('shape_pt_lon', 0.0)),
                'shape_pt_sequence': int(point.get('shape_pt_sequence', 0)),
                'shape_dist_traveled': float(point.get('shape_dist_traveled', 0.0))
            })
        
        return points
    
    def get_route_by_id(self, route_id: str) -> Optional[Dict]:
        """Get a specific route by ID."""
        if self.routes.empty:
            return None
        
        route_data = self.routes[self.routes['route_id'] == route_id]
        if route_data.empty:
            return None
        
        route = route_data.iloc[0]
        return {
            'route_id': route.get('route_id', ''),
            'route_short_name': route.get('route_short_name', ''),
            'route_long_name': route.get('route_long_name', ''),
            'route_type': route.get('route_type', 3),
            'route_color': route.get('route_color', 'FFFFFF'),
            'route_text_color': route.get('route_text_color', '000000')
        }
    
    def get_stop_by_id(self, stop_id: str) -> Optional[Dict]:
        """Get a specific stop by ID."""
        if self.stops.empty:
            return None
        
        stop_data = self.stops[self.stops['stop_id'] == stop_id]
        if stop_data.empty:
            return None
        
        stop = stop_data.iloc[0]
        return {
            'stop_id': stop.get('stop_id', ''),
            'stop_name': stop.get('stop_name', ''),
            'stop_lat': float(stop.get('stop_lat', 0.0)),
            'stop_lon': float(stop.get('stop_lon', 0.0)),
            'stop_code': stop.get('stop_code', ''),
            'stop_desc': stop.get('stop_desc', '')
        }
    
    def is_loaded(self) -> bool:
        """Check if GTFS data has been loaded."""
        return not (self.routes.empty or self.stops.empty or self.trips.empty or self.stop_times.empty)
