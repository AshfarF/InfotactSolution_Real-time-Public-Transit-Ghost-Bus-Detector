from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
from typing import List, Dict, Any
import uvicorn

from .models import BusUpdate, BusStatus, FilterRequest
from .gtfs_loader import GTFSLoader
from .detector import GhostBusDetector
from .storage import RedisStorage
from .websocket_manager import ConnectionManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ghost Bus Detector API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global instances
gtfs_loader = GTFSLoader("../")  # Path to GTFS files
detector = GhostBusDetector()
storage = RedisStorage()
manager = ConnectionManager()

# Store active buses
active_buses: Dict[str, BusUpdate] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    try:
        # Load GTFS data
        logger.info("Loading GTFS data...")
        gtfs_loader.load_all()
        
        # Initialize Redis connection
        await storage.connect()
        
        # Start the bus simulator
        asyncio.create_task(bus_simulator())
        
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    await storage.disconnect()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Ghost Bus Detector API is running", "status": "healthy"}

@app.get("/routes")
async def get_routes():
    """Get all available routes"""
    try:
        routes = gtfs_loader.get_routes()
        return {"routes": routes, "total": len(routes)}
    except Exception as e:
        logger.error(f"Error getting routes: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading routes: {str(e)}")

@app.get("/stops")
async def get_stops():
    """Get all stops"""
    try:
        stops = gtfs_loader.get_stops()
        return {"stops": stops, "total": len(stops)}
    except Exception as e:
        logger.error(f"Error getting stops: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading stops: {str(e)}")

@app.get("/buses")
async def get_all_buses():
    """Get all active buses with their current status"""
    buses_data = []
    for bus_id, bus in active_buses.items():
        # Get ghost detection results
        is_ghost, anomaly_types, severity = detector.detect_anomalies(bus.dict())
        
        bus_data = bus.dict()
        bus_data.update({
            "is_ghost": is_ghost,
            "anomaly_types": anomaly_types,
            "severity": severity,
            "status": "ghost" if is_ghost else "active"
        })
        buses_data.append(bus_data)
    
    return {"buses": buses_data, "total": len(buses_data)}

@app.get("/buses/{bus_id}")
async def get_bus(bus_id: str):
    """Get specific bus information"""
    if bus_id not in active_buses:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    bus = active_buses[bus_id]
    is_ghost, anomaly_types, severity = detector.detect_anomalies(bus.dict())
    
    bus_data = bus.dict()
    bus_data.update({
        "is_ghost": is_ghost,
        "anomaly_types": anomaly_types,
        "severity": severity,
        "status": "ghost" if is_ghost else "active"
    })
    
    return bus_data

@app.post("/buses/{bus_id}/update")
async def update_bus_position(bus_id: str, update: BusUpdate):
    """Update bus position (for testing)"""
    active_buses[bus_id] = update
    
    # Store in Redis
    await storage.store_bus_position(bus_id, update.dict())
    
    # Detect anomalies
    is_ghost, anomaly_types, severity = detector.detect_anomalies(update.dict())
    
    # Broadcast update
    bus_data = update.dict()
    bus_data.update({
        "is_ghost": is_ghost,
        "anomaly_types": anomaly_types,
        "severity": severity,
        "status": "ghost" if is_ghost else "active"
    })
    
    await manager.broadcast({
        "type": "bus_update",
        "data": bus_data
    })
    
    return {"message": "Bus position updated", "bus_id": bus_id}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        # Send initial snapshot
        buses_data = []
        for bus_id, bus in active_buses.items():
            is_ghost, anomaly_types, severity = detector.detect_anomalies(bus.dict())
            bus_data = bus.dict()
            bus_data.update({
                "is_ghost": is_ghost,
                "anomaly_types": anomaly_types,
                "severity": severity,
                "status": "ghost" if is_ghost else "active"
            })
            buses_data.append(bus_data)
        
        await websocket.send_json({
            "type": "snapshot",
            "data": buses_data
        })
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def bus_simulator():
    """Simulate bus movements for testing"""
    import random
    import time
    from math import sin, cos, radians
    
    # Initialize some test buses
    test_buses = [
        {"id": "WEST_001", "route_id": "WEST", "lat": 39.7392, "lon": -104.9903},
        {"id": "SOUT_002", "route_id": "SOUT", "lat": 39.7392, "lon": -104.9903},
        {"id": "NRTH_003", "route_id": "NRTH", "lat": 39.7392, "lon": -104.9903},
        {"id": "PEGA_004", "route_id": "PEGA", "lat": 39.7392, "lon": -104.9903},
        {"id": "GHOST_005", "route_id": "WEST", "lat": 39.7392, "lon": -104.9903},  # This will be a ghost
    ]
    
    await asyncio.sleep(5)  # Wait for startup
    
    while True:
        try:
            current_time = time.time()
            
            for i, bus_info in enumerate(test_buses):
                bus_id = bus_info["id"]
                
                # Create realistic movement for most buses
                if bus_id != "GHOST_005":
                    # Simulate movement along a route
                    time_offset = current_time / 60  # Slow movement
                    lat_offset = sin(time_offset + i) * 0.01
                    lon_offset = cos(time_offset + i) * 0.01
                    
                    lat = bus_info["lat"] + lat_offset
                    lon = bus_info["lon"] + lon_offset
                    speed = random.uniform(20, 60)  # km/h
                    
                    bus_update = BusUpdate(
                        id=bus_id,
                        lat=lat,
                        lon=lon,
                        route_id=bus_info["route_id"],
                        speed=speed,
                        timestamp=current_time,
                        bearing=random.uniform(0, 360)
                    )
                else:
                    # Ghost bus - stale data, no movement
                    bus_update = BusUpdate(
                        id=bus_id,
                        lat=bus_info["lat"],
                        lon=bus_info["lon"],
                        route_id=bus_info["route_id"],
                        speed=0,
                        timestamp=current_time - 300,  # 5 minutes old
                        bearing=0
                    )
                
                # Update active buses
                active_buses[bus_id] = bus_update
                
                # Store in Redis
                await storage.store_bus_position(bus_id, bus_update.dict())
                
                # Detect anomalies
                is_ghost, anomaly_types, severity = detector.detect_anomalies(bus_update.dict())
                
                # Broadcast update
                bus_data = bus_update.dict()
                bus_data.update({
                    "is_ghost": is_ghost,
                    "anomaly_types": anomaly_types,
                    "severity": severity,
                    "status": "ghost" if is_ghost else "active"
                })
                
                await manager.broadcast({
                    "type": "bus_update",
                    "data": bus_data
                })
            
            await asyncio.sleep(10)  # Update every 10 seconds
            
        except Exception as e:
            logger.error(f"Error in bus simulator: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
