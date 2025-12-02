import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ImageProcessor = () => {
  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.zip')) {
      setFile(selectedFile);
      setError(null);
      setResult(null);
    } else {
      setError('Please select a ZIP file');
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.zip')) {
        setFile(droppedFile);
        setError(null);
        setResult(null);
      } else {
        setError('Please drop a ZIP file');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API}/process-images`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minutes timeout
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error processing images. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setProcessing(false);
    }
  };

  const handleDownload = () => {
    if (!result?.session_id) {
      console.log('Download prevented: No session ID');
      return;
    }

    console.log('Starting direct download for session:', result.session_id);
    
    // Create direct download link
    const downloadUrl = `${API}/download/${result.session_id}`;
    
    // Open in new window - browser will handle download
    window.open(downloadUrl, '_blank');
    
    console.log('✅ Download link opened:', downloadUrl);
    
    // Cleanup server files after a delay
    setTimeout(async () => {
      try {
        console.log('Cleaning up server files...');
        await axios.delete(`${API}/cleanup/${result.session_id}`);
        console.log('✅ Server cleanup completed');
      } catch (cleanupErr) {
        console.log('Cleanup completed or file already removed');
      }
    }, 5000); // Wait 5 seconds for download to start
  };

  const handleReset = async () => {
    // Cleanup server files if result exists
    if (result?.session_id) {
      try {
        await axios.delete(`${API}/cleanup/${result.session_id}`);
      } catch (err) {
        // Ignore cleanup errors
        console.log('Cleanup completed or file already removed');
      }
    }
    
    setFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4" data-testid="app-title">
            LoRA Image Processor
          </h1>
          <p className="text-xl text-purple-200" data-testid="app-subtitle">
            Prepare images for Stable Diffusion LoRA training
          </p>
          <div className="mt-4 text-sm text-purple-300">
            <p>✨ Face detection & smart cropping</p>
            <p>📐 Outputs: 512×512 (close-up) & 512×768 (portrait)</p>
            <p>🚀 High-quality upscaling with Lanczos</p>
          </div>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          {!result ? (
            <>
              {/* Upload Area */}
              <div
                className={`border-3 border-dashed rounded-xl p-12 text-center transition-all ${
                  dragActive
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-300 hover:border-purple-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                data-testid="upload-area"
              >
                <div className="space-y-4">
                  <div className="flex justify-center">
                    <svg
                      className="w-20 h-20 text-purple-500"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                      />
                    </svg>
                  </div>

                  <div>
                    <label
                      htmlFor="file-upload"
                      className="cursor-pointer text-purple-600 hover:text-purple-700 font-semibold text-lg"
                      data-testid="upload-label"
                    >
                      Choose a ZIP file
                    </label>
                    <p className="text-gray-500 mt-2">or drag and drop here</p>
                    <input
                      id="file-upload"
                      type="file"
                      accept=".zip"
                      onChange={handleFileChange}
                      className="hidden"
                      data-testid="file-input"
                    />
                  </div>

                  {file && (
                    <div className="mt-4 p-4 bg-purple-50 rounded-lg" data-testid="selected-file">
                      <p className="text-sm text-gray-700">
                        <span className="font-semibold">Selected:</span> {file.name}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Size: {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg" data-testid="error-message">
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}

              {/* Process Button */}
              <button
                onClick={handleUpload}
                disabled={!file || processing}
                className={`mt-8 w-full py-4 px-6 rounded-xl font-semibold text-lg transition-all ${
                  !file || processing
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                }`}
                data-testid="process-button"
              >
                {processing ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Processing Images...
                  </span>
                ) : (
                  '🎨 Process Images'
                )}
              </button>
            </>
          ) : (
            <>
              {/* Success Result */}
              <div className="text-center space-y-6" data-testid="success-result">
                <div className="inline-block p-4 bg-green-100 rounded-full">
                  <svg
                    className="w-16 h-16 text-green-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>

                <h2 className="text-3xl font-bold text-gray-800">Processing Complete!</h2>

                <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 space-y-3">
                  <div className="grid grid-cols-2 gap-4 text-left">
                    <div>
                      <p className="text-sm text-gray-600">Input Images</p>
                      <p className="text-2xl font-bold text-purple-600">{result.total_images_processed}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Output Files</p>
                      <p className="text-2xl font-bold text-pink-600">{result.total_output_files}</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700 mt-4 pt-4 border-t border-gray-200">
                    Each image was processed into 512×512 and 512×768 versions
                  </p>
                </div>

                <div className="flex gap-4">
                  <button
                    onClick={handleDownload}
                    disabled={downloading}
                    className={`flex-1 py-4 px-6 rounded-xl font-semibold text-lg shadow-lg transition-all ${
                      downloading
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-600 hover:to-emerald-700 hover:shadow-xl transform hover:-translate-y-0.5'
                    }`}
                    data-testid="download-button"
                  >
                    {downloading ? (
                      <span className="flex items-center justify-center text-white">
                        <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                            fill="none"
                          />
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          />
                        </svg>
                        Downloading...
                      </span>
                    ) : (
                      '📥 Download Processed Images'
                    )}
                  </button>
                  <button
                    onClick={handleReset}
                    disabled={downloading}
                    className={`py-4 px-6 rounded-xl font-semibold text-lg transition-all ${
                      downloading
                        ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                    data-testid="reset-button"
                  >
                    ↻ Process Another
                  </button>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Info Section */}
        <div className="mt-8 text-center text-sm text-purple-200">
          <p>💡 <strong>Tip:</strong> Images are automatically cropped with face detection and upscaled for optimal LoRA training</p>
        </div>
      </div>
    </div>
  );
};

export default ImageProcessor;
