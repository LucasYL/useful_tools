'use client';

import { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';

interface VideoInputProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
}

export function VideoInput({ onSubmit, isLoading }: VideoInputProps) {
  const [url, setUrl] = useState('');
  const { t } = useLanguage();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
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
          className="w-full px-4 py-3 pr-28 text-base rounded-full border border-neutral-300 bg-white shadow-sm focus:ring-2 focus:ring-neutral-300 focus:border-transparent transition-all duration-200 outline-none disabled:bg-neutral-100 disabled:text-neutral-400"
        />
        <button
          type="submit"
          disabled={isLoading || !url.trim()}
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
      <div className="mt-2 text-center text-xs text-neutral-500">
        {t('pasteYoutubeUrl')}
      </div>
    </form>
  );
} 