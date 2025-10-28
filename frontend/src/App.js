import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import Map from './components/Map';
import UploadPanel from './components/UploadPanel';
import StatsPanel from './components/StatsPanel';
import RouteOptimizer from './components/RouteOptimizer';
import { Activity, AlertCircle, MapPin, Package } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [damageReports, setDamageReports] = useState([]);
  const [roadStatuses, setRoadStatuses] = useState([]);
  const [supplyPoints, setSupplyPoints] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [optimizedRoutes, setOptimizedRoutes] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('upload'); // upload, optimize, stats

  // Fetch initial data
  useEffect(() => {
    fetchDamageReports();
    fetchRoadStatuses();
    fetchSupplyPoints();
    fetchStats();
  }, []);

  const fetchDamageReports = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/reports`);
      setDamageReports(response.data);
    } catch (error) {
      console.error('Error fetching damage reports:', error);
    }
  };

  const fetchRoadStatuses = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/navigation/roads`);
      setRoadStatuses(response.data);
    } catch (error) {
      console.error('Error fetching road statuses:', error);
    }
  };

  const fetchSupplyPoints = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/supply/points`);
      setSupplyPoints(response.data);
    } catch (error) {
      console.error('Error fetching supply points:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleUploadSuccess = (newReport) => {
    setDamageReports([newReport, ...damageReports]);
    fetchStats();
  };

  const handleRouteOptimized = (routes) => {
    setOptimizedRoutes(routes);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Activity className="w-8 h-8 text-crisis-500" />
          <div>
            <h1 className="text-2xl font-bold">RAPID</h1>
            <p className="text-sm text-gray-400">AI-Powered Crisis Navigator</p>
          </div>
        </div>
        
        {stats && (
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-crisis-500" />
              <div>
                <div className="text-xs text-gray-400">Critical Reports</div>
                <div className="text-lg font-bold">{stats.severe_damage_reports}</div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <MapPin className="w-5 h-5 text-yellow-500" />
              <div>
                <div className="text-xs text-gray-400">Blocked Roads</div>
                <div className="text-lg font-bold">{stats.blocked_roads}</div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Package className="w-5 h-5 text-blue-500" />
              <div>
                <div className="text-xs text-gray-400">Supply Points</div>
                <div className="text-lg font-bold">{stats.supply_points}</div>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className="w-96 bg-gray-800 border-r border-gray-700 flex flex-col">
          {/* Tab Navigation */}
          <div className="flex border-b border-gray-700">
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex-1 px-4 py-3 text-sm font-medium ${
                activeTab === 'upload'
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Upload
            </button>
            <button
              onClick={() => setActiveTab('optimize')}
              className={`flex-1 px-4 py-3 text-sm font-medium ${
                activeTab === 'optimize'
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Optimize
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`flex-1 px-4 py-3 text-sm font-medium ${
                activeTab === 'stats'
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Stats
            </button>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === 'upload' && (
              <UploadPanel
                onUploadSuccess={handleUploadSuccess}
                apiUrl={API_URL}
              />
            )}
            {activeTab === 'optimize' && (
              <RouteOptimizer
                supplyPoints={supplyPoints}
                onRouteOptimized={handleRouteOptimized}
                apiUrl={API_URL}
              />
            )}
            {activeTab === 'stats' && (
              <StatsPanel
                stats={stats}
                damageReports={damageReports}
                roadStatuses={roadStatuses}
              />
            )}
          </div>

          {/* Dashboard */}
          <Dashboard
            reports={damageReports}
            onSelectReport={setSelectedReport}
          />
        </aside>

        {/* Map */}
        <main className="flex-1">
          <Map
            damageReports={damageReports}
            roadStatuses={roadStatuses}
            supplyPoints={supplyPoints}
            selectedReport={selectedReport}
            optimizedRoutes={optimizedRoutes}
          />
        </main>
      </div>
    </div>
  );
}

export default App;
