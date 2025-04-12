'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

interface VideoPlayerProps {
  videoId: string;
  onTimeUpdate?: (time: number) => void;
}

export function VideoPlayer({ videoId, onTimeUpdate }: VideoPlayerProps) {
  const [isPlayerReady, setIsPlayerReady] = useState(false);
  const [playerError, setPlayerError] = useState<string | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const playerCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const { t } = useLanguage();

  // 监听来自iframe的消息
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // 只处理来自YouTube的消息
      if (event.origin !== 'https://www.youtube.com') return;
      
      try {
        const data = JSON.parse(event.data);
        // 检查是否是YouTube API事件
        if (data.event === 'onStateChange' && data.info === 1 && onTimeUpdate) {
          // 播放状态变为播放中
          if (playerCheckIntervalRef.current === null && iframeRef.current) {
            playerCheckIntervalRef.current = setInterval(() => {
              // 发送getCurrentTime消息到iframe
              iframeRef.current?.contentWindow?.postMessage(
                JSON.stringify({
                  event: 'command',
                  func: 'getCurrentTime',
                  args: []
                }),
                '*'
              );
            }, 500);
          }
        } else if (data.event === 'onReady') {
          setIsPlayerReady(true);
        } else if (data.event === 'onError') {
          setPlayerError('视频无法加载，请尝试直接在YouTube上观看');
        } else if (data.event === 'infoDelivery' && data.info && typeof data.info.currentTime === 'number') {
          // 接收到当前时间信息
          if (onTimeUpdate) {
            onTimeUpdate(data.info.currentTime);
          }
        }
      } catch (e) {
        // 忽略非JSON消息
      }
    };

    window.addEventListener('message', handleMessage);
    
    return () => {
      window.removeEventListener('message', handleMessage);
      if (playerCheckIntervalRef.current) {
        clearInterval(playerCheckIntervalRef.current);
        playerCheckIntervalRef.current = null;
      }
    };
  }, [videoId, onTimeUpdate]);

  // 处理加载超时
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (!isPlayerReady) {
        console.warn('YouTube player failed to load within timeout');
        // 不设置错误，继续尝试加载视频
      }
    }, 10000);

    return () => clearTimeout(timeoutId);
  }, [isPlayerReady]);

  // 错误处理
  useEffect(() => {
    if (!videoId) {
      setPlayerError('无效的视频ID');
    } else {
      setPlayerError(null);
    }
  }, [videoId]);

  // 直接使用iframe嵌入视频
  return (
    <div className="flex flex-col items-center mt-8">
      <h2 className="mb-4 text-xl font-bold">视频</h2>
      
      {!videoId && (
        <div className="w-[640px] h-[360px] bg-gray-100 flex items-center justify-center">
          <div className="text-gray-600">未提供视频ID</div>
        </div>
      )}
      
      {videoId && !isPlayerReady && !playerError && (
        <div className="w-[640px] h-[360px] bg-gray-100 flex items-center justify-center">
          <div className="flex flex-col items-center text-gray-600">
            <p className="mb-4">加载视频播放器中...</p>
            <p className="text-sm">如果视频无法加载，您可以
              <a 
                href={`https://www.youtube.com/watch?v=${videoId}`} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="text-blue-500 underline ml-1"
              >
                直接在YouTube上观看
              </a>
            </p>
          </div>
        </div>
      )}
      
      {playerError && (
        <div className="w-[640px] h-[360px] bg-red-50 flex items-center justify-center">
          <div className="text-red-600 text-center p-4">
            <p className="font-bold mb-2">无法加载视频</p>
            <p className="mb-4">{playerError}</p>
            <a 
              href={`https://www.youtube.com/watch?v=${videoId}`} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              在YouTube上观看
            </a>
          </div>
        </div>
      )}
      
      {videoId && (
        <iframe 
          ref={iframeRef}
          width="640" 
          height="360" 
          src={`https://www.youtube.com/embed/${videoId}?enablejsapi=1&origin=${window.location.origin}`}
          title="YouTube video player" 
          frameBorder="0" 
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className={!isPlayerReady && playerError === null ? 'hidden' : ''}
          onLoad={() => {
            // iframe加载完成不代表播放器准备好，所以我们仍然需要等待onReady消息
            setTimeout(() => {
              if (!isPlayerReady) {
                setIsPlayerReady(true); // 如果10秒后仍未收到onReady消息，则强制显示
              }
            }, 3000);
          }}
        ></iframe>
      )}
    </div>
  );
}

// TimelineViewer组件内容保持不变
// ... 现有的TimelineViewer组件代码 ...

// Enhanced TranscriptViewer with timestamp linking
interface TranscriptEntry {
  text: string;
  start: number;
  duration: number;
}

interface TimelineViewerProps {
  transcript: TranscriptEntry[];
  videoId: string;
  onSeek?: (time: number) => void;
}

export function TimelineViewer({ transcript, videoId, onSeek }: TimelineViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { t } = useLanguage();

  // Format time in MM:SS format
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // Function to seek to a specific time
  const seekTo = (time: number) => {
    if (typeof onSeek === 'function') {
      onSeek(time);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <h2 className="mb-4 text-xl font-bold">{t('transcript')}</h2>
      <div 
        ref={containerRef}
        className="p-4 bg-white rounded-lg shadow max-h-96 overflow-y-auto"
      >
        {transcript.map((entry, index) => (
          <div 
            key={index} 
            className="mb-2 p-2 border-l-4 border-transparent transcript-entry hover:bg-gray-50 cursor-pointer"
            onClick={() => seekTo(entry.start)}
            data-start={entry.start}
          >
            <span className="text-gray-500 font-mono">
              {formatTime(entry.start)}
            </span>
            <p>{entry.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
} 