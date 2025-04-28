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
            <p key={`text-${i}`} className="mb-4 text-neutral-700">
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
                className="bg-neutral-100 text-neutral-700 text-sm font-medium mr-2 px-2.5 py-1 rounded-full hover:bg-neutral-200 transition-colors flex items-center cursor-pointer"
                title={t('timestampJumpTooltip')}
              >
                <span className="mr-1">▶</span>
                {timestamp}
              </button>
              <h4 className="font-semibold text-neutral-900">
                {content.split('\n')[0]?.trim()}
              </h4>
            </div>
            <div className="pl-4 border-l-2 border-neutral-200">
              {content.split('\n').slice(1).map((line, lineIndex) => (
                <p key={`line-${i}-${lineIndex}`} className="mb-2 text-neutral-700">
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
    <>
      {videoId && onSeek && (
        <div className="mb-4 flex items-center text-xs text-neutral-500 bg-neutral-50 p-2 rounded-lg">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <span>{t('clickTimestampToJump')}</span>
        </div>
      )}
      
      <div className="prose prose-neutral max-w-none">
        {formatSummary(summary)}
      </div>
    </>
  );
} 