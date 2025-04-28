'use client';

import { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';

interface VideoInputProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
}

export function VideoInput({ onSubmit, isLoading }: VideoInputProps) {
  const [url, setUrl] = useState('');
  const [isValid, setIsValid] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const { t } = useLanguage();

  // 检查输入是否是有效的YouTube URL或视频ID
  useEffect(() => {
    const validateInput = (input: string) => {
      if (!input.trim()) {
        setIsValid(true); // 空输入不显示错误
        setErrorMsg('');
        return;
      }
      
      // 检查是否是11位的YouTube视频ID
      if (/^[a-zA-Z0-9_-]{11}$/.test(input.trim())) {
        setIsValid(true);
        setErrorMsg('');
        return;
      }
      
      // 检查是否是有效的YouTube URL
      const youtubePrefixes = [
        'youtube.com/watch?v=',
        'youtu.be/',
        'youtube.com/embed/',
        'youtube.com/v/',
      ];
      
      const hasValidPrefix = youtubePrefixes.some(prefix => 
        input.trim().includes(prefix)
      );
      
      if (hasValidPrefix) {
        setIsValid(true);
        setErrorMsg('');
      } else {
        setIsValid(false);
        setErrorMsg(t('invalidYoutubeUrl'));
      }
    };
    
    validateInput(url);
  }, [url, t]);

  // 尝试提取视频ID以便显示
  const extractVideoId = (input: string): string | null => {
    // 如果已经是11位YouTube ID
    if (/^[a-zA-Z0-9_-]{11}$/.test(input.trim())) {
      return input.trim();
    }
    
    // 尝试从URL中提取
    const regex = /(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = input.trim().match(regex);
    return match ? match[1] : null;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      // 如果输入是有效的，保存一个整洁的版本到控制台
      const videoId = extractVideoId(url.trim());
      console.log('提交的URL:', url.trim());
      console.log('提取的视频ID:', videoId);
      
      onSubmit(url.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder={t('videoInput')}
          disabled={isLoading}
          className={`w-full px-4 py-3 pr-28 text-base rounded-full border ${!isValid ? 'border-red-500 focus:ring-red-300' : 'border-neutral-300 focus:ring-neutral-300'} bg-white shadow-sm focus:ring-2 focus:border-transparent transition-all duration-200 outline-none disabled:bg-neutral-100 disabled:text-neutral-400`}
        />
        <button
          type="submit"
          disabled={isLoading || !url.trim() || !isValid}
          className="absolute right-1.5 top-1/2 -translate-y-1/2 px-5 py-2 rounded-full bg-black text-white font-medium text-sm hover:opacity-80 transition-opacity focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-black disabled:bg-neutral-300 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <div className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{t('processing')}</span>
            </div>
          ) : (
            t('summarize')
          )}
        </button>
      </div>
      
      {!isValid && (
        <div className="mt-2 text-xs text-red-500">
          {errorMsg}
        </div>
      )}
      
      <div className="mt-2 text-center text-xs text-neutral-500">
        {extractVideoId(url) ? 
          `${t('videoId')}: ${extractVideoId(url)}` : 
          t('pasteYoutubeUrl')}
      </div>
    </form>
  );
} 