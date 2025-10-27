import React, { useState, useEffect, useCallback } from 'react';
import BusMap from './components/BusMap';
import FilterPanel from './components/FilterPanel';
import StatusPanel from './components/StatusPanel';
import './App.css';

function App() {
  const [buses, setBuses] = useState({});
  const [routes, setRoutes] = useState([]);
  const [stops, setStops] = useState([]);
  const [filters, setFilters] = useState({
    showActive: true,
    showGhost: true,
    showAnomalies: true,
    selectedRoutes: []
  });
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [statistics, setStatistics] = useState({
    total: 0,
    active: 0,
    ghost: 0,
    anomalies: 0
  });

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8000/ws');
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
      };
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'snapshot') {
            // Initial snapshot of all buses
            const busesDict = {};
            message.data.forEach(bus => {
              busesDict[bus.id] = bus;
            });
            setBuses(busesDict);
          } else if (message.type === 'bus_update') {
            // Individual bus update
            setBuses(prev => ({
              ...prev,
              [message.data.id]: message.data
            }));
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionStatus('disconnected');
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
      };
      
      return ws;
    };

    const ws = connectWebSocket();
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  // Load routes and stops
  useEffect(() => {
    const loadStaticData = async () => {
      try {
        // Load routes
        const routesResponse = await fetch('http://localhost:8000/routes');
        if (routesResponse.ok) {
          const routesData = await routesResponse.json();
          console.log('Routes data received:', routesData); // Debug log
          setRoutes(routesData.routes || routesData);
        }
        
        // Load stops
        const stopsResponse = await fetch('http://localhost:8000/stops');
        if (stopsResponse.ok) {
          const stopsData = await stopsResponse.json();
          console.log('Stops data received:', stopsData); // Debug log
          console.log('Setting stops to:', stopsData.stops || stopsData); // Debug log
          setStops(stopsData.stops || stopsData);
        }
      } catch (error) {
        console.error('Error loading static data:', error);
      }
    };

    loadStaticData();
  }, []);

  // Debug: Add useEffect to log stops state changes
  useEffect(() => {
    console.log('Stops state updated:', stops);
    console.log('Number of stops:', stops.length);
    if (stops.length > 0) {
      console.log('First stop sample:', stops[0]);
    }
  }, [stops]);

  // Update statistics when buses change
  useEffect(() => {
    const busList = Object.values(buses);
    const stats = {
      total: busList.length,
      active: busList.filter(bus => bus.status === 'active').length,
      ghost: busList.filter(bus => bus.is_ghost).length,
      anomalies: busList.filter(bus => bus.anomaly_types && bus.anomaly_types.length > 0).length
    };
    setStatistics(stats);
  }, [buses]);

  // Filter buses based on current filters
  const filteredBuses = useCallback(() => {
    return Object.values(buses).filter(bus => {
      // Filter by status
      if (bus.is_ghost && !filters.showGhost) return false;
      if (!bus.is_ghost && !filters.showActive) return false;
      
      // Filter by anomalies
      if (bus.anomaly_types && bus.anomaly_types.length > 0 && !filters.showAnomalies) return false;
      
      // Filter by routes
      if (filters.selectedRoutes.length > 0 && !filters.selectedRoutes.includes(bus.route_id)) return false;
      
      return true;
    });
  }, [buses, filters]);

  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🚌 Ghost Bus Detector</h1>
        <div className="connection-status">
          <span className={`status-indicator ${connectionStatus}`}></span>
          {connectionStatus === 'connected' ? 'Connected' : 
           connectionStatus === 'error' ? 'Connection Error' : 'Connecting...'}
        </div>
      </header>
      
      <div className="app-content">
        <div className="sidebar">
          <FilterPanel 
            filters={filters}
            routes={routes}
            onFilterChange={handleFilterChange}
          />
          <StatusPanel 
            statistics={statistics}
            connectionStatus={connectionStatus}
          />
        </div>
        
        <div className="map-container">
          <BusMap 
            buses={filteredBuses()}
            stops={stops}
            routes={routes}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
