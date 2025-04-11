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
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {t('summaryType')}
      </label>
      <div className="flex space-x-4">
        <label className={`inline-flex items-center ${disabled ? 'opacity-50' : ''}`}>
          <input
            type="radio"
            value="short"
            checked={selectedType === 'short'}
            onChange={() => onChange('short')}
            disabled={disabled}
            className="form-radio h-4 w-4 text-indigo-600 transition duration-150 ease-in-out"
          />
          <span className="ml-2">{t('shortSummary')}</span>
        </label>
        <label className={`inline-flex items-center ${disabled ? 'opacity-50' : ''}`}>
          <input
            type="radio"
            value="detailed"
            checked={selectedType === 'detailed'}
            onChange={() => onChange('detailed')}
            disabled={disabled}
            className="form-radio h-4 w-4 text-indigo-600 transition duration-150 ease-in-out"
          />
          <span className="ml-2">{t('detailedSummary')}</span>
        </label>
      </div>
    </div>
  );
}; 