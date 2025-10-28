import React from 'react';
import { BarChart3, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';

function StatsPanel({ stats, damageReports, roadStatuses }) {
  const severityCounts = damageReports.reduce((acc, report) => {
    acc[report.damage_severity] = (acc[report.damage_severity] || 0) + 1;
    return acc;
  }, {});

  const getSeverityColor = (severity) => {
    const colors = {
      0: 'bg-green-500',
      1: 'bg-yellow-500',
      2: 'bg-orange-500',
      3: 'bg-red-500',
      4: 'bg-gray-500',
    };
    return colors[severity] || 'bg-gray-500';
  };

  const getSeverityLabel = (severity) => {
    const labels = {
      0: 'No Damage',
      1: 'Minor Damage',
      2: 'Major Damage',
      3: 'Destroyed',
      4: 'Unclassified',
    };
    return labels[severity] || 'Unknown';
  };

  const roadStatusCounts = roadStatuses.reduce((acc, road) => {
    acc[road.status] = (acc[road.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-xl font-bold mb-2">System Statistics</h2>
        <p className="text-sm text-gray-400">
          Real-time crisis management metrics
        </p>
      </div>

      {/* Overview Cards */}
      {stats && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <BarChart3 className="w-5 h-5 text-blue-500" />
              <span className="text-2xl font-bold">{stats.total_damage_reports}</span>
            </div>
            <div className="text-sm text-gray-400">Total Reports</div>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              <span className="text-2xl font-bold">{stats.severe_damage_reports}</span>
            </div>
            <div className="text-sm text-gray-400">Critical</div>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="w-5 h-5 text-yellow-500" />
              <span className="text-2xl font-bold">{stats.blocked_roads}</span>
            </div>
            <div className="text-sm text-gray-400">Blocked Roads</div>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-2xl font-bold">{stats.supply_points}</span>
            </div>
            <div className="text-sm text-gray-400">Supply Points</div>
          </div>
        </div>
      )}

      {/* Damage Severity Breakdown */}
      <div className="bg-gray-700 rounded-lg p-4">
        <h3 className="font-bold mb-4">Damage Severity Distribution</h3>
        <div className="space-y-3">
          {[0, 1, 2, 3, 4].map((severity) => {
            const count = severityCounts[severity] || 0;
            const percentage = damageReports.length > 0
              ? (count / damageReports.length) * 100
              : 0;

            return (
              <div key={severity}>
                <div className="flex items-center justify-between mb-1 text-sm">
                  <span>{getSeverityLabel(severity)}</span>
                  <span className="font-medium">{count}</span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getSeverityColor(severity)}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Road Status Breakdown */}
      <div className="bg-gray-700 rounded-lg p-4">
        <h3 className="font-bold mb-4">Road Network Status</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-sm">Open</span>
            </div>
            <span className="font-medium">{roadStatusCounts.open || 0}</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-sm">Blocked</span>
            </div>
            <span className="font-medium">{roadStatusCounts.blocked || 0}</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-orange-500" />
              <span className="text-sm">Damaged</span>
            </div>
            <span className="font-medium">{roadStatusCounts.damaged || 0}</span>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="bg-gray-700 rounded-lg p-4">
        <h3 className="font-bold mb-4">System Health</h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-gray-400">API Status</span>
            <span className="flex items-center space-x-1 text-green-500">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span>Online</span>
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400">ML Models</span>
            <span className="flex items-center space-x-1 text-green-500">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span>Active</span>
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Database</span>
            <span className="flex items-center space-x-1 text-green-500">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span>Connected</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default StatsPanel;
