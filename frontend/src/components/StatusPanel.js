import React from 'react';

const StatusPanel = ({ statistics, connectionStatus }) => {
  const formatConnectionStatus = (status) => {
    switch (status) {
      case 'connected':
        return { text: 'Connected', color: '#27ae60' };
      case 'disconnected':
        return { text: 'Disconnected', color: '#f39c12' };
      case 'error':
        return { text: 'Connection Error', color: '#e74c3c' };
      default:
        return { text: 'Connecting...', color: '#95a5a6' };
    }
  };

  const connectionInfo = formatConnectionStatus(connectionStatus);

  return (
    <div className="status-panel">
      <h3>📊 Statistics</h3>
      
      {/* Statistics Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number total">{statistics.total}</div>
          <div className="stat-label">Total Buses</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-number active">{statistics.active}</div>
          <div className="stat-label">Active</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-number ghost">{statistics.ghost}</div>
          <div className="stat-label">Ghost</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-number anomaly">{statistics.anomalies}</div>
          <div className="stat-label">Anomalies</div>
        </div>
      </div>

      {/* Connection Status */}
      <div style={{
        background: 'white',
        padding: '1rem',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '1rem'
      }}>
        <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>
          Connection Status
        </h4>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem',
          fontSize: '0.9rem'
        }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: connectionInfo.color
          }}></div>
          <span style={{ color: connectionInfo.color, fontWeight: '500' }}>
            {connectionInfo.text}
          </span>
        </div>
      </div>

      {/* Legend */}
      <div className="legend">
        <h4>Map Legend</h4>
        
        <div className="legend-item">
          <div className="legend-dot active"></div>
          <span className="legend-text">Active Bus</span>
        </div>
        
        <div className="legend-item">
          <div className="legend-dot ghost"></div>
          <span className="legend-text">Ghost Bus</span>
        </div>
        
        <div className="legend-item">
          <div className="legend-dot anomaly"></div>
          <span className="legend-text">Anomaly/Warning</span>
        </div>
      </div>

      {/* System Information */}
      <div style={{
        background: 'white',
        padding: '1rem',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginTop: '1rem'
      }}>
        <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.9rem' }}>
          System Info
        </h4>
        
        <div style={{ fontSize: '0.8rem', color: '#6c757d', lineHeight: '1.4' }}>
          <div style={{ marginBottom: '0.5rem' }}>
            <strong>Ghost Detection:</strong> Real-time anomaly analysis
          </div>
          <div style={{ marginBottom: '0.5rem' }}>
            <strong>Update Frequency:</strong> Every 10 seconds
          </div>
          <div style={{ marginBottom: '0.5rem' }}>
            <strong>Data Source:</strong> Bustang Colorado GTFS
          </div>
          <div>
            <strong>Detection Rules:</strong> Stale data, off-route, stationary
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      {statistics.total > 0 && (
        <div style={{
          background: 'white',
          padding: '1rem',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          marginTop: '1rem'
        }}>
          <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.9rem' }}>
            Performance
          </h4>
          
          <div style={{ fontSize: '0.8rem', color: '#6c757d' }}>
            <div style={{ marginBottom: '0.5rem' }}>
              <strong>Ghost Rate:</strong>{' '}
              {((statistics.ghost / statistics.total) * 100).toFixed(1)}%
            </div>
            <div style={{ marginBottom: '0.5rem' }}>
              <strong>Active Rate:</strong>{' '}
              {((statistics.active / statistics.total) * 100).toFixed(1)}%
            </div>
            <div>
              <strong>Anomaly Rate:</strong>{' '}
              {((statistics.anomalies / statistics.total) * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatusPanel;
