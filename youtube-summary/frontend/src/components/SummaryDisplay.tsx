'use client';

import React from 'react';
import { useLanguage } from '@/contexts/LanguageContext';

interface SummaryDisplayProps {
  summary: string;
  title: string;
  summaryType: string;
  videoId?: string;
  onSeek?: (time: number) => void;
}

export function SummaryDisplay({ summary, title, summaryType, videoId, onSeek }: SummaryDisplayProps) {
  const { t } = useLanguage();
  
  // Convert timestamp to seconds
  const timeToSeconds = (timeStr: string): number => {
    const parts = timeStr.split(':');
    if (parts.length === 2) {
      return parseInt(parts[0]) * 60 + parseInt(parts[1]);
    } else if (parts.length === 3) {
      return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
    }
    return 0;
  };
  
  // Handle timestamp click event
  const handleTimestampClick = (timestamp: string) => {
    if (onSeek) {
      const seconds = timeToSeconds(timestamp);
      onSeek(seconds);
    }
  };
  
  // Format summary text with enhanced timestamp display
  const formatSummary = (text: string) => {
    // Use regex to match timestamp format like "0:00 - "
    const parts = text.split(/(\d+:\d+)\s*-\s*/);
    
    if (parts.length <= 1) {
      // If no timestamp format is matched, return the original text
      return <p className="whitespace-pre-wrap">{text}</p>;
    }
    
    const elements = [];
    let i = 0;
    
    while (i < parts.length) {
      if (i % 2 === 0) {
        // This is regular text or paragraph heading
        if (parts[i].trim()) {
          elements.push(
            <p key={`text-${i}`} className="mb-4">
              {parts[i]}
            </p>
          );
        }
      } else {
        // This is a timestamp
        const timestamp = parts[i];
        const content = parts[i + 1] || '';
        
        elements.push(
          <div key={`section-${i}`} className="mb-6">
            <div className="flex items-center mb-2">
              <button
                onClick={() => handleTimestampClick(timestamp)}
                className="bg-indigo-100 text-indigo-800 text-sm font-medium mr-2 px-2.5 py-0.5 rounded hover:bg-indigo-200 transition-colors flex items-center cursor-pointer"
                title={t('timestampJumpTooltip')}
              >
                <span className="mr-1">▶</span>
                {timestamp}
              </button>
              <h4 className="font-semibold">
                {content.split('\n')[0]?.trim()}
              </h4>
            </div>
            <div className="pl-4 border-l-2 border-indigo-100">
              {content.split('\n').slice(1).map((line, lineIndex) => (
                <p key={`line-${i}-${lineIndex}`} className="mb-2">
                  {line}
                </p>
              ))}
            </div>
          </div>
        );
        
        i++; // Skip the next part since we've already processed it
      }
      
      i++;
    }
    
    return <div>{elements}</div>;
  };
  
  return (
    <div className="max-w-2xl mx-auto mt-8">
      <div className="p-4 bg-white rounded-lg shadow">
        <h2 className="mb-4 text-xl font-bold">
          {summaryType === 'detailed' ? t('detailedSummary') : t('shortSummary')}
        </h2>
        <h3 className="mb-4 text-lg font-semibold text-gray-700">{title}</h3>
        <div className="mb-2 text-sm text-gray-500">
          {videoId && onSeek ? (
            <p>{t('clickTimestampToJump')}</p>
          ) : null}
        </div>
        {formatSummary(summary)}
      </div>
    </div>
  );
} 