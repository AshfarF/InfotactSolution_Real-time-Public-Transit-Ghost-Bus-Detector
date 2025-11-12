# 🚌 Ghost Bus Detector

A real-time analytics system that identifies "ghost buses" in public transit networks—vehicles that appear on tracking apps but are not in service, are non-responsive, or are severely off-route.

## 📋 Overview

This system provides riders with a more accurate and reliable view of the transit system by filtering out unreliable bus data, reducing uncertainty and wait times for daily commuters and tourists.

## 🏗️ Architecture

- **Backend**: FastAPI with Python for real-time data processing and anomaly detection
- **Frontend**: React with Leaflet maps for interactive visualization
- **Database**: Redis for real-time caching and pub/sub messaging
- **Data Source**: GTFS (General Transit Feed Specification) data from Bustang Colorado

## ✨ Features

### Core Functionality
- **Real-time Bus Tracking**: Live visualization of bus positions on an interactive map
- **Ghost Bus Detection**: Identifies problematic buses using multiple detection algorithms:
  - **Stale Data Detection**: Buses with outdated position information
  - **Stationary Detection**: Buses stuck at non-designated stops
  - **Off-Route Detection**: Buses significantly deviating from their routes
  - **Speed Anomaly Detection**: Unusual speed patterns

### User Interface
- **Interactive Map**: Leaflet-based map with custom bus icons
- **Real-time Updates**: WebSocket connections for live data streaming
- **Advanced Filtering**: Show/hide different bus types and routes
- **Statistics Dashboard**: Real-time metrics and performance indicators
- **Responsive Design**: Works on desktop and mobile devices

### Technical Features
- **WebSocket Communication**: Real-time bidirectional communication
- **Redis Caching**: Fast data storage and retrieval
- **GTFS Integration**: Standard transit data format support
- **Docker Support**: Easy deployment and scaling
- **Anomaly Scoring**: Weighted scoring system for ghost detection

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bustang-co-us
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup (Development)

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

#### Redis Setup
```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or install locally
# Windows: Download from https://redis.io/download
# Linux: sudo apt-get install redis-server
# macOS: brew install redis
```

## 📊 API Endpoints

### Bus Data
- `GET /buses` - Get all buses with status
- `GET /buses/{bus_id}` - Get specific bus information
- `POST /buses/{bus_id}/update` - Update bus position (testing)

### Static Data
- `GET /routes` - Get all transit routes
- `GET /stops` - Get all bus stops

### WebSocket
- `WS /ws` - Real-time bus updates

## 🎯 Ghost Detection Algorithms

### 1. Stale Data Detection
- **Threshold**: 2 minutes without updates
- **Logic**: Flags buses with outdated position data
- **Severity**: Critical

### 2. Stationary Detection
- **Threshold**: No movement for 1+ minutes at non-stops
- **Logic**: Detects buses stuck outside designated stops
- **Severity**: Warning

### 3. Speed Anomaly Detection
- **Spike Detection**: Current speed > 3× average speed
- **Drop Detection**: Current speed < 30% of average speed
- **Logic**: Uses historical speed data for comparison
- **Severity**: Warning

### 4. Off-Route Detection
- **Threshold**: Outside Colorado state boundaries (simplified)
- **Logic**: Geographic boundary checking
- **Severity**: Critical

## 🎨 User Interface Guide

### Map Features
- **Green Dots**: Active, healthy buses
- **Red Pulsing Dots**: Ghost buses
- **Orange Dots**: Buses with warnings
- **Blue Dots**: Bus stops (when enabled)

### Sidebar Controls
- **Status Filters**: Toggle active/ghost/anomaly buses
- **Route Filters**: Filter by specific transit routes
- **Statistics**: Real-time system metrics
- **Connection Status**: WebSocket connection indicator

### Bus Information
Click any bus marker to see:
- Bus ID and route information
- Current status and anomaly details
- Speed and last update time
- Severity level and coordinates

## 🔧 Configuration

### Environment Variables

#### Backend
- `REDIS_URL`: Redis connection string (default: redis://localhost:6379)
- `GTFS_PATH`: Path to GTFS data files (default: ../)

#### Frontend
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000)
- `REACT_APP_WS_URL`: WebSocket URL (default: ws://localhost:8000)

### Detection Thresholds
Edit `backend/app/detector.py` to adjust:
- `stale_threshold`: Time before marking as stale (default: 120s)
- `stationary_threshold`: Time for stationary detection (default: 60s)
- `off_route_threshold`: Distance threshold for off-route (default: 200m)

## 📈 Performance & Scaling

### Current Capacity
- **Bus Updates**: 1000+ buses with 10-second update intervals
- **WebSocket Connections**: 100+ concurrent users
- **Data Retention**: 60 position points per bus in memory

### Scaling Recommendations
- **High Load**: Use Redis Cluster for distributed caching
- **Multiple Workers**: Scale backend with multiple FastAPI instances
- **Database**: Add PostgreSQL/TimescaleDB for historical data
- **CDN**: Use CDN for frontend static assets

## 🧪 Testing

### Bus Simulator
The system includes a built-in bus simulator that creates:
- 4 active buses with realistic movement patterns
- 1 ghost bus with stale data for testing

### Manual Testing
```bash
# Update a bus position
curl -X POST "http://localhost:8000/buses/TEST_001/update" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "TEST_001",
    "lat": 39.7392,
    "lon": -104.9903,
    "route_id": "WEST",
    "speed": 45,
    "bearing": 180
  }'
```

## 🛠️ Development

### Project Structure
```
bustang-co-us/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py        # Pydantic models
│   │   ├── gtfs_loader.py   # GTFS data processing
│   │   ├── detector.py      # Ghost detection algorithms
│   │   ├── storage.py       # Redis integration
│   │   └── websocket_manager.py # WebSocket handling
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BusMap.js    # Leaflet map component
│   │   │   ├── FilterPanel.js # Filter controls
│   │   │   └── StatusPanel.js # Statistics display
│   │   ├── App.js           # Main React component
│   │   └── App.css          # Styling
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml       # Multi-service setup
└── *.txt                   # GTFS data files
```

### Adding New Detection Rules
1. Edit `backend/app/detector.py`
2. Add new detection method to `GhostBusDetector` class
3. Update `detect_anomalies()` method to include new rule
4. Test with bus simulator

### Frontend Customization
- **Map Styling**: Edit `frontend/src/components/BusMap.js`
- **UI Colors**: Modify CSS variables in `frontend/src/App.css`
- **New Filters**: Extend `FilterPanel.js` component

## 🔍 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if backend is running on port 8000
   - Verify CORS settings in FastAPI
   - Check browser console for errors

2. **No Buses Appearing**
   - Ensure Redis is running
   - Check backend logs for GTFS loading errors
   - Verify bus simulator is active

3. **Map Not Loading**
   - Check internet connection (requires OpenStreetMap tiles)
   - Verify Leaflet CSS is loaded
   - Check browser console for JavaScript errors

4. **Docker Issues**
   - Ensure Docker daemon is running
   - Check port conflicts (3000, 8000, 6379)
   - Review docker-compose logs

### Logs
```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f redis
```

## 📝 Data Sources

This project uses GTFS data from **Bustang Colorado**, Colorado Department of Transportation's interregional express bus service. The dataset includes:

- **Routes**: 6 bus routes (West, South, North, Pegasus, Snowstang, Estes Park)
- **Stops**: 54 bus stops across Colorado
- **Trips**: 509 scheduled trips
- **Shapes**: Detailed route geometries with 13M+ coordinate points

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Colorado Department of Transportation** for providing GTFS data
- **OpenStreetMap** contributors for map tiles
- **Leaflet** for the mapping library
- **FastAPI** and **React** communities for excellent frameworks

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review API documentation at `/docs`

---
