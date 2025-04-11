'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

interface VideoPlayerProps {
  videoId: string;
  onTimeUpdate?: (time: number) => void;
}

// Define a global declaration for YouTube IFrame API
declare global {
  interface Window {
    YT: any;
    onYouTubeIframeAPIReady: () => void;
  }
}

export function VideoPlayer({ videoId, onTimeUpdate }: VideoPlayerProps) {
  const playerRef = useRef<any>(null);
  const [isAPIReady, setIsAPIReady] = useState(false);
  const playerDivRef = useRef<HTMLDivElement>(null);
  const timeUpdateIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Load YouTube API
  useEffect(() => {
    // If script is already there, don't add it again
    if (document.getElementById('youtube-api')) {
      if (window.YT && window.YT.Player) {
        setIsAPIReady(true);
      }
      return;
    }

    // Create script element
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    tag.id = 'youtube-api';
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);

    // Define callback
    window.onYouTubeIframeAPIReady = () => {
      setIsAPIReady(true);
    };

    // Cleanup
    return () => {
      // Can't remove script tag because it might be used by other components
      window.onYouTubeIframeAPIReady = () => {};
    };
  }, []);

  // Initialize player when API is ready
  useEffect(() => {
    if (!isAPIReady || !videoId || !playerDivRef.current) return;

    playerRef.current = new window.YT.Player(playerDivRef.current, {
      videoId: videoId,
      height: '360',
      width: '640',
      playerVars: {
        autoplay: 0,
        rel: 0,
        modestbranding: 1,
      },
      events: {
        onStateChange: (event: any) => {
          // YouTube player states: -1 (unstarted), 0 (ended), 1 (playing), 2 (paused), 3 (buffering), 5 (video cued)
          if (event.data === 1 && onTimeUpdate) { // Playing
            // Create interval to track playback time
            if (timeUpdateIntervalRef.current === null) {
              timeUpdateIntervalRef.current = setInterval(() => {
                const currentTime = playerRef.current.getCurrentTime();
                onTimeUpdate(currentTime);
              }, 500); // Update every 500ms
            }
          } else if (event.data !== 1 && timeUpdateIntervalRef.current !== null) {
            // If not playing, clear the interval
            clearInterval(timeUpdateIntervalRef.current);
            timeUpdateIntervalRef.current = null;
          }
        }
      }
    });

    return () => {
      if (timeUpdateIntervalRef.current) {
        clearInterval(timeUpdateIntervalRef.current);
        timeUpdateIntervalRef.current = null;
      }
      if (playerRef.current) {
        playerRef.current.destroy();
      }
    };
  }, [isAPIReady, videoId, onTimeUpdate]);

  return (
    <div className="flex justify-center mt-8">
      <div ref={playerDivRef} id="youtube-player" />
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
  const [player, setPlayer] = useState<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { t } = useLanguage();

  // Format time in MM:SS format
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // Initialize YouTube API
  useEffect(() => {
    // If we already have the API and player instance, don't recreate
    if (window.YT && window.YT.Player && player) return;

    // Create script element if needed
    if (!document.getElementById('youtube-api')) {
      const tag = document.createElement('script');
      tag.src = 'https://www.youtube.com/iframe_api';
      tag.id = 'youtube-api';
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);
    }

    // Define callback
    window.onYouTubeIframeAPIReady = () => {
      if (!document.getElementById('hidden-player')) {
        // Create hidden player element if it doesn't exist
        const playerElement = document.createElement('div');
        playerElement.id = 'hidden-player';
        playerElement.style.display = 'none';
        document.body.appendChild(playerElement);
      }

      // Initialize player
      const newPlayer = new window.YT.Player('hidden-player', {
        videoId: videoId,
        events: {
          onReady: () => {
            setPlayer(newPlayer);
          },
        },
      });
    };

    // If API is already loaded, initialize player immediately
    if (window.YT && window.YT.Player) {
      window.onYouTubeIframeAPIReady();
    }

    // Cleanup
    return () => {
      // Don't destroy player as it might be used by other components
    };
  }, [videoId]);

  // Function to seek to a specific time
  const seekTo = (time: number) => {
    if (player && typeof onSeek === 'function') {
      onSeek(time);
    } else if (player) {
      // If no external handler, use the hidden player
      player.seekTo(time, true);
      
      // Find the closest visible player on the page and seek it too
      const visiblePlayer = document.querySelector('iframe[src*="youtube.com"]');
      if (visiblePlayer && (visiblePlayer as any).contentWindow) {
        try {
          const message = JSON.stringify({
            event: 'command',
            func: 'seekTo',
            args: [time, true],
          });
          (visiblePlayer as any).contentWindow.postMessage(message, '*');
        } catch (e) {
          console.error('Error seeking visible player:', e);
        }
      }
    }
  };

  // Scroll to current timestamp
  useEffect(() => {
    const highlightCurrentTimestamp = () => {
      if (!player || !containerRef.current) return;
      
      const currentTime = player.getCurrentTime();
      
      // Find the current transcript entry
      const currentEntry = transcript.find((entry, index) => {
        const nextEntry = transcript[index + 1];
        if (!nextEntry) return entry.start <= currentTime;
        return entry.start <= currentTime && nextEntry.start > currentTime;
      });
      
      if (currentEntry) {
        const entryElement = document.querySelector(`[data-start="${currentEntry.start}"]`);
        if (entryElement) {
          // Remove highlight from all entries
          document.querySelectorAll('.transcript-entry').forEach(el => {
            el.classList.remove('bg-primary-50', 'border-primary-200');
          });
          
          // Add highlight to current entry
          entryElement.classList.add('bg-primary-50', 'border-primary-200');
          
          // Scroll into view if needed
          if (containerRef.current) {
            const container = containerRef.current;
            const elementTop = (entryElement as HTMLElement).offsetTop;
            const containerTop = container.scrollTop;
            const containerBottom = containerTop + container.clientHeight;
            
            if (elementTop < containerTop || elementTop > containerBottom - 100) {
              container.scrollTop = elementTop - container.clientHeight / 2;
            }
          }
        }
      }
    };
    
    const interval = setInterval(highlightCurrentTimestamp, 1000);
    return () => clearInterval(interval);
  }, [player, transcript]);

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