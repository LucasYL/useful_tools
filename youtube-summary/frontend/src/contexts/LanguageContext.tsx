'use client';
import React, { createContext, useContext, useState, ReactNode } from 'react';

// Define translation texts
const translations = {
  'en': {
    'appTitle': 'YouTube Video Summarizer',
    'videoInput': 'Enter YouTube video URL',
    'summarize': 'Summarize',
    'processing': 'Processing video...',
    'processingNote': 'This might take a minute depending on the video length.',
    'error': 'Error:',
    'summaryType': 'Summary Type',
    'shortSummary': 'Short Summary',
    'detailedSummary': 'Detailed Summary',
    'language': 'Language',
    'transcript': 'Transcript',
    'clickTimestampToJump': 'Click on timestamps to jump to that point in the video',
    'timestampJumpTooltip': 'Jump to timestamp',
    'video': 'Video',
    'noVideoId': 'No video ID provided',
    'loadingPlayer': 'Loading video player...',
    'videoLoadingFallback': 'If the video fails to load, you can ',
    'watchOnYouTube': 'watch it directly on YouTube',
    'videoLoadError': 'Unable to load video',
    'invalidVideoId': 'Invalid video ID',
    'transcriptUnavailable': 'Transcript data unavailable'
  },
  'zh': {
    'appTitle': 'YouTube视频摘要工具',
    'videoInput': '输入YouTube视频链接',
    'summarize': '生成摘要',
    'processing': '正在处理视频...',
    'processingNote': '根据视频长度，这可能需要一点时间。',
    'error': '错误：',
    'summaryType': '摘要类型',
    'shortSummary': '简短摘要',
    'detailedSummary': '详细摘要',
    'language': '语言',
    'transcript': '字幕文本',
    'clickTimestampToJump': '点击时间戳可以跳转到视频对应位置',
    'timestampJumpTooltip': '跳转到时间点',
    'video': '视频',
    'noVideoId': '未提供视频ID',
    'loadingPlayer': '加载视频播放器中...',
    'videoLoadingFallback': '如果视频无法加载，您可以',
    'watchOnYouTube': '直接在YouTube上观看',
    'videoLoadError': '无法加载视频',
    'invalidVideoId': '无效的视频ID',
    'transcriptUnavailable': '字幕数据不可用'
  }
};

// Define context type
interface LanguageContextType {
  language: string;
  setLanguage: (code: string) => void;
  t: (key: string, params?: Record<string, string>) => string;
}

// Create context
const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key) => key,
});

// Create Provider component
export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState('en');

  // Translation function with parameter support
  const t = (key: string, params?: Record<string, string>): string => {
    let translation = translations[language as keyof typeof translations]?.[key as keyof typeof translations[keyof typeof translations]] || key;
    
    // Replace parameters if provided
    if (params) {
      Object.entries(params).forEach(([paramKey, paramValue]) => {
        translation = translation.replace(`{${paramKey}}`, paramValue);
      });
    }
    
    return translation;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

// Create Hook for use in components
export function useLanguage() {
  return useContext(LanguageContext);
} 