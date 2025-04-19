'use client';

import { useState } from 'react';
import { VideoInput } from '@/components/VideoInput';
import { SummaryDisplay } from '@/components/SummaryDisplay';
import { SummaryTypeSelector } from '@/components/SummaryTypeSelector';
import { LanguageSelector } from '@/components/LanguageSelector';
import { VideoPlayer, TimelineViewer } from '@/components/VideoPlayer';
import { useLanguage } from '@/contexts/LanguageContext';

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
  const { language, setLanguage, t } = useLanguage();
  const [currentTime, setCurrentTime] = useState(0);
  const [showTranscript, setShowTranscript] = useState(false);

  const handleSubmit = async (url: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // Extract video ID from URL if needed
      const videoId = extractVideoId(url);
      
      if (!videoId) {
        throw new Error('Invalid YouTube URL');
      }
      
      console.log('正在为视频生成摘要:', videoId);
      
      // 创建超时信号（防止请求超时）
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 120秒超时
      
      // Call backend API
      const response = await fetch('http://localhost:8000/api/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          video_id: videoId,
          summary_type: summaryType,
          language: language
        }),
        signal: controller.signal,
      });
      
      // 清除超时计时器
      clearTimeout(timeoutId);
      
      console.log('收到响应，状态码:', response.status);

      if (!response.ok) {
        // 增强错误处理，获取原始响应文本
        const errorText = await response.text();
        console.error('错误响应:', errorText.substring(0, 200) + (errorText.length > 200 ? '...' : ''));
        
        // 尝试解析JSON（如果可能）
        try {
          const errorData = JSON.parse(errorText);
          throw new Error(errorData.detail?.message || '获取摘要失败');
        } catch (parseError) {
          throw new Error(`请求失败 (${response.status}): ${errorText.substring(0, 100)}...`);
        }
      }

      // 解析响应JSON
      let data;
      try {
        const responseText = await response.text();
        console.log('成功获取响应，数据大小:', Math.round(responseText.length / 1024) + 'KB');
        
        data = JSON.parse(responseText);
        console.log('摘要长度:', data.summary.length + '字符');
      } catch (jsonError: any) {
        console.error('解析响应JSON失败');
        throw new Error(`解析响应失败: ${jsonError.message}`);
      }

      setSummaryData({
        videoId: data.video_id,
        title: data.title,
        description: data.description,
        summary: data.summary,
        transcript: data.transcript,
        chapters: data.chapters,
      });
    } catch (err) {
      console.error('处理错误:', err);
      setError(err instanceof Error ? err.message : '发生未知错误');
    } finally {
      setLoading(false);
    }
  };

  // Function to extract YouTube video ID from URL
  const extractVideoId = (url: string): string | null => {
    const regex = /(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = url.match(regex);
    return match ? match[1] : url;
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

  // 修改语言处理函数，同时更新界面语言和后端请求参数
  const handleLanguageChange = (languageCode: string) => {
    setLanguage(languageCode);
  };

  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-900 font-sans">
      {/* Header with glass effect */}
      <header className="sticky top-0 z-10 backdrop-blur-md bg-neutral-50/80 border-b border-neutral-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <h1 className="text-2xl font-semibold text-center">
            {t('appTitle')}
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
            
            <LanguageSelector 
              selectedLanguage={language} 
              onChange={handleLanguageChange} 
              disabled={loading}
            />
          </div>
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