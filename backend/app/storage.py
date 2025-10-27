import redis.asyncio as aioredis
import json
import logging
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

class RedisStorage:
    """Redis storage for real-time bus data and caching"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis = None
        self.pubsub = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = aioredis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # For development, continue without Redis
            self.redis = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
    
    async def store_bus_position(self, bus_id: str, bus_data: Dict):
        """Store bus position data"""
        if not self.redis:
            return
        
        try:
            # Filter out None values before storing
            filtered_data = {k: v for k, v in bus_data.items() if v is not None}
            
            # Store latest position as hash
            key = f"bus:{bus_id}"
            if filtered_data:  # Only store if we have valid data
                # Use individual hset calls instead of mapping for compatibility
                for field, value in filtered_data.items():
                    await self.redis.hset(key, field, str(value))
                await self.redis.expire(key, 300)  # 5 minute TTL
            
            # Store in position history list
            history_key = f"bus:{bus_id}:history"
            position_entry = {
                "lat": bus_data.get("lat"),
                "lon": bus_data.get("lon"),
                "timestamp": bus_data.get("timestamp"),
                "speed": bus_data.get("speed")
            }
            
            # Filter out None values from history entry
            position_entry = {k: v for k, v in position_entry.items() if v is not None}
            
            if position_entry:  # Only store if we have valid position data
                await self.redis.lpush(history_key, json.dumps(position_entry))
                await self.redis.ltrim(history_key, 0, 59)  # Keep last 60 positions
                await self.redis.expire(history_key, 3600)  # 1 hour TTL
            
        except Exception as e:
            logger.error(f"Error storing bus position: {e}")
    
    async def get_bus_position(self, bus_id: str) -> Optional[Dict]:
        """Get latest bus position"""
        if not self.redis:
            return None
        
        try:
            key = f"bus:{bus_id}"
            data = await self.redis.hgetall(key)
            if data:
                # Convert string values back to appropriate types
                return {
                    "id": data.get("id"),
                    "lat": float(data.get("lat", 0)),
                    "lon": float(data.get("lon", 0)),
                    "route_id": data.get("route_id"),
                    "speed": float(data.get("speed", 0)) if data.get("speed") else None,
                    "timestamp": float(data.get("timestamp", 0)),
                    "bearing": float(data.get("bearing", 0)) if data.get("bearing") else None
                }
        except Exception as e:
            logger.error(f"Error getting bus position: {e}")
        
        return None
    
    async def get_all_bus_positions(self) -> List[Dict]:
        """Get all active bus positions"""
        if not self.redis:
            return []
        
        try:
            # Get all bus keys
            keys = await self.redis.keys("bus:*")
            # Filter out history keys
            position_keys = [key for key in keys if not key.endswith(":history")]
            
            buses = []
            for key in position_keys:
                data = await self.redis.hgetall(key)
                if data:
                    bus_data = {
                        "id": data.get("id"),
                        "lat": float(data.get("lat", 0)),
                        "lon": float(data.get("lon", 0)),
                        "route_id": data.get("route_id"),
                        "speed": float(data.get("speed", 0)) if data.get("speed") else None,
                        "timestamp": float(data.get("timestamp", 0)),
                        "bearing": float(data.get("bearing", 0)) if data.get("bearing") else None
                    }
                    buses.append(bus_data)
            
            return buses
            
        except Exception as e:
            logger.error(f"Error getting all bus positions: {e}")
            return []
    
    async def get_bus_history(self, bus_id: str, limit: int = 10) -> List[Dict]:
        """Get bus position history"""
        if not self.redis:
            return []
        
        try:
            history_key = f"bus:{bus_id}:history"
            history_data = await self.redis.lrange(history_key, 0, limit - 1)
            
            history = []
            for entry in history_data:
                try:
                    position = json.loads(entry)
                    history.append(position)
                except json.JSONDecodeError:
                    continue
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting bus history: {e}")
            return []
    
    async def store_anomaly_detection(self, bus_id: str, anomaly_data: Dict):
        """Store anomaly detection results"""
        if not self.redis:
            return
        
        try:
            key = f"anomaly:{bus_id}"
            await self.redis.hset(key, mapping=anomaly_data)
            await self.redis.expire(key, 3600)  # 1 hour TTL
            
        except Exception as e:
            logger.error(f"Error storing anomaly data: {e}")
    
    async def get_anomaly_detection(self, bus_id: str) -> Optional[Dict]:
        """Get anomaly detection results"""
        if not self.redis:
            return None
        
        try:
            key = f"anomaly:{bus_id}"
            data = await self.redis.hgetall(key)
            return data if data else None
            
        except Exception as e:
            logger.error(f"Error getting anomaly data: {e}")
            return None
    
    async def publish_bus_update(self, bus_data: Dict):
        """Publish bus update to subscribers"""
        if not self.redis:
            return
        
        try:
            channel = "bus_updates"
            message = json.dumps(bus_data)
            await self.redis.publish(channel, message)
            
        except Exception as e:
            logger.error(f"Error publishing bus update: {e}")
    
    async def subscribe_to_updates(self):
        """Subscribe to bus updates"""
        if not self.redis:
            return None
        
        try:
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe("bus_updates")
            return self.pubsub
            
        except Exception as e:
            logger.error(f"Error subscribing to updates: {e}")
            return None
    
    async def store_route_cache(self, route_id: str, route_data: Dict):
        """Cache route data"""
        if not self.redis:
            return
        
        try:
            key = f"route:{route_id}"
            await self.redis.hset(key, mapping=route_data)
            await self.redis.expire(key, 86400)  # 24 hour TTL
            
        except Exception as e:
            logger.error(f"Error caching route data: {e}")
    
    async def get_route_cache(self, route_id: str) -> Optional[Dict]:
        """Get cached route data"""
        if not self.redis:
            return None
        
        try:
            key = f"route:{route_id}"
            data = await self.redis.hgetall(key)
            return data if data else None
            
        except Exception as e:
            logger.error(f"Error getting cached route data: {e}")
            return None
    
    async def cleanup_expired_buses(self):
        """Clean up expired bus data"""
        if not self.redis:
            return
        
        try:
            # This would be called periodically to clean up old data
            # Redis TTL handles most of this automatically
            pass
            
        except Exception as e:
            logger.error(f"Error cleaning up expired data: {e}")
