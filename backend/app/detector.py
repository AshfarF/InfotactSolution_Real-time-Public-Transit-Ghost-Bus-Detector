import time
import math
import statistics
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class GhostBusDetector:
    """Detects ghost buses using various anomaly detection rules"""
    
    def __init__(self):
        # Detection thresholds
        self.stale_threshold = 120  # 2 minutes
        self.stationary_threshold = 60  # 1 minute
        self.min_speed_threshold = 0.5  # m/s
        self.off_route_threshold = 200  # meters
        self.stop_buffer = 50  # meters around stops
        
        # Historical data storage (in-memory for simplicity)
        self.position_history: Dict[str, List[Dict]] = {}
        self.speed_history: Dict[str, List[float]] = {}
        self.max_history_length = 60  # Keep last 60 readings
    
    def detect_anomalies(self, bus_data: Dict) -> Tuple[bool, List[str], str]:
        """
        Detect anomalies in bus data
        Returns: (is_ghost, anomaly_types, severity)
        """
        bus_id = bus_data.get("id", "")
        current_time = time.time()
        
        anomaly_types = []
        
        # 1. Stale data detection
        last_update = bus_data.get("timestamp", current_time)
        if current_time - last_update > self.stale_threshold:
            anomaly_types.append("stale_data")
        
        # 2. Store position history
        self._store_position_history(bus_id, bus_data)
        
        # 3. Non-moving detection
        if self._is_stationary_at_non_stop(bus_id, bus_data):
            anomaly_types.append("stationary_non_stop")
        
        # 4. Speed anomaly detection
        speed_anomaly = self._detect_speed_anomaly(bus_id, bus_data.get("speed"))
        if speed_anomaly:
            anomaly_types.append(speed_anomaly)
        
        # 5. Off-route detection (simplified - would need route geometry)
        # For now, just check if bus is in a reasonable area
        if self._is_off_route(bus_data):
            anomaly_types.append("off_route")
        
        # Determine if it's a ghost bus
        is_ghost = len(anomaly_types) > 0
        
        # Determine severity
        severity = self._calculate_severity(anomaly_types)
        
        return is_ghost, anomaly_types, severity
    
    def _store_position_history(self, bus_id: str, bus_data: Dict):
        """Store position history for movement analysis"""
        if bus_id not in self.position_history:
            self.position_history[bus_id] = []
        
        position_entry = {
            "lat": bus_data.get("lat", 0),
            "lon": bus_data.get("lon", 0),
            "timestamp": bus_data.get("timestamp", time.time()),
            "speed": bus_data.get("speed", 0)
        }
        
        self.position_history[bus_id].append(position_entry)
        
        # Keep only recent history
        if len(self.position_history[bus_id]) > self.max_history_length:
            self.position_history[bus_id] = self.position_history[bus_id][-self.max_history_length:]
    
    def _is_stationary_at_non_stop(self, bus_id: str, bus_data: Dict) -> bool:
        """Check if bus is stationary at a non-stop location"""
        if bus_id not in self.position_history:
            return False
        
        history = self.position_history[bus_id]
        if len(history) < 3:
            return False
        
        # Check if bus hasn't moved much in recent history
        recent_positions = history[-5:]  # Last 5 positions
        if len(recent_positions) < 3:
            return False
        
        # Calculate total distance moved
        total_distance = 0
        for i in range(1, len(recent_positions)):
            distance = self._haversine_distance(
                recent_positions[i-1]["lat"], recent_positions[i-1]["lon"],
                recent_positions[i]["lat"], recent_positions[i]["lon"]
            )
            total_distance += distance
        
        # Check time span
        time_span = recent_positions[-1]["timestamp"] - recent_positions[0]["timestamp"]
        
        # If moved less than 20 meters in more than 1 minute, consider stationary
        if total_distance < 20 and time_span > self.stationary_threshold:
            # Check if near a bus stop (simplified - would need GTFS stops data)
            # For now, assume not near stop if in the middle of coordinates
            lat, lon = bus_data.get("lat", 0), bus_data.get("lon", 0)
            # This is a simplified check - in real implementation, use GTFS stops
            return True
        
        return False
    
    def _detect_speed_anomaly(self, bus_id: str, current_speed: Optional[float]) -> Optional[str]:
        """Detect speed anomalies"""
        if current_speed is None:
            return None
        
        # Store speed history
        if bus_id not in self.speed_history:
            self.speed_history[bus_id] = []
        
        self.speed_history[bus_id].append(current_speed)
        
        # Keep only recent history
        if len(self.speed_history[bus_id]) > self.max_history_length:
            self.speed_history[bus_id] = self.speed_history[bus_id][-self.max_history_length:]
        
        # Need at least 5 readings for analysis
        if len(self.speed_history[bus_id]) < 5:
            return None
        
        speeds = self.speed_history[bus_id]
        avg_speed = statistics.mean(speeds)
        
        # Speed spike detection
        if avg_speed > 0 and current_speed > avg_speed * 3:
            return "speed_spike"
        
        # Speed drop detection
        if avg_speed > 10 and current_speed < avg_speed * 0.3:
            return "speed_drop"
        
        return None
    
    def _is_off_route(self, bus_data: Dict) -> bool:
        """Simplified off-route detection"""
        lat, lon = bus_data.get("lat", 0), bus_data.get("lon", 0)
        
        # Colorado bounds check (very simplified)
        # Colorado is roughly between 37°N-41°N and 102°W-109°W
        if not (37.0 <= lat <= 41.0 and -109.0 <= lon <= -102.0):
            return True
        
        return False
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters"""
        R = 6371000  # Earth's radius in meters
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2)**2)
        
        return 2 * R * math.asin(math.sqrt(a))
    
    def _calculate_severity(self, anomaly_types: List[str]) -> str:
        """Calculate severity based on anomaly types"""
        if not anomaly_types:
            return "info"
        
        critical_anomalies = {"stale_data", "off_route"}
        warning_anomalies = {"stationary_non_stop", "speed_spike", "speed_drop"}
        
        if any(anomaly in critical_anomalies for anomaly in anomaly_types):
            return "critical"
        elif any(anomaly in warning_anomalies for anomaly in anomaly_types):
            return "warning"
        else:
            return "info"
    
    def get_bus_statistics(self, bus_id: str) -> Dict:
        """Get statistics for a specific bus"""
        stats = {
            "position_history_count": len(self.position_history.get(bus_id, [])),
            "speed_history_count": len(self.speed_history.get(bus_id, [])),
            "avg_speed": None,
            "total_distance": 0
        }
        
        # Calculate average speed
        if bus_id in self.speed_history and self.speed_history[bus_id]:
            stats["avg_speed"] = statistics.mean(self.speed_history[bus_id])
        
        # Calculate total distance traveled
        if bus_id in self.position_history and len(self.position_history[bus_id]) > 1:
            positions = self.position_history[bus_id]
            total_distance = 0
            for i in range(1, len(positions)):
                distance = self._haversine_distance(
                    positions[i-1]["lat"], positions[i-1]["lon"],
                    positions[i]["lat"], positions[i]["lon"]
                )
                total_distance += distance
            stats["total_distance"] = total_distance
        
        return stats
