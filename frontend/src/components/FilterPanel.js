import React from 'react';

const FilterPanel = ({ filters, routes, onFilterChange }) => {
  const handleStatusFilterChange = (filterType) => {
    onFilterChange({
      [filterType]: !filters[filterType]
    });
  };

  const handleRouteFilterChange = (routeId) => {
    const currentRoutes = filters.selectedRoutes || [];
    const updatedRoutes = currentRoutes.includes(routeId)
      ? currentRoutes.filter(id => id !== routeId)
      : [...currentRoutes, routeId];
    
    onFilterChange({
      selectedRoutes: updatedRoutes
    });
  };

  const clearAllRouteFilters = () => {
    onFilterChange({
      selectedRoutes: []
    });
  };

  const selectAllRoutes = () => {
    onFilterChange({
      selectedRoutes: routes.map(route => route.route_id)
    });
  };

  return (
    <div className="filter-panel">
      <h3>🔍 Filters</h3>
      
      {/* Bus Status Filters */}
      <div className="filter-group">
        <h4>Bus Status</h4>
        <div className="checkbox-group">
          <div className="checkbox-item">
            <input
              type="checkbox"
              id="showActive"
              checked={filters.showActive}
              onChange={() => handleStatusFilterChange('showActive')}
            />
            <label htmlFor="showActive">
              <span style={{ color: '#27ae60' }}>●</span> Active Buses
            </label>
          </div>
          
          <div className="checkbox-item">
            <input
              type="checkbox"
              id="showGhost"
              checked={filters.showGhost}
              onChange={() => handleStatusFilterChange('showGhost')}
            />
            <label htmlFor="showGhost">
              <span style={{ color: '#e74c3c' }}>●</span> Ghost Buses
            </label>
          </div>
          
          <div className="checkbox-item">
            <input
              type="checkbox"
              id="showAnomalies"
              checked={filters.showAnomalies}
              onChange={() => handleStatusFilterChange('showAnomalies')}
            />
            <label htmlFor="showAnomalies">
              <span style={{ color: '#f39c12' }}>●</span> Anomalies
            </label>
          </div>
        </div>
      </div>

      {/* Route Filters */}
      {routes.length > 0 && (
        <div className="filter-group">
          <h4>Routes</h4>
          
          <div style={{ marginBottom: '10px', display: 'flex', gap: '8px' }}>
            <button
              onClick={selectAllRoutes}
              style={{
                padding: '4px 8px',
                fontSize: '0.75rem',
                border: '1px solid #bdc3c7',
                background: '#ecf0f1',
                borderRadius: '3px',
                cursor: 'pointer'
              }}
            >
              All
            </button>
            <button
              onClick={clearAllRouteFilters}
              style={{
                padding: '4px 8px',
                fontSize: '0.75rem',
                border: '1px solid #bdc3c7',
                background: '#ecf0f1',
                borderRadius: '3px',
                cursor: 'pointer'
              }}
            >
              None
            </button>
          </div>
          
          <div className="route-filters">
            {routes.map(route => (
              <div key={route.route_id} className="checkbox-item">
                <input
                  type="checkbox"
                  id={`route-${route.route_id}`}
                  checked={filters.selectedRoutes.includes(route.route_id)}
                  onChange={() => handleRouteFilterChange(route.route_id)}
                />
                <label htmlFor={`route-${route.route_id}`}>
                  <span 
                    style={{ 
                      color: `#${route.route_color}`,
                      fontWeight: 'bold'
                    }}
                  >
                    ●
                  </span>
                  {' '}
                  {route.route_short_name || route.route_id}
                  {route.route_long_name && (
                    <div style={{ 
                      fontSize: '0.75rem', 
                      color: '#7f8c8d',
                      marginLeft: '15px'
                    }}>
                      {route.route_long_name}
                    </div>
                  )}
                </label>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filter Summary */}
      <div style={{
        marginTop: '15px',
        padding: '10px',
        background: '#f8f9fa',
        borderRadius: '4px',
        fontSize: '0.8rem',
        color: '#6c757d'
      }}>
        <div>
          <strong>Active Filters:</strong>
        </div>
        <div>
          Status: {[
            filters.showActive && 'Active',
            filters.showGhost && 'Ghost',
            filters.showAnomalies && 'Anomalies'
          ].filter(Boolean).join(', ') || 'None'}
        </div>
        {filters.selectedRoutes.length > 0 && (
          <div>
            Routes: {filters.selectedRoutes.length} selected
          </div>
        )}
      </div>
    </div>
  );
};

export default FilterPanel;
