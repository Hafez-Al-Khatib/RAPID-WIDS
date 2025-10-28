import React from 'react';
import { Clock, MapPin } from 'lucide-react';

function Dashboard({ reports, onSelectReport }) {
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
      1: 'Minor',
      2: 'Major',
      3: 'Destroyed',
      4: 'Unknown',
    };
    return labels[severity] || 'Unknown';
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  return (
    <div className="border-t border-gray-700 max-h-64 overflow-y-auto">
      <div className="px-4 py-3 bg-gray-900 sticky top-0 border-b border-gray-700">
        <h3 className="font-bold text-sm">Recent Reports ({reports.length})</h3>
      </div>
      
      <div className="divide-y divide-gray-700">
        {reports.length === 0 ? (
          <div className="p-6 text-center text-gray-500 text-sm">
            No reports yet. Upload a disaster photo to get started.
          </div>
        ) : (
          reports.slice(0, 10).map((report) => (
            <button
              key={report.id}
              onClick={() => onSelectReport(report)}
              className="w-full px-4 py-3 text-left hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <div
                    className={`w-2 h-2 rounded-full ${getSeverityColor(
                      report.damage_severity
                    )}`}
                  />
                  <span className="font-medium text-sm">
                    Report #{report.id}
                  </span>
                </div>
                <span className="text-xs text-gray-400">
                  {formatTimestamp(report.timestamp)}
                </span>
              </div>
              
              <div className="flex items-center space-x-4 text-xs text-gray-400">
                <div className="flex items-center space-x-1">
                  <MapPin className="w-3 h-3" />
                  <span>
                    {report.latitude.toFixed(4)}, {report.longitude.toFixed(4)}
                  </span>
                </div>
                <div>
                  <span className={`px-2 py-0.5 rounded ${getSeverityColor(report.damage_severity)} text-white`}>
                    {getSeverityLabel(report.damage_severity)}
                  </span>
                </div>
              </div>
              
              {report.description && (
                <p className="text-xs text-gray-500 mt-2 line-clamp-2">
                  {report.description}
                </p>
              )}
            </button>
          ))
        )}
      </div>
    </div>
  );
}

export default Dashboard;
