'use client';

import React from 'react';
import { useLanguage } from '@/contexts/LanguageContext';

interface SummaryDisplayProps {
  summary: string;
  title: string;
  summaryType: string;
}

export function SummaryDisplay({ summary, title, summaryType }: SummaryDisplayProps) {
  const { t } = useLanguage();
  
  return (
    <div className="max-w-2xl mx-auto mt-8">
      <div className="p-4 bg-white rounded-lg shadow">
        <h2 className="mb-4 text-xl font-bold">
          {summaryType === 'detailed' ? t('detailedSummary') : t('shortSummary')}
        </h2>
        <h3 className="mb-2 text-lg font-semibold text-gray-700">{title}</h3>
        <p className="whitespace-pre-wrap">
          {summary}
        </p>
      </div>
    </div>
  );
} 