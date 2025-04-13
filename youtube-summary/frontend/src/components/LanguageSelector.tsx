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
    <div>
      <span className="block text-xs font-medium text-neutral-500 mb-2">
        {t('language')}
      </span>
      <div className="inline-flex items-center p-1 bg-neutral-100 rounded-full">
        {languages.map((lang) => (
          <button
            key={lang.code}
            type="button"
            onClick={() => onChange(lang.code)}
            disabled={disabled}
            className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
              selectedLanguage === lang.code
                ? 'bg-white shadow-sm text-black'
                : 'text-neutral-500 hover:text-neutral-700'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {lang.name}
          </button>
        ))}
      </div>
    </div>
  );
}; 