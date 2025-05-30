'use client';

import { useState } from 'react';
import { testDirectAPI } from '../directTest';

export default function ApiTestPage() {
  const [videoId, setVideoId] = useState('');
  const [summaryType, setSummaryType] = useState('detailed');
  const [language, setLanguage] = useState('zh');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleTest = async () => {
    if (!videoId) return;
    
    setLoading(true);
    setResult(null);
    
    try {
      console.log('Starting direct API test:', videoId, summaryType, language);
      const testResult = await testDirectAPI(videoId, summaryType, language);
      setResult(testResult);
      
      if (testResult.success && testResult.data) {
        // Display key metrics
        console.log('Test successful');
        console.log('Response size:', Math.round(JSON.stringify(testResult.data).length / 1024) + 'KB');
        console.log('Summary length:', testResult.data.summary.length + ' characters');
      }
    } catch (error) {
      console.error('Test failed:', error);
      setResult({ success: false, error });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">YouTube Summary API Test Tool</h1>
      <p className="mb-4 text-neutral-600">Test backend API directly, bypassing Next.js proxy</p>
      
      <div className="flex flex-col gap-4 mb-6 bg-white p-6 rounded-xl shadow-sm">
        <div>
          <label className="block text-sm font-medium mb-1">Video ID or URL</label>
          <input 
            type="text" 
            value={videoId} 
            onChange={(e) => setVideoId(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="Enter YouTube video ID or URL"
          />
        </div>
        
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Summary Type</label>
            <select 
              value={summaryType} 
              onChange={(e) => setSummaryType(e.target.value)}
              className="w-full p-2 border rounded"
            >
              <option value="short">Short Summary</option>
              <option value="detailed">Detailed Summary</option>
            </select>
          </div>
          
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Language</label>
            <select 
              value={language} 
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full p-2 border rounded"
            >
              <option value="zh">Chinese</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>
        
        <button 
          onClick={handleTest}
          disabled={loading || !videoId}
          className="bg-blue-600 text-white py-2 px-4 rounded disabled:bg-blue-300"
        >
          {loading ? 'Processing...' : 'Start Test'}
        </button>
      </div>
      
      {loading && (
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 text-center">
          <p className="text-blue-800 font-medium">Request processing, please wait...</p>
          <p className="text-blue-600 text-sm mt-1">Generating detailed summaries may take longer</p>
        </div>
      )}
      
      {result && (
        <div className="mt-6 bg-white p-6 rounded-xl shadow-sm">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            {result.success ? (
              <span className="text-green-600 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Test Successful
              </span>
            ) : (
              <span className="text-red-600 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Test Failed
              </span>
            )}
          </h2>
          
          {result.success && result.data && (
            <div>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-neutral-50 p-3 rounded">
                  <p className="text-sm font-medium text-neutral-500">Video Title</p>
                  <p className="font-medium">{result.data.title.substring(0, 60)}{result.data.title.length > 60 ? '...' : ''}</p>
                </div>
                <div className="bg-neutral-50 p-3 rounded">
                  <p className="text-sm font-medium text-neutral-500">Data Size</p>
                  <p className="font-medium">{Math.round(JSON.stringify(result.data).length / 1024)}KB</p>
                </div>
                <div className="bg-neutral-50 p-3 rounded">
                  <p className="text-sm font-medium text-neutral-500">Transcript Entries</p>
                  <p className="font-medium">{result.data.transcript.length} entries</p>
                </div>
                <div className="bg-neutral-50 p-3 rounded">
                  <p className="text-sm font-medium text-neutral-500">Summary Length</p>
                  <p className="font-medium">{result.data.summary.length} characters</p>
                </div>
              </div>
              
              <div className="mt-4">
                <h3 className="font-medium mb-2">Summary Preview:</h3>
                <div className="bg-neutral-50 p-4 rounded overflow-auto max-h-[300px]">
                  <p className="whitespace-pre-wrap">{result.data.summary.substring(0, 600)}...</p>
                </div>
              </div>
            </div>
          )}
          
          {!result.success && (
            <div className="bg-red-50 p-4 rounded">
              <p className="text-red-800 font-medium">Error Message</p>
              <p className="text-red-700">{result.error?.toString()}</p>
              {result.responseText && (
                <div className="mt-2">
                  <p className="text-red-800 font-medium">Response Preview:</p>
                  <pre className="text-sm overflow-auto max-h-[200px] p-2 bg-red-100 rounded">
                    {result.responseText}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
} 