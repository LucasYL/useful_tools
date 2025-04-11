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
    <form onSubmit={handleSubmit} className="mb-8">
      <div className="flex flex-col sm:flex-row gap-2">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder={t('videoInput')}
          disabled={isLoading}
          className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100 disabled:text-gray-500"
        />
        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="bg-indigo-600 text-white p-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:bg-indigo-300"
        >
          {t('summarize')}
        </button>
      </div>
    </form>
  );
} 