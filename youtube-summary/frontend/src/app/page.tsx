'use client';

import { useState, useEffect } from 'react';
import { VideoInput } from '@/components/VideoInput';
import { SummaryDisplay } from '@/components/SummaryDisplay';
import { SummaryTypeSelector } from '@/components/SummaryTypeSelector';
import { SummaryLanguageSelector } from '@/components/SummaryLanguageSelector';
import { VideoPlayer, TimelineViewer } from '@/components/VideoPlayer';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

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
  const router = useRouter();

  // 如果用户未登录，重定向到登录页面
  useEffect(() => {
    if (!isAuthenticated) {
      // 不立即重定向，让用户看到提示信息
      // router.push('/login');
    }
  }, [isAuthenticated]);

  const handleSubmit = async (url: string) => {
    // 如果未登录，不允许提交
    if (!isAuthenticated) {
      setError(t('loginRequired'));
      return;
    }
    
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

  // 如果用户未登录，显示登录页面
  if (!isAuthenticated) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-neutral-50 to-white font-sans flex flex-col items-center justify-center p-8">
        <div className="max-w-xl w-full bg-white rounded-2xl shadow-lg border border-neutral-100 p-10 text-center">
          <h1 className="text-3xl font-semibold mb-8 text-neutral-800">
            {t('welcomeToClipnote')}
          </h1>
          <p className="mb-10 text-lg text-neutral-600">
            {t('loginRequiredMessage')}
          </p>
          <div className="flex flex-col space-y-4">
            <Link 
              href="/login"
              className="px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-lg shadow-sm"
            >
              {t('login')}
            </Link>
            <Link 
              href="/register"
              className="px-6 py-4 bg-neutral-100 text-neutral-800 rounded-lg hover:bg-neutral-200 transition-colors text-lg"
            >
              {t('createAccount')}
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-neutral-50 to-white font-sans">
      {/* 正常主页内容，只有登录用户能看到 */}
      {/* Header with glass effect */}
      <header className="sticky top-0 z-10 backdrop-blur-md bg-white/80 border-b border-neutral-100 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 sm:px-8 py-6">
          <h1 className="text-3xl font-semibold text-center text-neutral-800">
            YouTube Summarizer
          </h1>
        </div>
      </header>

      {/* Input Section */}
      <section className="max-w-3xl mx-auto px-6 sm:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-lg border border-neutral-100 p-8">
          <VideoInput onSubmit={handleSubmit} isLoading={loading} />
          
          <div className="mt-8 flex flex-wrap gap-6 justify-center">
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
        </div>
      </section>
      
      {loading && (
        <div className="max-w-xl mx-auto mt-12 px-6 text-center">
          <div className="animate-pulse">
            <div className="h-3 bg-neutral-200 rounded-full w-64 mb-6 mx-auto"></div>
            <div className="h-2.5 bg-neutral-200 rounded-full max-w-[480px] mb-4 mx-auto"></div>
            <div className="h-2.5 bg-neutral-200 rounded-full mb-4 mx-auto"></div>
          </div>
          <p className="mt-6 text-xl font-medium text-neutral-800">{t('processing')}</p>
          <p className="text-base text-neutral-500 mt-2">{t('processingNote')}</p>
        </div>
      )}
      
      {error && (
        <div className="max-w-xl mx-auto mt-12 px-6">
          <div className="p-8 rounded-xl bg-red-50 border border-red-100 text-center shadow-sm">
            <p className="font-medium text-xl text-red-800 mb-2">{t('error')}</p>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}
      
      {summaryData && !loading && (
        <section className="max-w-7xl mx-auto px-6 sm:px-8 py-12">
          <div className="grid grid-cols-1 lg:grid-cols-[5fr_4fr] gap-12">
            {/* Left column - Video */}
            <div className="flex flex-col w-full max-w-full">
              <VideoPlayer 
                videoId={summaryData.videoId} 
                onTimeUpdate={handleTimeUpdate}
              />
              
              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowTranscript(!showTranscript)}
                  className="px-5 py-3 text-base font-medium text-neutral-700 bg-neutral-100 hover:bg-neutral-200 rounded-lg transition-colors shadow-sm"
                >
                  {showTranscript ? t('hideTranscript') : t('showTranscript')}
                </button>
              </div>
              
              {/* Transcript (hidden by default) */}
              {showTranscript && (
                <div className="mt-6">
                  <TimelineViewer 
                    transcript={summaryData.transcript} 
                    videoId={summaryData.videoId}
                    onSeek={handleSeek}
                  />
                </div>
              )}
            </div>
            
            {/* Right column - Summary */}
            <div className="h-[calc(100vh-12rem)] sticky top-24">
              <div className="bg-white rounded-2xl shadow-lg border border-neutral-100 p-8 h-full overflow-y-auto">
                <SummaryDisplay
                  summary={summaryData.summary}
                  title={summaryData.title}
                  summaryType={summaryType}
                  videoId={summaryData.videoId}
                  onSeek={handleSeek}
                />
              </div>
            </div>
          </div>
        </section>
      )}
    </main>
  );
} 