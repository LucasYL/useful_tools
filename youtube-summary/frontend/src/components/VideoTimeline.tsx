'use client';

import React from 'react';
import { useLanguage } from '@/contexts/LanguageContext';

interface Chapter {
  start_time: number;
  title: string;
}

interface VideoTimelineProps {
  chapters: Chapter[];
  onSeek: (time: number) => void;
  currentTime?: number;
}

export const VideoTimeline: React.FC<VideoTimelineProps> = ({
  chapters,
  onSeek,
  currentTime = 0,
}) => {
  const { t } = useLanguage();
  
  // 格式化时间为 MM:SS 格式
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // 计算每个章节应该占据的百分比宽度
  const calculateChapterWidths = () => {
    if (!chapters || chapters.length === 0) return [];

    const totalDuration = chapters.reduce((max, chapter, index) => {
      const nextChapter = chapters[index + 1];
      const chapterDuration = nextChapter
        ? nextChapter.start_time - chapter.start_time
        : 3600; // 假设最后一章节持续1小时(如果没有明确的结束时间)
      return Math.max(max, chapter.start_time + chapterDuration);
    }, 0);

    return chapters.map((chapter, index) => {
      const nextChapter = chapters[index + 1];
      const duration = nextChapter
        ? nextChapter.start_time - chapter.start_time
        : totalDuration - chapter.start_time;
      return {
        ...chapter,
        width: (duration / totalDuration) * 100,
        isActive: currentTime >= chapter.start_time && 
                  (!nextChapter || currentTime < nextChapter.start_time)
      };
    });
  };

  const chaptersWithWidth = calculateChapterWidths();

  // 如果没有章节，不渲染组件
  if (!chapters || chapters.length === 0) {
    return null;
  }

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <h2 className="mb-4 text-xl font-bold">{t('videoChapters')}</h2>
      <div className="mb-2 h-6 flex w-full bg-gray-200 rounded overflow-hidden">
        {chaptersWithWidth.map((chapter, index) => (
          <div
            key={index}
            className={`h-full flex-shrink-0 cursor-pointer transition-all 
                      ${chapter.isActive ? 'bg-indigo-500' : 'bg-indigo-300 hover:bg-indigo-400'}`}
            style={{ width: `${chapter.width}%` }}
            onClick={() => onSeek(chapter.start_time)}
            title={`${chapter.title} (${formatTime(chapter.start_time)})`}
          />
        ))}
      </div>
      <div className="space-y-2">
        {chapters.map((chapter, index) => (
          <div 
            key={index} 
            className={`p-2 flex items-center cursor-pointer hover:bg-gray-50 rounded
                       ${currentTime >= chapter.start_time && 
                        (index === chapters.length - 1 || currentTime < chapters[index + 1].start_time) 
                        ? 'bg-indigo-50 border-l-4 border-indigo-500' 
                        : 'border-l-4 border-transparent'}`}
            onClick={() => onSeek(chapter.start_time)}
          >
            <span className="text-gray-500 font-mono min-w-[50px]">
              {formatTime(chapter.start_time)}
            </span>
            <span className="ml-4">{chapter.title}</span>
          </div>
        ))}
      </div>
    </div>
  );
}; 