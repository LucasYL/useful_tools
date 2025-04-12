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

  const handleSubmit = async (url: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // Extract video ID from URL if needed
      const videoId = extractVideoId(url);
      
      if (!videoId) {
        throw new Error('Invalid YouTube URL');
      }
      
      // Call backend API
      const response = await fetch('/api/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          video_id: videoId,
          summary_type: summaryType,
          language: language
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || 'Failed to fetch summary');
      }

      const data = await response.json();
      setSummaryData({
        videoId: data.video_id,
        title: data.title,
        description: data.description,
        summary: data.summary,
        transcript: data.transcript,
        chapters: data.chapters,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
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
    <main className="min-h-screen p-8 bg-gray-50">
      <h1 className="mb-8 text-3xl font-bold text-center text-gray-800">
        {t('appTitle')}
      </h1>
      
      <VideoInput onSubmit={handleSubmit} isLoading={loading} />
      
      <div className="flex flex-col sm:flex-row justify-center gap-4">
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
      
      {loading && (
        <div className="mt-8 text-center">
          <p className="text-lg">{t('processing')}</p>
          <p className="text-sm text-gray-500">{t('processingNote')}</p>
        </div>
      )}
      
      {error && (
        <div className="p-4 mt-8 text-center text-red-500 bg-red-50 rounded-lg">
          <p className="font-semibold">{t('error')}</p>
          <p>{error}</p>
        </div>
      )}
      
      {summaryData && !loading && (
        <>
          {/* Video Player */}
          <VideoPlayer 
            videoId={summaryData.videoId} 
            onTimeUpdate={handleTimeUpdate}
          />
          
          {/* Summary */}
          <SummaryDisplay
            summary={summaryData.summary}
            title={summaryData.title}
            summaryType={summaryType}
          />
          
          {/* Transcript with Timeline */}
          <TimelineViewer 
            transcript={summaryData.transcript} 
            videoId={summaryData.videoId}
            onSeek={handleSeek}
          />
        </>
      )}
    </main>
  );
} 