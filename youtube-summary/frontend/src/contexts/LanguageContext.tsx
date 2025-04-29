'use client';
import React, { createContext, useContext, useState, ReactNode } from 'react';

// Define translation texts
const translations = {
  'en': {
    'appTitle': 'Clipnote',
    'videoInput': 'Enter YouTube video URL',
    'summarize': 'Summarize',
    'processing': 'Processing video...',
    'processingNote': 'This might take a minute depending on the video length.',
    'error': 'Error:',
    'summaryType': 'Summary Type',
    'shortSummary': 'Short Summary',
    'detailedSummary': 'Detailed Summary',
    'language': 'Language',
    'outputLanguage': 'Output Language',
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
    'transcriptUnavailable': 'Transcript data unavailable',
    'showTranscript': 'Show Transcript',
    'hideTranscript': 'Hide Transcript',
    'pasteYoutubeUrl': 'Paste a YouTube video URL to generate a summary',
    'playerLoadingTimeout': 'Player is taking longer than expected to load',
    'retryLoading': 'Retry Loading',
    'notLoggedInNote': 'You are not logged in. Login to save your summaries and access them later.',
    // Auth translations
    'login': 'Log In',
    'loggingIn': 'Logging In...',
    'register': 'Sign Up',
    'registering': 'Creating Account...',
    'username': 'Username',
    'email': 'Email',
    'password': 'Password',
    'confirmPassword': 'Confirm Password',
    'passwordRequirements': 'Password must be at least 6 characters long',
    'passwordsNotMatch': 'Passwords do not match',
    'passwordTooShort': 'Password must be at least 6 characters long',
    'noAccount': 'Don\'t have an account?',
    'signUp': 'Sign Up',
    'alreadyHaveAccount': 'Already have an account?',
    'loginRequired': 'Login Required',
    'loginToViewHistory': 'Please login to view your summary history',
    'loginToViewSummary': 'Please login to view this summary',
    'backToHome': 'Back to Home',
    'logout': 'Log Out',
    'welcomeToYTSum': 'Welcome to Clipnote',
    'welcomeToClipnote': 'Welcome to Clipnote',
    'loginRequiredMessage': 'Please log in to access the YouTube summarizer tool and create summaries.',
    'createAccount': 'Create Account',
    'createNew': 'Create New',
    // History translations
    'summaryHistory': 'Summary History',
    'showOnlyFavorites': 'Show only favorites',
    'loading': 'Loading...',
    'failedToLoadHistory': 'Failed to load summary history',
    'failedToLoadSummary': 'Failed to load summary',
    'noSummaries': 'You have no saved summaries yet',
    'noFavoriteSummaries': 'You have no favorite summaries yet',
    'createSummary': 'Create a Summary',
    'viewDetails': 'View Details',
    'delete': 'Delete',
    'favorite': 'Favorite',
    'unfavorite': 'Unfavorite',
    'confirmDelete': 'Are you sure you want to delete this summary?',
    'summaryDetail': 'Summary Detail',
    'summaryContent': 'Summary Content',
    'summaryNotFound': 'Summary not found',
    'backToHistory': 'Back to History',
    'instantSummaries': 'Instant Summaries',
    'instantSummariesDesc': 'Get summaries in seconds with AI-powered technology',
    'timeStampedOutlines': 'Time-Stamped Outlines',
    'timeStampedOutlinesDesc': 'Navigate videos easily with clickable timestamps',
    'summaryManagement': 'Organized Summary Archive',
    'summaryManagementDesc': 'Save, search and organize all your video insights in one place',
    'welcomeBack': 'Welcome Back',
    'enterUsername': 'Enter your username',
    'enterPassword': 'Enter your password',
    'chooseUsername': 'Choose a username',
    'enterEmail': 'Enter your email',
    'createPassword': 'Create a password',
    'repeatPassword': 'Repeat your password',
    'demoCredentials': 'Demo Credentials',
    'intelligentVideoSummarizer': 'Intelligent Video Summarizer',
  },
  'zh': {
    'appTitle': 'Clipnote',
    'videoInput': '输入YouTube视频链接',
    'summarize': '生成摘要',
    'processing': '正在处理视频...',
    'processingNote': '根据视频长度，这可能需要一点时间。',
    'error': '错误：',
    'summaryType': '摘要类型',
    'shortSummary': '简短摘要',
    'detailedSummary': '详细摘要',
    'language': '语言',
    'outputLanguage': '输出语言',
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
    'transcriptUnavailable': '字幕数据不可用',
    'showTranscript': '显示字幕',
    'hideTranscript': '隐藏字幕',
    'pasteYoutubeUrl': '粘贴YouTube视频网址以生成摘要',
    'playerLoadingTimeout': '播放器加载时间超过预期',
    'retryLoading': '重试加载',
    'notLoggedInNote': '您尚未登录。登录后可以保存摘要并在以后查看。',
    // Auth translations
    'login': '登录',
    'loggingIn': '登录中...',
    'register': '注册',
    'registering': '创建账号中...',
    'username': '用户名',
    'email': '电子邮箱',
    'password': '密码',
    'confirmPassword': '确认密码',
    'passwordRequirements': '密码必须至少6个字符',
    'passwordsNotMatch': '两次输入的密码不匹配',
    'passwordTooShort': '密码必须至少6个字符',
    'noAccount': '还没有账号？',
    'signUp': '立即注册',
    'alreadyHaveAccount': '已有账号？',
    'loginRequired': '需要登录',
    'loginToViewHistory': '请登录以查看您的摘要历史',
    'loginToViewSummary': '请登录以查看此摘要',
    'backToHome': '返回首页',
    'logout': '退出登录',
    'welcomeToYTSum': '欢迎使用Clipnote',
    'welcomeToClipnote': '欢迎使用Clipnote',
    'loginRequiredMessage': '请登录以使用YouTube摘要工具并创建摘要。',
    'createAccount': '创建账号',
    'createNew': '创建新摘要',
    // History translations
    'summaryHistory': '摘要历史',
    'showOnlyFavorites': '只显示收藏',
    'loading': '加载中...',
    'failedToLoadHistory': '加载摘要历史失败',
    'failedToLoadSummary': '加载摘要失败',
    'noSummaries': '您还没有保存的摘要',
    'noFavoriteSummaries': '您还没有收藏的摘要',
    'createSummary': '创建摘要',
    'viewDetails': '查看详情',
    'delete': '删除',
    'favorite': '收藏',
    'unfavorite': '取消收藏',
    'confirmDelete': '确定要删除这个摘要吗？',
    'summaryDetail': '摘要详情',
    'summaryContent': '摘要内容',
    'summaryNotFound': '未找到摘要',
    'backToHistory': '返回历史记录',
    'instantSummaries': '即时摘要',
    'instantSummariesDesc': '利用AI技术，几秒钟内获取视频摘要',
    'timeStampedOutlines': '时间戳大纲',
    'timeStampedOutlinesDesc': '通过可点击的时间戳轻松导航视频内容',
    'summaryManagement': '摘要归档管理',
    'summaryManagementDesc': '在一处保存、搜索和组织您的所有视频见解',
    'welcomeBack': '欢迎回来',
    'enterUsername': '输入用户名',
    'enterPassword': '输入密码',
    'chooseUsername': '选择用户名',
    'enterEmail': '输入电子邮箱',
    'createPassword': '创建密码',
    'repeatPassword': '再次输入密码',
    'demoCredentials': '演示账号',
    'intelligentVideoSummarizer': '智能视频摘要工具',
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