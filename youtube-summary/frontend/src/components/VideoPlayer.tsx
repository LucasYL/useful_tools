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
  const [loadTimeout, setLoadTimeout] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const playerCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const { t } = useLanguage();

  // 初始化YouTube Player API
  useEffect(() => {
    // 创建YouTube API脚本
    if (!document.getElementById('youtube-api')) {
      const tag = document.createElement('script');
      tag.id = 'youtube-api';
      tag.src = 'https://www.youtube.com/iframe_api';
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);
    }
    
    // Reset states when video ID changes
    setIsPlayerReady(false);
    setPlayerError(null);
    setLoadTimeout(false);
    
    return () => {
      if (playerCheckIntervalRef.current) {
        clearInterval(playerCheckIntervalRef.current);
        playerCheckIntervalRef.current = null;
      }
    };
  }, [videoId]);

  // Listen for messages from iframe
  useEffect(() => {
    if (!videoId) return;
    
    const handleMessage = (event: MessageEvent) => {
      // Process messages from YouTube
      if (event.origin !== 'https://www.youtube.com') return;
      
      try {
        const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
        
        // Check if it's a YouTube API event
        if (data.event === 'onStateChange' && data.info === 1 && onTimeUpdate) {
          // Playback state changed to playing
          if (playerCheckIntervalRef.current === null && iframeRef.current) {
            playerCheckIntervalRef.current = setInterval(() => {
              // Send getCurrentTime message to iframe
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
          setLoadTimeout(false);
        } else if (data.event === 'onError') {
          setPlayerError(t('videoLoadError'));
        } else if (data.event === 'infoDelivery' && data.info && typeof data.info.currentTime === 'number') {
          // Received current time information
          if (onTimeUpdate) {
            onTimeUpdate(data.info.currentTime);
          }
        }
      } catch (e) {
        // Ignore non-JSON messages
      }
    };

    window.addEventListener('message', handleMessage);
    
    // 设置超时检测
    const timeoutId = setTimeout(() => {
      if (!isPlayerReady) {
        console.warn('YouTube player failed to load within timeout');
        setLoadTimeout(true);
      }
    }, 10000);
    
    return () => {
      window.removeEventListener('message', handleMessage);
      clearTimeout(timeoutId);
      if (playerCheckIntervalRef.current) {
        clearInterval(playerCheckIntervalRef.current);
        playerCheckIntervalRef.current = null;
      }
    };
  }, [videoId, onTimeUpdate, t, isPlayerReady]);

  // Error handling
  useEffect(() => {
    if (!videoId) {
      setPlayerError(t('invalidVideoId'));
    } else {
      setPlayerError(null);
    }
  }, [videoId, t]);

  // 手动强制加载视频
  const handleRetryLoad = () => {
    if (!videoId || !iframeRef.current || !iframeRef.current.contentWindow) return;
    
    // 重新加载iframe
    const currentSrc = iframeRef.current.src;
    iframeRef.current.src = '';
    setTimeout(() => {
      if (iframeRef.current) {
        iframeRef.current.src = currentSrc;
      }
    }, 100);
  };

  // Embed video using iframe
  return (
    <div className="flex flex-col w-full">
      <h2 className="text-2xl font-semibold mb-6 text-neutral-800">{t('video')}</h2>
      
      {!videoId && (
        <div className="aspect-video w-full rounded-xl bg-neutral-50 flex items-center justify-center overflow-hidden shadow-inner border border-neutral-100">
          <div className="text-neutral-500 p-8 text-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto mb-4 text-neutral-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <p className="text-lg">{t('noVideoId')}</p>
          </div>
        </div>
      )}
      
      {videoId && !isPlayerReady && !playerError && (
        <div className="aspect-video w-full rounded-xl bg-neutral-50 flex items-center justify-center overflow-hidden shadow-inner border border-neutral-100">
          <div className="flex flex-col items-center text-neutral-500 p-8 text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-neutral-300 mb-6"></div>
            <p className="font-medium mb-4 text-lg">{t('loadingPlayer')}</p>
            {loadTimeout && (
              <>
                <p className="text-base text-amber-600 mb-5">
                  {t('playerLoadingTimeout')}
                </p>
                <button 
                  onClick={handleRetryLoad}
                  className="px-5 py-3 bg-neutral-200 text-neutral-700 rounded-lg hover:bg-neutral-300 transition-colors mb-5 text-base font-medium shadow-sm"
                >
                  {t('retryLoading')}
                </button>
              </>
            )}
            <p className="text-base">
              {t('videoLoadingFallback')}
              <a 
                href={`https://www.youtube.com/watch?v=${videoId}`} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="text-blue-500 hover:underline ml-1"
              >
                {t('watchOnYouTube')}
              </a>
            </p>
          </div>
        </div>
      )}
      
      {playerError && (
        <div className="aspect-video w-full rounded-xl bg-red-50 flex items-center justify-center overflow-hidden shadow-inner border border-red-100">
          <div className="text-red-500 p-8 text-center max-w-md">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto mb-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="font-medium mb-4 text-xl">{t('videoLoadError')}</p>
            <p className="mb-6 text-base">{playerError}</p>
            <a 
              href={`https://www.youtube.com/watch?v=${videoId}`} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="inline-block px-5 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors shadow-sm font-medium text-base"
            >
              {t('watchOnYouTube')}
            </a>
          </div>
        </div>
      )}
      
      {videoId && (
        <div className={`aspect-video w-full rounded-xl overflow-hidden bg-black shadow-md ${!isPlayerReady && playerError === null ? 'hidden' : ''}`}>
          <iframe 
            ref={iframeRef}
            width="100%" 
            height="100%" 
            src={`https://www.youtube.com/embed/${videoId}?enablejsapi=1&origin=${window.location.origin}&rel=0&modestbranding=1&fs=1`}
            title="YouTube video player" 
            frameBorder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            onLoad={() => {
              // iframe load completion doesn't mean player is ready, so we still need to wait for onReady message
              setTimeout(() => {
                if (!isPlayerReady) {
                  setIsPlayerReady(true); // If onReady message not received after 3 seconds, force display
                }
              }, 3000);
            }}
          ></iframe>
        </div>
      )}
    </div>
  );
}

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
  const [currentPlaybackTime, setCurrentPlaybackTime] = useState<number>(0);

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
      setCurrentPlaybackTime(time);
    }
  };

  // Use useEffect to track current playback time updates
  useEffect(() => {
    // Listen for video playback update messages
    const handleTimeUpdate = (time: number) => {
      setCurrentPlaybackTime(time);
    };
    
    // Auto-scroll to the currently playing segment
    if (containerRef.current && transcript.length > 0) {
      const currentEntry = transcript.find(
        entry => currentPlaybackTime >= entry.start && 
                currentPlaybackTime < (entry.start + entry.duration)
      );
      
      if (currentEntry) {
        const entryElement = containerRef.current.querySelector(
          `[data-start="${currentEntry.start}"]`
        ) as HTMLElement;
        
        if (entryElement) {
          entryElement.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'nearest'
          });
        }
      }
    }
    
    // Add listener for time updates from the VideoPlayer component
    if (onSeek) {
      window.addEventListener('message', (event) => {
        if (event.origin !== 'https://www.youtube.com') return;
        
        try {
          const data = JSON.parse(event.data);
          if (data.event === 'infoDelivery' && data.info && typeof data.info.currentTime === 'number') {
            handleTimeUpdate(data.info.currentTime);
          }
        } catch (e) {
          // Ignore non-JSON messages
        }
      });
    }
    
    return () => {
      if (onSeek) {
        window.removeEventListener('message', () => {});
      }
    };
  }, [currentPlaybackTime, transcript, onSeek]);

  return (
    <div>
      <h3 className="text-lg font-medium mb-3">{t('transcript')}</h3>
      {transcript && transcript.length > 0 ? (
        <div 
          ref={containerRef}
          className="p-4 bg-white rounded-xl border border-neutral-200 shadow-sm max-h-96 overflow-y-auto"
        >
          {transcript.map((entry, index) => {
            // Check if this is the currently playing segment
            const isCurrentlyPlaying = currentPlaybackTime >= entry.start && 
                                      currentPlaybackTime < (entry.start + entry.duration);
            
            return (
              <div 
                key={index} 
                className={`mb-2 p-2 border-l-2 transcript-entry hover:bg-neutral-50 cursor-pointer transition duration-200 ${
                  isCurrentlyPlaying ? 'border-black bg-neutral-100' : 'border-transparent'
                }`}
                onClick={() => seekTo(entry.start)}
                data-start={entry.start}
              >
                <span className={`font-mono text-sm ${
                  isCurrentlyPlaying ? 'text-black font-medium' : 'text-neutral-500'
                }`}>
                  {formatTime(entry.start)}
                </span>
                <p className={`text-sm ${isCurrentlyPlaying ? 'font-medium text-black' : 'text-neutral-700'}`}>{entry.text}</p>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="p-4 bg-neutral-100 text-neutral-500 rounded-xl text-center text-sm border border-neutral-200">
          {t('transcriptUnavailable')}
        </div>
      )}
    </div>
  );
} 