'use client';

import React from 'react';
import { useLanguage } from '@/contexts/LanguageContext';

export interface Language {
  code: string;
  name: string;
}

interface LanguageSelectorProps {
  languages?: Language[];
  selectedLanguage: string;
  onChange: (languageCode: string) => void;
  disabled?: boolean;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  languages = [
    { code: 'en', name: 'English' },
    { code: 'zh', name: '中文' }
  ],
  selectedLanguage,
  onChange,
  disabled = false,
}) => {
  const { t } = useLanguage();
  
  return (
    <div className="mb-4">
      <label htmlFor="language-selector" className="block text-sm font-medium text-gray-700 mb-1">
        {t('language')}
      </label>
      <select
        id="language-selector"
        value={selectedLanguage}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm disabled:bg-gray-100 disabled:text-gray-500"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
}; 