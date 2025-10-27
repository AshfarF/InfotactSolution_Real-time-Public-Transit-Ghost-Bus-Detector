import React, { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom bus icons
const createBusIcon = (status, severity = 'info') => {
  let color = '#27ae60'; // Default green for active
  
  if (status === 'ghost') {
    color = '#e74c3c'; // Red for ghost
  } else if (severity === 'warning') {
    color = '#f39c12'; // Orange for warnings
  } else if (severity === 'critical') {
    color = '#e74c3c'; // Red for critical
  }

  return L.divIcon({
    className: 'custom-bus-icon',
    html: `
      <div style="
        width: 16px;
        height: 16px;
        background-color: ${color};
        border: 2px solid white;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        ${status === 'ghost' ? 'animation: pulse 1.5s infinite;' : ''}
      "></div>
    `,
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  });
};

// Stop icon
const stopIcon = L.divIcon({
  className: 'custom-stop-icon',
  html: `
    <div style="
      width: 8px;
      height: 8px;
      background-color: #3498db;
      border: 1px solid white;
      border-radius: 50%;
      box-shadow: 0 1px 2px rgba(0,0,0,0.2);
    "></div>
  `,
  iconSize: [10, 10],
  iconAnchor: [5, 5]
});

const BusMap = ({ buses, stops, routes }) => {
  const [selectedBus, setSelectedBus] = useState(null);
  const [showStops, setShowStops] = useState(false);
  const [mapCenter, setMapCenter] = useState([39.7392, -104.9903]); // Denver center
  const [mapZoom, setMapZoom] = useState(10);

  // Debug: Log props to console
  useEffect(() => {
    console.log('BusMap received props:');
    console.log('- buses:', buses);
    console.log('- stops:', stops);
    console.log('- routes:', routes);
    console.log('- showStops state:', showStops);
  }, [buses, stops, routes, showStops]);

  // Calculate map bounds based on buses and stops
  useEffect(() => {
    if (buses.length > 0) {
      const lats = buses.map(bus => bus.lat);
      const lons = buses.map(bus => bus.lon);
      
      if (stops.length > 0) {
        lats.push(...stops.map(stop => stop.stop_lat));
        lons.push(...stops.map(stop => stop.stop_lon));
      }
      
      const minLat = Math.min(...lats);
      const maxLat = Math.max(...lats);
      const minLon = Math.min(...lons);
      const maxLon = Math.max(...lons);
      
      const centerLat = (minLat + maxLat) / 2;
      const centerLon = (minLon + maxLon) / 2;
      
      setMapCenter([centerLat, centerLon]);
    }
  }, [buses, stops]);

  // Format timestamp for display
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  };

  // Format anomaly types for display
  const formatAnomalyTypes = (types) => {
    if (!types || types.length === 0) return 'None';
    return types.map(type => type.replace('_', ' ')).join(', ');
  };

  // Get route color
  const getRouteColor = (routeId) => {
    const route = routes.find(r => r.route_id === routeId);
    return route ? `#${route.route_color}` : '#3498db';
  };

  // Memoized bus markers for performance
  const busMarkers = useMemo(() => {
    return buses.map(bus => (
      <Marker
        key={bus.id}
        position={[bus.lat, bus.lon]}
        icon={createBusIcon(bus.status, bus.severity)}
        eventHandlers={{
          click: () => setSelectedBus(bus)
        }}
      >
        <Popup>
          <div style={{ minWidth: '200px' }}>
            <h4 style={{ margin: '0 0 10px 0', color: '#2c3e50' }}>
              Bus {bus.id}
            </h4>
            
            <div style={{ marginBottom: '8px' }}>
              <strong>Route:</strong> {bus.route_id}
            </div>
            
            <div style={{ marginBottom: '8px' }}>
              <strong>Status:</strong>{' '}
              <span style={{ 
                color: bus.is_ghost ? '#e74c3c' : '#27ae60',
                fontWeight: 'bold'
              }}>
                {bus.is_ghost ? 'Ghost Bus' : 'Active'}
              </span>
            </div>
            
            {bus.speed && (
              <div style={{ marginBottom: '8px' }}>
                <strong>Speed:</strong> {Math.round(bus.speed)} km/h
              </div>
            )}
            
            <div style={{ marginBottom: '8px' }}>
              <strong>Last Update:</strong> {formatTimestamp(bus.timestamp)}
            </div>
            
            {bus.anomaly_types && bus.anomaly_types.length > 0 && (
              <div style={{ marginBottom: '8px' }}>
                <strong>Anomalies:</strong>{' '}
                <span style={{ color: '#f39c12' }}>
                  {formatAnomalyTypes(bus.anomaly_types)}
                </span>
              </div>
            )}
            
            <div style={{ marginBottom: '8px' }}>
              <strong>Severity:</strong>{' '}
              <span style={{ 
                color: bus.severity === 'critical' ? '#e74c3c' : 
                       bus.severity === 'warning' ? '#f39c12' : '#27ae60'
              }}>
                {bus.severity || 'info'}
              </span>
            </div>
            
            <div style={{ fontSize: '0.8em', color: '#7f8c8d', marginTop: '10px' }}>
              Lat: {bus.lat.toFixed(6)}, Lon: {bus.lon.toFixed(6)}
            </div>
          </div>
        </Popup>
      </Marker>
    ));
  }, [buses]);

  // Memoized stop markers for performance
  const stopMarkers = useMemo(() => {
    if (!showStops) return [];
    
    return stops.slice(0, 50).map(stop => ( // Limit stops for performance
      <Marker
        key={stop.stop_id}
        position={[stop.stop_lat, stop.stop_lon]}
        icon={stopIcon}
      >
        <Popup>
          <div>
            <h4 style={{ margin: '0 0 8px 0' }}>{stop.stop_name}</h4>
            <div><strong>Stop ID:</strong> {stop.stop_id}</div>
            {stop.stop_code && (
              <div><strong>Code:</strong> {stop.stop_code}</div>
            )}
          </div>
        </Popup>
      </Marker>
    ));
  }, [stops, showStops]);

  return (
    <div style={{ height: '100%', position: 'relative' }}>
      {/* Map Controls */}
      <div style={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        zIndex: 1000,
        background: 'white',
        padding: '10px',
        borderRadius: '4px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
      }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <input
            type="checkbox"
            checked={showStops}
            onChange={(e) => setShowStops(e.target.checked)}
          />
          Show Bus Stops
        </label>
      </div>

      {/* Legend */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        left: '20px',
        zIndex: 1000,
        background: 'white',
        padding: '15px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
        minWidth: '150px'
      }}>
        <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9rem' }}>Legend</h4>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            backgroundColor: '#27ae60',
            borderRadius: '50%',
            border: '2px solid white',
            boxShadow: '0 1px 2px rgba(0,0,0,0.2)'
          }}></div>
          <span style={{ fontSize: '0.8rem' }}>Active Bus</span>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            backgroundColor: '#e74c3c',
            borderRadius: '50%',
            border: '2px solid white',
            boxShadow: '0 1px 2px rgba(0,0,0,0.2)',
            animation: 'pulse 1.5s infinite'
          }}></div>
          <span style={{ fontSize: '0.8rem' }}>Ghost Bus</span>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            backgroundColor: '#f39c12',
            borderRadius: '50%',
            border: '2px solid white',
            boxShadow: '0 1px 2px rgba(0,0,0,0.2)'
          }}></div>
          <span style={{ fontSize: '0.8rem' }}>Warning</span>
        </div>
        
        {showStops && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '8px',
              height: '8px',
              backgroundColor: '#3498db',
              borderRadius: '50%',
              border: '1px solid white',
              boxShadow: '0 1px 2px rgba(0,0,0,0.2)'
            }}></div>
            <span style={{ fontSize: '0.8rem' }}>Bus Stop</span>
          </div>
        )}
      </div>

      {/* Map */}
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Bus markers */}
        {busMarkers}
        
        {/* Stop markers */}
        {stopMarkers}
      </MapContainer>

      {/* Bus count indicator */}
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '10px',
        zIndex: 1000,
        background: 'rgba(0,0,0,0.7)',
        color: 'white',
        padding: '8px 12px',
        borderRadius: '4px',
        fontSize: '0.9rem'
      }}>
        Showing {buses.length} buses
      </div>
    </div>
  );
};

export default BusMap;
