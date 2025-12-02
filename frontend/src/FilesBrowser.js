import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FilesBrowser = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API}/files`);
      setFiles(response.data.files);
    } catch (err) {
      setError('Error loading files');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleString();
  };

  const handleDownload = async (filename) => {
    try {
      console.log('Downloading:', filename);
      const url = `${API}/files/download/${filename}`;
      
      // Fetch the file
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      // Get the blob
      const blob = await response.blob();
      console.log('Blob received:', blob.size, 'bytes');
      
      // Create object URL and download
      const objectUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = objectUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      setTimeout(() => {
        window.URL.revokeObjectURL(objectUrl);
        document.body.removeChild(a);
      }, 100);
      
      console.log('✅ Download initiated');
    } catch (err) {
      console.error('Download failed:', err);
      alert(`Download failed: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            📁 Processed Files
          </h1>
          <p className="text-xl text-purple-200">
            Download your processed LoRA training images
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800">Available Downloads</h2>
            <button
              onClick={loadFiles}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all"
            >
              🔄 Refresh
            </button>
          </div>

          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
              <p className="mt-4 text-gray-600">Loading files...</p>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {!loading && !error && files.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📭</div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">No files yet</h3>
              <p className="text-gray-500">Process some images to see them here!</p>
              <p className="text-sm text-gray-400 mt-4">
                Run: <code className="bg-gray-100 px-2 py-1 rounded">python process_lora_images.py yourfile.zip --public</code>
              </p>
            </div>
          )}

          {!loading && !error && files.length > 0 && (
            <div className="space-y-4">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 hover:shadow-md transition-all"
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-2xl">📦</span>
                          <h3 className="text-lg font-semibold text-gray-800">{file.filename}</h3>
                        </div>
                        <div className="flex gap-4 text-sm text-gray-600">
                          <span>📊 Size: {formatBytes(file.size)}</span>
                          <span>🕐 Created: {formatDate(file.created)}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDownload(file.filename)}
                        className="ml-4 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-semibold hover:from-green-600 hover:to-emerald-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all"
                      >
                        📥 Download
                      </button>
                    </div>
                    <div className="text-xs text-gray-500 bg-gray-50 rounded px-3 py-2">
                      <span className="font-semibold">Direct link:</span>{' '}
                      <a 
                        href={`${API}/files/download/${file.filename}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-purple-600 hover:underline break-all"
                      >
                        {`${BACKEND_URL}/api/files/download/${file.filename}`}
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-purple-900 bg-opacity-50 rounded-xl p-6 text-white">
          <h3 className="text-lg font-semibold mb-3">💡 How to add files here:</h3>
          <div className="space-y-2 text-purple-100">
            <p>1. Upload your ZIP file to the server (e.g., to <code className="bg-purple-800 px-2 py-1 rounded">/tmp/</code>)</p>
            <p>2. Run the processing script with <code className="bg-purple-800 px-2 py-1 rounded">--public</code> flag:</p>
            <code className="block bg-purple-800 px-4 py-2 rounded mt-2">
              python3 /app/process_lora_images.py /tmp/your_images.zip --public
            </code>
            <p className="mt-3">3. Refresh this page to see and download your processed files!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FilesBrowser;
