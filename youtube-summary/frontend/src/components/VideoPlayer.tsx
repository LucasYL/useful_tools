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

  // Listen for messages from iframe
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // Only process messages from YouTube
      if (event.origin !== 'https://www.youtube.com') return;
      
      try {
        const data = JSON.parse(event.data);
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
    
    return () => {
      window.removeEventListener('message', handleMessage);
      if (playerCheckIntervalRef.current) {
        clearInterval(playerCheckIntervalRef.current);
        playerCheckIntervalRef.current = null;
      }
    };
  }, [videoId, onTimeUpdate, t]);

  // Handle loading timeout
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (!isPlayerReady) {
        console.warn('YouTube player failed to load within timeout');
        // Don't set error, continue trying to load video
      }
    }, 10000);

    return () => clearTimeout(timeoutId);
  }, [isPlayerReady]);

  // Error handling
  useEffect(() => {
    if (!videoId) {
      setPlayerError(t('invalidVideoId'));
    } else {
      setPlayerError(null);
    }
  }, [videoId, t]);

  // Embed video using iframe
  return (
    <div className="flex flex-col items-center mt-8">
      <h2 className="mb-4 text-xl font-bold">{t('video')}</h2>
      
      {!videoId && (
        <div className="w-[640px] h-[360px] bg-gray-100 flex items-center justify-center">
          <div className="text-gray-600">{t('noVideoId')}</div>
        </div>
      )}
      
      {videoId && !isPlayerReady && !playerError && (
        <div className="w-[640px] h-[360px] bg-gray-100 flex items-center justify-center">
          <div className="flex flex-col items-center text-gray-600">
            <p className="mb-4">{t('loadingPlayer')}</p>
            <p className="text-sm">{t('videoLoadingFallback')}
              <a 
                href={`https://www.youtube.com/watch?v=${videoId}`} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="text-blue-500 underline ml-1"
              >
                {t('watchOnYouTube')}
              </a>
            </p>
          </div>
        </div>
      )}
      
      {playerError && (
        <div className="w-[640px] h-[360px] bg-red-50 flex items-center justify-center">
          <div className="text-red-600 text-center p-4">
            <p className="font-bold mb-2">{t('videoLoadError')}</p>
            <p className="mb-4">{playerError}</p>
            <a 
              href={`https://www.youtube.com/watch?v=${videoId}`} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              {t('watchOnYouTube')}
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
            // iframe load completion doesn't mean player is ready, so we still need to wait for onReady message
            setTimeout(() => {
              if (!isPlayerReady) {
                setIsPlayerReady(true); // If onReady message not received after 3 seconds, force display
              }
            }, 3000);
          }}
        ></iframe>
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
    const handleTimeUpdate = (event: MessageEvent) => {
      if (event.origin !== 'https://www.youtube.com') return;
      
      try {
        const data = JSON.parse(event.data);
        if (data.event === 'infoDelivery' && data.info && typeof data.info.currentTime === 'number') {
          setCurrentPlaybackTime(data.info.currentTime);
        }
      } catch (e) {
        // Ignore non-JSON messages
      }
    };
    
    window.addEventListener('message', handleTimeUpdate);
    return () => {
      window.removeEventListener('message', handleTimeUpdate);
    };
  }, []);

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <h2 className="mb-4 text-xl font-bold">{t('transcript')}</h2>
      {transcript && transcript.length > 0 ? (
        <div 
          ref={containerRef}
          className="p-4 bg-white rounded-lg shadow max-h-96 overflow-y-auto"
        >
          {transcript.map((entry, index) => {
            // Check if this is the currently playing segment
            const isCurrentlyPlaying = currentPlaybackTime >= entry.start && 
                                      currentPlaybackTime < (entry.start + entry.duration);
            
            return (
              <div 
                key={index} 
                className={`mb-2 p-2 border-l-4 transcript-entry hover:bg-gray-50 cursor-pointer transition duration-200 ${
                  isCurrentlyPlaying ? 'border-blue-500 bg-blue-50' : 'border-transparent'
                }`}
                onClick={() => seekTo(entry.start)}
                data-start={entry.start}
              >
                <span className={`font-mono ${
                  isCurrentlyPlaying ? 'text-blue-600 font-bold' : 'text-gray-500'
                }`}>
                  {formatTime(entry.start)}
                </span>
                <p className={isCurrentlyPlaying ? 'font-medium' : ''}>{entry.text}</p>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="p-4 bg-gray-100 text-gray-600 rounded-lg text-center">
          {t('transcriptUnavailable')}
        </div>
      )}
    </div>
  );
} 