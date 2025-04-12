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
  
  // 处理摘要文本，增强时间戳的显示效果
  const formatSummary = (text: string) => {
    // 使用正则表达式匹配时间戳格式，如 "0:00 - "
    const parts = text.split(/(\d+:\d+)\s*-\s*/);
    
    if (parts.length <= 1) {
      // 如果没有匹配到时间戳格式，则直接返回原文本
      return <p className="whitespace-pre-wrap">{text}</p>;
    }
    
    const elements = [];
    let i = 0;
    
    while (i < parts.length) {
      if (i % 2 === 0) {
        // 这是常规文本或段落标题
        if (parts[i].trim()) {
          elements.push(
            <p key={`text-${i}`} className="mb-4">
              {parts[i]}
            </p>
          );
        }
      } else {
        // 这是时间戳
        const timestamp = parts[i];
        const content = parts[i + 1] || '';
        
        elements.push(
          <div key={`section-${i}`} className="mb-6">
            <div className="flex items-center mb-2">
              <span className="bg-indigo-100 text-indigo-800 text-sm font-medium mr-2 px-2.5 py-0.5 rounded">
                {timestamp}
              </span>
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
        
        i++; // 跳过下一个部分，因为我们已经处理了
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
        {formatSummary(summary)}
      </div>
    </div>
  );
} 