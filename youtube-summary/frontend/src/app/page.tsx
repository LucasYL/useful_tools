'use client';

import { useState } from 'react';
import { VideoInput } from '@/components/VideoInput';
import { SummaryDisplay } from '@/components/SummaryDisplay';
import { SummaryTypeSelector } from '@/components/SummaryTypeSelector';
import { SummaryLanguageSelector } from '@/components/SummaryLanguageSelector';
import { VideoPlayer, TimelineViewer } from '@/components/VideoPlayer';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';

interface TranscriptEntry {
  text: string;
  start: number;
  duration: number;
}

interface Chapter {
  start_time: number;
  title: string;
}

interface SummaryData {
  videoId: string;
  title: string;
  description: string;
  summary: string;
  transcript: TranscriptEntry[];
  chapters: Chapter[];
}

export default function Home() {
  const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summaryType, setSummaryType] = useState<string>('short');
  const [summaryLanguage, setSummaryLanguage] = useState<string>('en');
  const { language, t } = useLanguage();
  const { isAuthenticated, token } = useAuth();
  const [currentTime, setCurrentTime] = useState(0);
  const [showTranscript, setShowTranscript] = useState(false);

  const handleSubmit = async (url: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // 详细记录输入信息
      console.log('原始输入URL:', url);
      
      // Extract video ID from URL if needed
      const videoId = extractVideoId(url);
      
      if (!videoId) {
        throw new Error('Invalid YouTube URL');
      }
      
      console.log('提取的视频ID:', videoId);
      console.log('请求信息:', {
        videoId,
        summaryType,
        summaryLanguage,
        isAuthenticated
      });
      
      // 构建API URL
      const apiUrl = `${process.env.NEXT_PUBLIC_API_URL || 'https://useful-tools.onrender.com'}/api/summarize`;
      console.log('请求API地址:', apiUrl);
      
      // Create timeout signal to prevent request hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
        console.error('API请求超时！');
      }, 120000); // 120 seconds timeout
      
      // 构建请求体
      const requestBody = { 
        video_id: videoId,
        summary_type: summaryType,
        language: summaryLanguage
      };
      console.log('请求体内容:', JSON.stringify(requestBody));
      
      // 尝试通过测试接口验证视频ID
      console.log('预先检查视频ID是否有字幕...');
      try {
        const testUrl = `${process.env.NEXT_PUBLIC_API_URL || 'https://useful-tools.onrender.com'}/api/test-transcript/${videoId}`;
        const testResponse = await fetch(testUrl);
        if (testResponse.ok) {
          const testData = await testResponse.json();
          console.log('字幕检查结果:', testData);
          if (!testData.success) {
            console.warn('字幕检查失败，但仍将尝试主请求');
          }
        }
      } catch (e) {
        console.warn('字幕预检查失败，但仍将继续:', e);
      }
      
      // Call backend API
      console.log('发送API请求...');
      try {
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(isAuthenticated && token ? { 'Authorization': `Bearer ${token}` } : {})
          },
          body: JSON.stringify(requestBody),
          signal: controller.signal,
        });
        
        // Clear timeout timer
        clearTimeout(timeoutId);
        
        console.log('收到响应, 状态码:', response.status, response.statusText);
  
        if (!response.ok) {
          // Enhanced error handling, get original response text
          const errorText = await response.text();
          console.error('错误响应:', errorText);
          
          // Try parsing JSON (if possible)
          try {
            const errorData = JSON.parse(errorText);
            console.error('解析后的错误数据:', errorData);
            const errorMessage = errorData.detail?.error || errorData.detail?.message || 'Failed to fetch summary';
            const suggestion = errorData.detail?.suggestion || '';
            throw new Error(`${errorMessage}${suggestion ? `\n\n提示: ${suggestion}` : ''}`);
          } catch (parseError) {
            console.error('解析错误JSON失败:', parseError);
            throw new Error(`Request failed (${response.status}): ${errorText.substring(0, 100)}...`);
          }
        }
  
        // Parse response JSON
        try {
          const responseText = await response.text();
          console.log('成功接收响应，数据大小:', Math.round(responseText.length / 1024) + 'KB');
          
          const data = JSON.parse(responseText);
          console.log('摘要长度:', data.summary.length + ' 字符');
          
          setSummaryData({
            videoId: data.video_id,
            title: data.title,
            description: data.description,
            summary: data.summary,
            transcript: data.transcript,
            chapters: data.chapters,
          });
        } catch (jsonError) {
          console.error('解析响应JSON失败:', jsonError);
          throw new Error(`Parse response failed: ${jsonError instanceof Error ? jsonError.message : String(jsonError)}`);
        }
      } catch (fetchError: any) {
        if (fetchError.name === 'AbortError') {
          throw new Error('请求超时，请稍后再试或尝试其他视频');
        }
        throw fetchError;
      }
    } catch (err) {
      console.error('处理错误:', err);
      setError(err instanceof Error ? err.message : '发生未知错误');
    } finally {
      setLoading(false);
    }
  };

  // Function to extract YouTube video ID from URL
  const extractVideoId = (url: string): string | null => {
    // 如果输入已经是一个11位字符的视频ID，直接返回
    if (/^[a-zA-Z0-9_-]{11}$/.test(url)) {
      console.log('输入似乎已经是视频ID:', url);
      return url;
    }
    
    // 使用更强大的正则表达式匹配多种YouTube URL格式
    const patterns = [
      // 标准YouTube URL (youtube.com/watch?v=ID)
      /(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})/,
      // 短URL (youtu.be/ID)
      /(?:youtu\.be\/)([a-zA-Z0-9_-]{11})/,
      // 嵌入URL (youtube.com/embed/ID)
      /(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
      // 短格式 (youtube.com/v/ID)
      /(?:youtube\.com\/v\/)([a-zA-Z0-9_-]{11})/,
      // 其他格式 (大多数YouTube URL)
      /(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
    ];
    
    // 尝试每个正则表达式
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match && match[1]) {
        console.log(`匹配成功，模式: ${pattern}, 提取ID: ${match[1]}`);
        return match[1];
      }
    }
    
    // 如果无法解析但看起来像YouTube URL，返回整个URL
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
      console.warn('无法解析视频ID，但输入似乎是YouTube URL:', url);
      return url;
    }
    
    // 否则，假设输入可能是直接的视频ID或其他URL
    console.warn('无法识别的URL格式，将整个输入作为视频ID:', url);
    return url;
  };

  // Function to handle seeking to a specific timestamp in the video
  const handleSeek = (time: number) => {
    setCurrentTime(time);
    const iframe = document.querySelector('iframe');
    if (iframe && iframe.contentWindow) {
      try {
        iframe.contentWindow.postMessage(JSON.stringify({
          event: 'command',
          func: 'seekTo',
          args: [time, true]
        }), '*');
      } catch (e) {
        console.error('Error seeking:', e);
      }
    }
  };

  // Track current playback time
  const handleTimeUpdate = (time: number) => {
    setCurrentTime(time);
  };

  // Handle summary language change - only change the language used for summary generation
  const handleLanguageChange = (languageCode: string) => {
    // Only update the state for API requests, don't change UI language
    setSummaryLanguage(languageCode);
  };

  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-900 font-sans">
      {/* Header with glass effect */}
      <header className="sticky top-0 z-10 backdrop-blur-md bg-neutral-50/80 border-b border-neutral-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <h1 className="text-2xl font-semibold text-center">
            YouTube Summarizer
          </h1>
        </div>
      </header>

      {/* Input Section */}
      <section className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
        <div className="bg-white rounded-xl shadow-sm border border-neutral-200 p-6">
          <VideoInput onSubmit={handleSubmit} isLoading={loading} />
          
          <div className="mt-4 flex flex-wrap gap-4 justify-center">
            <SummaryTypeSelector 
              selectedType={summaryType as any} 
              onChange={setSummaryType} 
              disabled={loading} 
            />
            
            <SummaryLanguageSelector 
              selectedLanguage={summaryLanguage} 
              onChange={handleLanguageChange} 
              disabled={loading}
            />
          </div>
          
          {!isAuthenticated && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-100 text-sm text-blue-700">
              <p>{t('notLoggedInNote')}</p>
            </div>
          )}
        </div>
      </section>
      
      {loading && (
        <div className="max-w-md mx-auto mt-8 px-4 text-center">
          <div className="animate-pulse">
            <div className="h-2.5 bg-neutral-300 rounded-full w-48 mb-4 mx-auto"></div>
            <div className="h-2 bg-neutral-300 rounded-full max-w-[360px] mb-2.5 mx-auto"></div>
            <div className="h-2 bg-neutral-300 rounded-full mb-2.5 mx-auto"></div>
          </div>
          <p className="mt-4 text-lg font-medium text-neutral-800">{t('processing')}</p>
          <p className="text-sm text-neutral-500">{t('processingNote')}</p>
        </div>
      )}
      
      {error && (
        <div className="max-w-md mx-auto mt-8 px-4">
          <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-center">
            <p className="font-medium text-red-800">{t('error')}</p>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}
      
      {summaryData && !loading && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left column - Video */}
            <div className="flex flex-col">
              <VideoPlayer 
                videoId={summaryData.videoId} 
                onTimeUpdate={handleTimeUpdate}
              />
              
              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => setShowTranscript(!showTranscript)}
                  className="px-4 py-2 text-sm font-medium text-neutral-700 bg-neutral-100 hover:bg-neutral-200 rounded-md transition-colors"
                >
                  {showTranscript ? t('hideTranscript') : t('showTranscript')}
                </button>
              </div>
              
              {/* Transcript (hidden by default) */}
              {showTranscript && (
                <div className="mt-4">
                  <TimelineViewer 
                    transcript={summaryData.transcript} 
                    videoId={summaryData.videoId}
                    onSeek={handleSeek}
                  />
                </div>
              )}
            </div>
            
            {/* Right column - Summary */}
            <div className="h-[calc(100vh-12rem)] sticky top-20">
              <SummaryDisplay
                summary={summaryData.summary}
                title={summaryData.title}
                summaryType={summaryType}
                videoId={summaryData.videoId}
                onSeek={handleSeek}
              />
            </div>
          </div>
        </section>
      )}
    </main>
  );
} 