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
      return <p className="whitespace-pre-wrap leading-relaxed text-neutral-800">{text}</p>;
    }
    
    const elements = [];
    let i = 0;
    
    while (i < parts.length) {
      if (i % 2 === 0) {
        // This is regular text or paragraph heading
        if (parts[i].trim()) {
          elements.push(
            <p key={`text-${i}`} className="mb-5 text-neutral-800 leading-relaxed">
              {parts[i]}
            </p>
          );
        }
      } else {
        // This is a timestamp
        const timestamp = parts[i];
        const content = parts[i + 1] || '';
        
        elements.push(
          <div key={`section-${i}`} className="mb-7 animate-fadeIn">
            <div className="flex items-center mb-3">
              <button
                onClick={() => handleTimestampClick(timestamp)}
                className="bg-blue-50 text-blue-700 text-xs font-semibold mr-3 px-3 py-1.5 rounded-full hover:bg-blue-100 transition-colors flex items-center cursor-pointer shadow-sm"
                title={t('timestampJumpTooltip')}
              >
                <span className="mr-1.5">▶</span>
                {timestamp}
              </button>
              <h4 className="font-semibold text-neutral-900 text-base">
                {content.split('\n')[0]?.trim()}
              </h4>
            </div>
            <div className="pl-5 border-l-2 border-neutral-200 hover:border-blue-300 transition-colors">
              {content.split('\n').slice(1).map((line, lineIndex) => (
                <p key={`line-${i}-${lineIndex}`} className="mb-3 text-neutral-700 leading-relaxed">
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
    
    return <div className="space-y-2">{elements}</div>;
  };
  
  return (
    <>
      {videoId && onSeek && (
        <div className="mb-5 flex items-center text-xs text-neutral-600 bg-blue-50 p-3 rounded-lg border border-blue-100 shadow-sm">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <span className="font-medium">{t('clickTimestampToJump')}</span>
        </div>
      )}
      
      <div className="prose prose-neutral max-w-none">
        {formatSummary(summary)}
      </div>
    </>
  );
} 