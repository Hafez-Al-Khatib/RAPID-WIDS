import React, { useState } from 'react';
import axios from 'axios';
import { Truck, Package, Route, Loader, CheckCircle, AlertCircle } from 'lucide-react';

function RouteOptimizer({ supplyPoints, onRouteOptimized, apiUrl }) {
  const [warehouseId, setWarehouseId] = useState('');
  const [selectedPoints, setSelectedPoints] = useState([]);
  const [numVehicles, setNumVehicles] = useState(3);
  const [vehicleCapacity, setVehicleCapacity] = useState(1000);
  const [optimizing, setOptimizing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const warehouses = supplyPoints.filter(p => p.type === 'warehouse');
  const deliveryPoints = supplyPoints.filter(
    p => p.type === 'affected_area' || p.type === 'shelter' || p.type === 'hospital'
  );

  const handlePointToggle = (pointId) => {
    setSelectedPoints(prev =>
      prev.includes(pointId)
        ? prev.filter(id => id !== pointId)
        : [...prev, pointId]
    );
  };

  const handleOptimize = async () => {
    if (!warehouseId || selectedPoints.length === 0) {
      setError('Please select a warehouse and at least one delivery point');
      return;
    }

    setOptimizing(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${apiUrl}/api/optimize/route`, {
        warehouse_id: parseInt(warehouseId),
        delivery_points: selectedPoints,
        num_vehicles: numVehicles,
        vehicle_capacity: vehicleCapacity,
      });

      setResult(response.data);
      onRouteOptimized(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Optimization failed');
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-xl font-bold mb-2">Supply Route Optimizer</h2>
        <p className="text-sm text-gray-400">
          Optimize delivery routes using Vehicle Routing Problem solver
        </p>
      </div>

      {/* Warehouse Selection */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Select Warehouse
        </label>
        <select
          value={warehouseId}
          onChange={(e) => setWarehouseId(e.target.value)}
          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
        >
          <option value="">Choose warehouse...</option>
          {warehouses.map((warehouse) => (
            <option key={warehouse.id} value={warehouse.id}>
              {warehouse.name} (Capacity: {warehouse.capacity})
            </option>
          ))}
        </select>
      </div>

      {/* Delivery Points Selection */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Select Delivery Points ({selectedPoints.length} selected)
        </label>
        <div className="space-y-2 max-h-48 overflow-y-auto bg-gray-700 rounded-lg p-3">
          {deliveryPoints.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">
              No delivery points available
            </p>
          ) : (
            deliveryPoints.map((point) => (
              <label
                key={point.id}
                className="flex items-center space-x-3 p-2 hover:bg-gray-600 rounded cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedPoints.includes(point.id)}
                  onChange={() => handlePointToggle(point.id)}
                  className="w-4 h-4 rounded border-gray-500"
                />
                <div className="flex-1">
                  <div className="text-sm font-medium">{point.name}</div>
                  <div className="text-xs text-gray-400">
                    Demand: {point.demand} | Priority: {point.priority}/5
                  </div>
                </div>
              </label>
            ))
          )}
        </div>
      </div>

      {/* Vehicle Configuration */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Number of Vehicles
          </label>
          <input
            type="number"
            min="1"
            max="10"
            value={numVehicles}
            onChange={(e) => setNumVehicles(parseInt(e.target.value))}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">
            Vehicle Capacity
          </label>
          <input
            type="number"
            min="100"
            step="100"
            value={vehicleCapacity}
            onChange={(e) => setVehicleCapacity(parseInt(e.target.value))}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Optimize Button */}
      <button
        onClick={handleOptimize}
        disabled={optimizing || !warehouseId || selectedPoints.length === 0}
        className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
      >
        {optimizing ? (
          <>
            <Loader className="w-5 h-5 animate-spin" />
            <span>Optimizing...</span>
          </>
        ) : (
          <>
            <Route className="w-5 h-5" />
            <span>Optimize Routes</span>
          </>
        )}
      </button>

      {/* Error Message */}
      {error && (
        <div className="flex items-start space-x-2 p-4 bg-red-900/30 border border-red-700 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-red-300">{error}</div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="p-4 bg-green-900/30 border border-green-700 rounded-lg space-y-3">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <h3 className="font-bold">Optimization Complete</h3>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-gray-700 rounded p-3">
              <div className="text-xs text-gray-400 mb-1">Total Distance</div>
              <div className="text-lg font-bold">
                {(result.total_distance / 1000).toFixed(2)} km
              </div>
            </div>
            <div className="bg-gray-700 rounded p-3">
              <div className="text-xs text-gray-400 mb-1">Est. Duration</div>
              <div className="text-lg font-bold">
                {result.total_duration.toFixed(0)} min
              </div>
            </div>
            <div className="bg-gray-700 rounded p-3">
              <div className="text-xs text-gray-400 mb-1">Vehicles Used</div>
              <div className="text-lg font-bold">{result.vehicles_used}</div>
            </div>
            <div className="bg-gray-700 rounded p-3">
              <div className="text-xs text-gray-400 mb-1">Routes</div>
              <div className="text-lg font-bold">{result.routes.length}</div>
            </div>
          </div>

          {/* Route Details */}
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Route Details:</h4>
            {result.routes.map((route, idx) => (
              <div key={idx} className="bg-gray-700 rounded p-3 text-sm">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <Truck className="w-4 h-4" />
                    <span className="font-medium">Vehicle {route.vehicle_id + 1}</span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {route.stops.length} stops
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-400">Distance: </span>
                    <span className="font-medium">
                      {(route.distance / 1000).toFixed(2)} km
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Load: </span>
                    <span className="font-medium">{route.load} units</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default RouteOptimizer;
