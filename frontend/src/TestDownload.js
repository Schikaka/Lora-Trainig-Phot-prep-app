import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TestDownload = () => {
  const [status, setStatus] = useState('');
  const [sessionId, setSessionId] = useState('a22afa05-e1a3-43b9-ba6c-8fba47f3e259'); // Test session

  const testDirectDownload = () => {
    setStatus('Testing direct link download...');
    const url = `${API}/download/${sessionId}`;
    window.open(url, '_blank');
    setStatus('✅ Opened in new tab');
  };

  const testBlobDownload = async () => {
    setStatus('Testing blob download...');
    try {
      const response = await axios.get(`${API}/download/${sessionId}`, {
        responseType: 'blob',
        timeout: 60000,
      });
      
      setStatus(`Received blob: ${response.data.size} bytes`);
      
      const blob = new Blob([response.data], { type: 'application/zip' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `test_download_${sessionId}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setStatus('✅ Download triggered via blob');
    } catch (err) {
      setStatus(`❌ Error: ${err.message}`);
      console.error(err);
    }
  };

  const testFetch = async () => {
    setStatus('Testing fetch API...');
    try {
      const response = await fetch(`${API}/download/${sessionId}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const blob = await response.blob();
      setStatus(`Received ${blob.size} bytes via fetch`);
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `test_fetch_${sessionId}.zip`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setStatus('✅ Download triggered via fetch');
    } catch (err) {
      setStatus(`❌ Error: ${err.message}`);
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-4">Download Test Page</h1>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Session ID:</label>
          <input
            type="text"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
        </div>

        <div className="space-y-3 mb-4">
          <button
            onClick={testDirectDownload}
            className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Test 1: Direct Link (Open in New Tab)
          </button>
          
          <button
            onClick={testBlobDownload}
            className="w-full bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Test 2: Axios Blob Download
          </button>
          
          <button
            onClick={testFetch}
            className="w-full bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600"
          >
            Test 3: Fetch API Download
          </button>
        </div>

        {status && (
          <div className="p-4 bg-gray-100 rounded">
            <p className="font-mono text-sm">{status}</p>
          </div>
        )}

        <div className="mt-6 text-sm text-gray-600">
          <p>Test URL: {API}/download/{sessionId}</p>
        </div>
      </div>
    </div>
  );
};

export default TestDownload;
