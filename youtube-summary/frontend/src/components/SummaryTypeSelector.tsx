'use client';

import React from 'react';
import { useLanguage } from '@/contexts/LanguageContext';

export type SummaryType = 'short' | 'detailed';

interface SummaryTypeSelectorProps {
  selectedType: SummaryType;
  onChange: (type: SummaryType) => void;
  disabled?: boolean;
}

export const SummaryTypeSelector: React.FC<SummaryTypeSelectorProps> = ({
  selectedType,
  onChange,
  disabled = false,
}) => {
  const { t } = useLanguage();

  return (
    <div>
      <span className="block text-xs font-medium text-neutral-500 mb-2">
        {t('summaryType')}
      </span>
      <div className="inline-flex items-center p-1 bg-neutral-100 rounded-full">
        <button
          type="button"
          onClick={() => onChange('short')}
          disabled={disabled}
          className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
            selectedType === 'short'
              ? 'bg-white shadow-sm text-black'
              : 'text-neutral-500 hover:text-neutral-700'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {t('shortSummary')}
        </button>
        <button
          type="button"
          onClick={() => onChange('detailed')}
          disabled={disabled}
          className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
            selectedType === 'detailed'
              ? 'bg-white shadow-sm text-black'
              : 'text-neutral-500 hover:text-neutral-700'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {t('detailedSummary')}
        </button>
      </div>
    </div>
  );
}; 