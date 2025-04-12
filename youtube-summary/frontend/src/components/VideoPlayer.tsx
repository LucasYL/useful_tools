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
  const [isPlayerReady, setIsPlayerReady] = useState(false);
  const [playerError, setPlayerError] = useState<string | null>(null);
  const [apiLoadTimeout, setApiLoadTimeout] = useState(false);
  const { t } = useLanguage();

  // Load YouTube API with timeout
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    
    // If script is already there, don't add it again
    if (document.getElementById('youtube-api')) {
      if (window.YT && window.YT.Player) {
        setIsAPIReady(true);
        return;
      }
    }

    // Set timeout to detect API loading failures
    timeoutId = setTimeout(() => {
      if (!window.YT || !window.YT.Player) {
        console.error("YouTube API failed to load within timeout");
        setApiLoadTimeout(true);
      }
    }, 8000); // 8 seconds timeout
    
    // Create script element
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    tag.id = 'youtube-api';
    tag.onerror = () => {
      console.error("Failed to load YouTube API script");
      setApiLoadTimeout(true);
      clearTimeout(timeoutId);
    };
    
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);

    // Define callback
    window.onYouTubeIframeAPIReady = () => {
      setIsAPIReady(true);
      clearTimeout(timeoutId);
    };

    // Cleanup
    return () => {
      clearTimeout(timeoutId);
      // Can't remove script tag because it might be used by other components
      window.onYouTubeIframeAPIReady = () => {};
    };
  }, []);

  // Initialize player when API is ready with timeout
  useEffect(() => {
    if ((!isAPIReady && !apiLoadTimeout) || !videoId) return;
    
    if (apiLoadTimeout) {
      setPlayerError("YouTube player could not be loaded. Please try again later or watch directly on YouTube.");
      return;
    }
    
    if (!playerDivRef.current) {
      setPlayerError("Player container not found");
      return;
    }

    // Reset player state when creating a new player
    setIsPlayerReady(false);
    setPlayerError(null);
    
    // Set timeout for player initialization
    const playerInitTimeout = setTimeout(() => {
      if (!isPlayerReady) {
        setPlayerError("Player initialization timed out. Try watching directly on YouTube.");
      }
    }, 10000); // 10 seconds timeout

    try {
      // Make sure we have a fresh div for the player
      const playerContainer = playerDivRef.current;
      while (playerContainer.firstChild) {
        playerContainer.removeChild(playerContainer.firstChild);
      }
      
      playerRef.current = new window.YT.Player(playerContainer, {
        videoId: videoId,
        height: '360',
        width: '640',
        playerVars: {
          autoplay: 0,
          rel: 0,
          modestbranding: 1,
          origin: window.location.origin,
        },
        events: {
          onReady: () => {
            console.log("YouTube player ready");
            setIsPlayerReady(true);
            clearTimeout(playerInitTimeout);
          },
          onError: (event: any) => {
            console.error("YouTube player error:", event.data);
            let errorMessage = "An error occurred while loading the video.";
            
            // Map YouTube error codes to more specific messages
            switch(event.data) {
              case 2:
                errorMessage = "Invalid video ID or parameter.";
                break;
              case 5:
                errorMessage = "HTML5 player error.";
                break;
              case 100:
                errorMessage = "Video not found or has been removed.";
                break;
              case 101:
              case 150:
                errorMessage = "Video owner does not allow embedding.";
                break;
            }
            
            setPlayerError(errorMessage);
            clearTimeout(playerInitTimeout);
          },
          onStateChange: (event: any) => {
            // YouTube player states: -1 (unstarted), 0 (ended), 1 (playing), 2 (paused), 3 (buffering), 5 (video cued)
            if (event.data === 1 && onTimeUpdate) { // Playing
              // Create interval to track playback time
              if (timeUpdateIntervalRef.current === null) {
                timeUpdateIntervalRef.current = setInterval(() => {
                  if (playerRef.current && typeof playerRef.current.getCurrentTime === 'function') {
                    const currentTime = playerRef.current.getCurrentTime();
                    onTimeUpdate(currentTime);
                  }
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
    } catch (error) {
      console.error("Error initializing YouTube player:", error);
      setPlayerError("Could not initialize video player");
      clearTimeout(playerInitTimeout);
    }

    return () => {
      clearTimeout(playerInitTimeout);
      if (timeUpdateIntervalRef.current) {
        clearInterval(timeUpdateIntervalRef.current);
        timeUpdateIntervalRef.current = null;
      }
      if (playerRef.current && typeof playerRef.current.destroy === 'function') {
        try {
          playerRef.current.destroy();
        } catch (error) {
          console.error("Error destroying player:", error);
        }
      }
    };
  }, [isAPIReady, apiLoadTimeout, videoId, onTimeUpdate, isPlayerReady]);

  return (
    <div className="flex flex-col items-center mt-8">
      <h2 className="mb-4 text-xl font-bold">视频</h2>
      
      {/* Loading state */}
      {!isPlayerReady && !playerError && (
        <div className="w-[640px] h-[360px] bg-gray-100 flex items-center justify-center">
          <div className="flex flex-col items-center text-gray-600">
            <p className="mb-4">加载视频播放器中...</p>
            <p className="text-sm">如果视频无法加载，您可以<a href={`https://www.youtube.com/watch?v=${videoId}`} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">直接在YouTube上观看</a></p>
          </div>
        </div>
      )}
      
      {/* Error state */}
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
      
      {/* YouTube iframe will be inserted here */}
      <div ref={playerDivRef} id="youtube-player" className="w-[640px] h-[360px]" />
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