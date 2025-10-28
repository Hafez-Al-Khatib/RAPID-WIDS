import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default marker icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom marker icons
const createDamageIcon = (severity) => {
  const colors = {
    0: '#22c55e', // green - no damage
    1: '#eab308', // yellow - minor
    2: '#f97316', // orange - major
    3: '#ef4444', // red - destroyed
    4: '#6b7280', // gray - unclassified
  };

  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        background-color: ${colors[severity] || colors[4]};
        width: 24px;
        height: 24px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      "></div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

const createSupplyIcon = (type) => {
  const colors = {
    warehouse: '#3b82f6',
    hospital: '#ef4444',
    shelter: '#22c55e',
    affected_area: '#f97316',
  };

  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        background-color: ${colors[type] || '#6b7280'};
        width: 20px;
        height: 20px;
        border-radius: 3px;
        border: 2px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      "></div>
    `,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
};

function MapController({ selectedReport }) {
  const map = useMap();

  useEffect(() => {
    if (selectedReport) {
      map.flyTo([selectedReport.latitude, selectedReport.longitude], 15, {
        duration: 1,
      });
    }
  }, [selectedReport, map]);

  return null;
}

function Map({ damageReports, roadStatuses, supplyPoints, selectedReport, optimizedRoutes }) {
  const [mapCenter, setMapCenter] = useState([0, 0]);
  const [mapZoom, setMapZoom] = useState(13);

  useEffect(() => {
    // Set map center based on first damage report or default
    if (damageReports.length > 0) {
      setMapCenter([damageReports[0].latitude, damageReports[0].longitude]);
    }
  }, [damageReports]);

  const getSeverityColor = (severity) => {
    const colors = {
      0: '#22c55e',
      1: '#eab308',
      2: '#f97316',
      3: '#ef4444',
      4: '#6b7280',
    };
    return colors[severity] || colors[4];
  };

  const getSeverityRadius = (severity) => {
    return (severity + 1) * 100; // Radius in meters
  };

  return (
    <MapContainer
      center={mapCenter}
      zoom={mapZoom}
      className="h-full w-full"
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <MapController selectedReport={selectedReport} />

      {/* Damage Reports with Heatmap Circles */}
      {damageReports.map((report) => (
        <React.Fragment key={report.id}>
          {/* Severity Circle */}
          <Circle
            center={[report.latitude, report.longitude]}
            radius={getSeverityRadius(report.damage_severity)}
            pathOptions={{
              color: getSeverityColor(report.damage_severity),
              fillColor: getSeverityColor(report.damage_severity),
              fillOpacity: 0.2,
              weight: 2,
            }}
          />
          
          {/* Marker */}
          <Marker
            position={[report.latitude, report.longitude]}
            icon={createDamageIcon(report.damage_severity)}
          >
            <Popup>
              <div className="text-gray-900">
                <h3 className="font-bold text-lg mb-2">Damage Report #{report.id}</h3>
                <div className="space-y-1 text-sm">
                  <div>
                    <strong>Severity:</strong>{' '}
                    <span
                      className="px-2 py-1 rounded text-white"
                      style={{ backgroundColor: getSeverityColor(report.damage_severity) }}
                    >
                      Level {report.damage_severity}
                    </span>
                  </div>
                  <div>
                    <strong>Confidence:</strong> {(report.confidence * 100).toFixed(1)}%
                  </div>
                  <div>
                    <strong>Status:</strong>{' '}
                    {report.verified ? (
                      <span className="text-green-600">✓ Verified</span>
                    ) : (
                      <span className="text-yellow-600">⚠ Unverified</span>
                    )}
                  </div>
                  <div>
                    <strong>Description:</strong> {report.description}
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(report.timestamp).toLocaleString()}
                  </div>
                </div>
              </div>
            </Popup>
          </Marker>
        </React.Fragment>
      ))}

      {/* Supply Points */}
      {supplyPoints.map((point) => (
        <Marker
          key={point.id}
          position={[point.latitude, point.longitude]}
          icon={createSupplyIcon(point.type)}
        >
          <Popup>
            <div className="text-gray-900">
              <h3 className="font-bold text-lg mb-2">{point.name}</h3>
              <div className="space-y-1 text-sm">
                <div>
                  <strong>Type:</strong> {point.type}
                </div>
                <div>
                  <strong>Capacity:</strong> {point.capacity}
                </div>
                <div>
                  <strong>Demand:</strong> {point.demand}
                </div>
                <div>
                  <strong>Priority:</strong> {point.priority}/5
                </div>
              </div>
            </div>
          </Popup>
        </Marker>
      ))}

      {/* Blocked Roads */}
      {roadStatuses
        .filter((road) => road.status === 'blocked')
        .map((road) => (
          <Polyline
            key={road.id}
            positions={[
              [road.start_lat, road.start_lon],
              [road.end_lat, road.end_lon],
            ]}
            pathOptions={{
              color: '#ef4444',
              weight: 5,
              opacity: 0.8,
              dashArray: '10, 10',
            }}
          >
            <Popup>
              <div className="text-gray-900">
                <h3 className="font-bold">⚠ Blocked Road</h3>
                <p className="text-sm">
                  <strong>Status:</strong> {road.status}
                </p>
                <p className="text-sm">
                  <strong>Severity:</strong> {road.severity}
                </p>
              </div>
            </Popup>
          </Polyline>
        ))}

      {/* Optimized Routes */}
      {optimizedRoutes && optimizedRoutes.routes && optimizedRoutes.routes.map((route, idx) => {
        const colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];
        const color = colors[idx % colors.length];
        
        // Convert stop indices to coordinates
        const routeCoords = route.stops.map((stopIdx) => {
          if (stopIdx === 0) {
            // Warehouse
            const warehouse = supplyPoints.find(p => p.type === 'warehouse');
            return warehouse ? [warehouse.latitude, warehouse.longitude] : null;
          } else {
            // Delivery point
            const point = supplyPoints[stopIdx - 1];
            return point ? [point.latitude, point.longitude] : null;
          }
        }).filter(coord => coord !== null);

        return (
          <Polyline
            key={`route-${idx}`}
            positions={routeCoords}
            pathOptions={{
              color: color,
              weight: 4,
              opacity: 0.7,
            }}
          >
            <Popup>
              <div className="text-gray-900">
                <h3 className="font-bold">Vehicle {route.vehicle_id + 1}</h3>
                <p className="text-sm">
                  <strong>Distance:</strong> {(route.distance / 1000).toFixed(2)} km
                </p>
                <p className="text-sm">
                  <strong>Load:</strong> {route.load} units
                </p>
              </div>
            </Popup>
          </Polyline>
        );
      })}
    </MapContainer>
  );
}

export default Map;
