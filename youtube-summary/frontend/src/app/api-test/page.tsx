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
      console.log('开始直接测试API:', videoId, summaryType, language);
      const testResult = await testDirectAPI(videoId, summaryType, language);
      setResult(testResult);
      
      if (testResult.success && testResult.data) {
        // 显示关键指标
        console.log('测试成功');
        console.log('响应大小:', Math.round(JSON.stringify(testResult.data).length / 1024) + 'KB');
        console.log('摘要长度:', testResult.data.summary.length + '字符');
      }
    } catch (error) {
      console.error('测试失败:', error);
      setResult({ success: false, error });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">YouTube摘要API测试工具</h1>
      <p className="mb-4 text-neutral-600">直接测试后端API，不经过Next.js代理</p>
      
      <div className="flex flex-col gap-4 mb-6 bg-white p-6 rounded-xl shadow-sm">
        <div>
          <label className="block text-sm font-medium mb-1">视频ID或URL</label>
          <input 
            type="text" 
            value={videoId} 
            onChange={(e) => setVideoId(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="输入YouTube视频ID或URL"
          />
        </div>
        
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">摘要类型</label>
            <select 
              value={summaryType} 
              onChange={(e) => setSummaryType(e.target.value)}
              className="w-full p-2 border rounded"
            >
              <option value="short">简短摘要</option>
              <option value="detailed">详细摘要</option>
            </select>
          </div>
          
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">语言</label>
            <select 
              value={language} 
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full p-2 border rounded"
            >
              <option value="zh">中文</option>
              <option value="en">英文</option>
            </select>
          </div>
        </div>
        
        <button 
          onClick={handleTest}
          disabled={loading || !videoId}
          className="bg-blue-600 text-white py-2 px-4 rounded disabled:bg-blue-300"
        >
          {loading ? '处理中...' : '开始测试'}
        </button>
      </div>
      
      {loading && (
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 text-center">
          <p className="text-blue-800 font-medium">请求处理中，请耐心等待...</p>
          <p className="text-blue-600 text-sm mt-1">生成详细摘要可能需要较长时间</p>
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
                测试成功
              </span>
            ) : (
              <span className="text-red-600 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                测试失败
              </span>
            )}
          </h2>
          
          {result.success && result.data && (
            <div>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-neutral-50 p-3 rounded">
                  <p className="text-sm font-medium text-neutral-500">视频标题</p>
                  <p className="font-medium">{result.data.title.substring(0, 60)}{result.data.title.length > 60 ? '...' : ''}</p>
                </div>
                <div className="bg-neutral-50 p-3 rounded">
                  <p className="text-sm font-medium text-neutral-500">数据大小</p>
                  <p className="font-medium">{Math.round(JSON.stringify(result.data).length / 1024)}KB</p>
                </div>
                <div className="bg-neutral-50 p-3 rounded">
                  <p className="text-sm font-medium text-neutral-500">字幕条数</p>
                  <p className="font-medium">{result.data.transcript.length}条</p>
                </div>
                <div className="bg-neutral-50 p-3 rounded">
                  <p className="text-sm font-medium text-neutral-500">摘要长度</p>
                  <p className="font-medium">{result.data.summary.length}字符</p>
                </div>
              </div>
              
              <div className="mt-4">
                <h3 className="font-medium mb-2">摘要预览：</h3>
                <div className="bg-neutral-50 p-4 rounded overflow-auto max-h-[300px]">
                  <p className="whitespace-pre-wrap">{result.data.summary.substring(0, 600)}...</p>
                </div>
              </div>
            </div>
          )}
          
          {!result.success && (
            <div className="bg-red-50 p-4 rounded">
              <p className="text-red-800 font-medium">错误信息</p>
              <p className="text-red-700">{result.error?.toString()}</p>
              {result.responseText && (
                <div className="mt-2">
                  <p className="text-red-800 font-medium">响应内容预览：</p>
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