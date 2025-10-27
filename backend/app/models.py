from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import time

class BusUpdate(BaseModel):
    """Model for bus position updates"""
    id: str = Field(..., description="Unique bus identifier")
    lat: float = Field(..., description="Latitude coordinate")
    lon: float = Field(..., description="Longitude coordinate")
    route_id: str = Field(..., description="Route identifier")
    speed: Optional[float] = Field(None, description="Speed in km/h")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp")
    bearing: Optional[float] = Field(None, description="Bearing in degrees")
    trip_id: Optional[str] = Field(None, description="Trip identifier")

class BusStatus(BaseModel):
    """Model for bus status with ghost detection results"""
    id: str
    lat: float
    lon: float
    route_id: str
    speed: Optional[float] = None
    timestamp: float
    bearing: Optional[float] = None
    is_ghost: bool = False
    anomaly_types: List[str] = []
    severity: str = "info"  # info, warning, critical
    status: str = "active"  # active, ghost

class FilterRequest(BaseModel):
    """Model for filtering requests"""
    show_active: bool = True
    show_ghost: bool = True
    show_anomalies: bool = True
    routes: Optional[List[str]] = None

class RouteInfo(BaseModel):
    """Model for route information"""
    route_id: str
    route_short_name: str
    route_long_name: str
    route_color: str
    route_type: int

class StopInfo(BaseModel):
    """Model for stop information"""
    stop_id: str
    stop_name: str
    stop_lat: float
    stop_lon: float
    stop_code: Optional[str] = None

class AnomalyDetectionResult(BaseModel):
    """Model for anomaly detection results"""
    is_anomaly: bool
    anomaly_types: List[str]
    severity: str
    confidence: float
    details: Dict[str, Any] = {}
