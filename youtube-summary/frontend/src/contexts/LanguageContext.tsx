'use client';
import React, { createContext, useContext, useState, ReactNode } from 'react';

// 定义翻译文本
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
  }
};

// 定义上下文类型
interface LanguageContextType {
  language: string;
  setLanguage: (code: string) => void;
  t: (key: string) => string;
}

// 创建上下文
const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key) => key,
});

// 创建Provider组件
export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState('en');

  // 翻译函数
  const t = (key: string): string => {
    return translations[language as keyof typeof translations]?.[key as keyof typeof translations[keyof typeof translations]] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

// 创建Hook以便在组件中使用
export function useLanguage() {
  return useContext(LanguageContext);
} 