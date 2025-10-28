import React, { useState } from 'react';
import axios from 'axios';
import { Upload, MapPin, AlertCircle, CheckCircle, Loader } from 'lucide-react';

function UploadPanel({ onUploadSuccess, apiUrl }) {
  const [file, setFile] = useState(null);
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude.toFixed(6));
          setLongitude(position.coords.longitude.toFixed(6));
        },
        (error) => {
          setError('Unable to get current location');
        }
      );
    } else {
      setError('Geolocation is not supported by this browser');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file || !latitude || !longitude) {
      setError('Please provide all required fields');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('latitude', latitude);
    formData.append('longitude', longitude);
    formData.append('description', description);
    formData.append('source', 'user_upload');

    try {
      const response = await axios.post(`${apiUrl}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
      onUploadSuccess(response.data);

      // Reset form
      setFile(null);
      setDescription('');
      document.getElementById('file-input').value = '';
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
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

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-xl font-bold mb-2">Upload Disaster Photo</h2>
        <p className="text-sm text-gray-400">
          Upload a photo with GPS coordinates for AI damage assessment
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium mb-2">Photo</label>
          <div className="relative">
            <input
              id="file-input"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
            <label
              htmlFor="file-input"
              className="flex items-center justify-center w-full px-4 py-8 border-2 border-dashed border-gray-600 rounded-lg cursor-pointer hover:border-gray-500 transition-colors"
            >
              <div className="text-center">
                <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                <p className="text-sm text-gray-400">
                  {file ? file.name : 'Click to upload or drag and drop'}
                </p>
              </div>
            </label>
          </div>
        </div>

        {/* GPS Coordinates */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Latitude</label>
            <input
              type="number"
              step="any"
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="0.000000"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Longitude</label>
            <input
              type="number"
              step="any"
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="0.000000"
              required
            />
          </div>
        </div>

        <button
          type="button"
          onClick={getCurrentLocation}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          <MapPin className="w-4 h-4" />
          <span>Use Current Location</span>
        </button>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Description (Optional)
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
            rows="3"
            placeholder="Describe the damage..."
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={uploading || !file || !latitude || !longitude}
          className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-crisis-600 hover:bg-crisis-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
        >
          {uploading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Upload className="w-5 h-5" />
              <span>Upload & Analyze</span>
            </>
          )}
        </button>
      </form>

      {/* Error Message */}
      {error && (
        <div className="flex items-start space-x-2 p-4 bg-red-900/30 border border-red-700 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-red-300">{error}</div>
        </div>
      )}

      {/* Success Result */}
      {result && (
        <div className="p-4 bg-green-900/30 border border-green-700 rounded-lg space-y-3">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <h3 className="font-bold">Analysis Complete</h3>
          </div>
          
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Severity:</span>
              <span
                className={`px-2 py-1 rounded font-medium text-white ${getSeverityColor(
                  result.damage_severity
                )}`}
              >
                {getSeverityLabel(result.damage_severity)}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Confidence:</span>
              <span className="font-medium">
                {(result.confidence * 100).toFixed(1)}%
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Report ID:</span>
              <span className="font-medium">#{result.id}</span>
            </div>
          </div>
          
          <p className="text-sm text-gray-300">{result.description}</p>
        </div>
      )}
    </div>
  );
}

export default UploadPanel;
