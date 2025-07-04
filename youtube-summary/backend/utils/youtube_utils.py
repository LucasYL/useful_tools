import re
import os
import json
import subprocess
import requests
import time
from typing import Dict, Any, List, Optional, Tuple
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

# Unified cache directory for all transcript and info files
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'transcripts_cache')
CACHE_EXPIRE_SECONDS = 7 * 24 * 3600  # 7 days

def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def clean_cache_dir():
    """Delete files in cache dir older than CACHE_EXPIRE_SECONDS."""
    ensure_cache_dir()
    now = time.time()
    for fname in os.listdir(CACHE_DIR):
        fpath = os.path.join(CACHE_DIR, fname)
        if os.path.isfile(fpath):
            if now - os.path.getmtime(fpath) > CACHE_EXPIRE_SECONDS:
                try:
                    os.remove(fpath)
                except Exception as e:
                    print(f"[WARN] Failed to remove old cache file {fpath}: {e}")

# Function to extract video ID from URL
def extract_video_id(url: str) -> str:
    """
    Extract video ID from YouTube URL
    
    Args:
        url: YouTube URL or direct video ID
        
    Returns:
        Video ID string
    """
    regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return url  # If no match, assume input is already a video ID

# Function to get video metadata using yt-dlp
def get_video_metadata(video_url: str) -> Dict[str, Any]:
    """
    Use yt-dlp to get YouTube video metadata
    
    Args:
        video_url: YouTube URL or video ID
        
    Returns:
        Dictionary containing title, description and chapters
        
    Raises:
        Exception: If metadata retrieval fails
    """
    try:
        clean_cache_dir()
        ensure_cache_dir()
        # Ensure we have a complete URL
        if not video_url.startswith(('http://', 'https://')):
            video_url = f"https://www.youtube.com/watch?v={video_url}"
            
        # Run yt-dlp to get metadata
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--print', 'webpage_url',
            '--write-info-json',
            '--no-warnings',
            '--quiet',
            video_url
        ]
        
        # Execute command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Get video ID to find info file
        video_id = extract_video_id(video_url)
        info_filename = os.path.join(CACHE_DIR, f"{video_id}.info.json")
        
        # Read info file
        if os.path.exists(info_filename):
            with open(info_filename, 'r') as f:
                info = json.load(f)
                
            # Clean up file
            os.remove(info_filename)
            
            # Extract relevant information
            title = info.get('title', 'Untitled Video')
            description = info.get('description', '')
            
            # Extract chapters
            chapters = []
            if 'chapters' in info and info['chapters']:
                for chapter in info['chapters']:
                    chapters.append({
                        'start_time': chapter.get('start_time', 0),
                        'title': chapter.get('title', 'Unnamed Chapter')
                    })
            
            return {
                'title': title,
                'description': description,
                'chapters': chapters,
                'thumbnail_url': info.get('thumbnail', ''),
                'channel': info.get('channel', '')
            }
        else:
            # If info file wasn't created, try alternative method
            cmd = [
                'yt-dlp',
                '--skip-download',
                '--dump-json',
                video_url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                
                # Extract relevant information
                title = info.get('title', 'Untitled Video')
                description = info.get('description', '')
                
                # Extract chapters
                chapters = []
                if 'chapters' in info and info['chapters']:
                    for chapter in info['chapters']:
                        chapters.append({
                            'start_time': chapter.get('start_time', 0),
                            'title': chapter.get('title', 'Unnamed Chapter')
                        })
                
                return {
                    'title': title,
                    'description': description,
                    'chapters': chapters,
                    'thumbnail_url': info.get('thumbnail', ''),
                    'channel': info.get('channel', '')
                }
            else:
                raise Exception(f"Failed to extract metadata: {result.stderr}")
    except Exception as e:
        raise Exception(f"Error retrieving video metadata: {str(e)}")

def get_transcript_with_youtube_api(video_id: str, max_entries: int = 500, max_chars: int = 50000) -> List[Dict[str, Any]]:
    """
    Get YouTube video transcript using youtube_transcript_api
    
    Args:
        video_id: YouTube video ID
        max_entries: Maximum number of entries, will sample if exceeded
        max_chars: Maximum character count, will trim if exceeded
        
    Returns:
        List of dictionaries containing text, start time and duration
        
    Raises:
        Exception: If transcript retrieval fails
    """
    try:
        # Use the new API format
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id)
        
        # Convert FetchedTranscript to our format
        transcript = []
        for snippet in fetched_transcript:
            transcript.append({
                'text': snippet.text,
                'start': snippet.start,
                'duration': snippet.duration
            })
        
        # Check transcript length
        print(f"Original transcript length: {len(transcript)} entries")
        total_duration = 0
        if transcript and len(transcript) > 0:
            last_entry = transcript[-1]
            total_duration = last_entry['start'] + last_entry['duration']
            print(f"Estimated video duration: {int(total_duration // 60)}:{int(total_duration % 60):02d}")

        # Calculate total text length
        transcript_text_length = sum(len(entry.get('text', '')) for entry in transcript)
        print(f"Original transcript text length: {transcript_text_length} characters")

        # Sample if transcript is too long
        if len(transcript) > max_entries or transcript_text_length > max_chars:
            print(f"Transcript too long, sampling will be applied")
            
            # Ensure we cover the entire video range
            if len(transcript) > max_entries:
                # Calculate sampling interval
                step = max(1, len(transcript) // max_entries)
                print(f"Sampling interval: 1 entry every {step} entries")
                
                # Sample
                sampled_transcript = []
                # Ensure we include first entry
                sampled_transcript.append(transcript[0])
                
                # Sample middle part
                for i in range(step, len(transcript) - 1, step):
                    sampled_transcript.append(transcript[i])
                
                # Ensure we include last entry
                if transcript[-1] != sampled_transcript[-1]:
                    sampled_transcript.append(transcript[-1])
                
                transcript = sampled_transcript
                print(f"Sampled transcript length: {len(transcript)} entries")
                
                # Recalculate text length
                transcript_text_length = sum(len(entry.get('text', '')) for entry in transcript)
                print(f"Sampled transcript text length: {transcript_text_length} characters")
            
            # If still too many characters, trim text
            if transcript_text_length > max_chars:
                print(f"Text still too long, character trimming will be applied")
                char_ratio = max_chars / transcript_text_length
                for i in range(len(transcript)):
                    text = transcript[i].get('text', '')
                    max_entry_chars = int(len(text) * char_ratio)
                    if len(text) > max_entry_chars:
                        transcript[i]['text'] = text[:max_entry_chars] + "..."
                
                # Final length verification
                final_length = sum(len(entry.get('text', '')) for entry in transcript)
                print(f"Final transcript text length: {final_length} characters")
                
        return transcript
                
    except Exception as e:
        raise Exception(f"Error retrieving transcript with youtube_transcript_api: {str(e)}")

def parse_vtt_content(vtt_content: str) -> List[Dict[str, Any]]:
    """
    Parse VTT format subtitle content
    
    Args:
        vtt_content: VTT format subtitle content
        
    Returns:
        List of dictionaries with text, start and duration
    """
    entries = []
    
    # Remove VTT header
    lines = vtt_content.strip().split('\n')
    if lines and lines[0].startswith('WEBVTT'):
        lines = lines[1:]
    
    # Process entries
    i = 0
    while i < len(lines):
        # Skip empty lines
        if not lines[i].strip():
            i += 1
            continue
            
        # Look for timestamp line
        if '-->' in lines[i]:
            # Parse time stamps
            time_parts = lines[i].split('-->')
            if len(time_parts) == 2:
                start_str = time_parts[0].strip()
                end_str = time_parts[1].strip().split(' ')[0]  # Remove styling
                
                # Convert to seconds
                try:
                    start = convert_timestamp_to_seconds(start_str)
                    end = convert_timestamp_to_seconds(end_str)
                    duration = end - start
                    
                    # Get text (may span multiple lines)
                    text_lines = []
                    i += 1
                    while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                        text_lines.append(lines[i].strip())
                        i += 1
                    
                    text = '\n'.join(text_lines)
                    
                    # Add entry
                    entries.append({
                        'text': text,
                        'start': start,
                        'duration': duration
                    })
                    continue
                except Exception as e:
                    print(f"Error parsing timestamp: {e}")
        
        i += 1
    
    return entries

def convert_timestamp_to_seconds(timestamp: str) -> float:
    """
    Convert timestamp string to seconds
    
    Args:
        timestamp: String in format HH:MM:SS.mmm or MM:SS.mmm
        
    Returns:
        Seconds as float
    """
    parts = timestamp.replace(',', '.').split(':')
    
    if len(parts) == 3:  # HH:MM:SS.mmm
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:  # MM:SS.mmm
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    else:
        raise ValueError(f"Invalid timestamp format: {timestamp}")

def get_transcript_with_ytdlp(video_id: str, max_entries: int = 500, max_chars: int = 50000) -> List[Dict[str, Any]]:
    """
    Get YouTube video transcript using yt-dlp
    
    Args:
        video_id: YouTube video ID
        max_entries: Maximum number of entries, will sample if exceeded
        max_chars: Maximum character count, will trim if exceeded
        
    Returns:
        List of dictionaries containing text, start time and duration
        
    Raises:
        Exception: If transcript retrieval fails
    """
    import contextlib
    import glob
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        clean_cache_dir()
        ensure_cache_dir()
        
        # Prepare yt-dlp options to download subtitles
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'skip_download': True,  # Skip video download, only get subtitles
            'quiet': True,
            'outtmpl': os.path.join(CACHE_DIR, '%(id)s.%(ext)s'),
            'subtitleslangs': ['en'],  # Prefer English subtitles
            'subtitlesformat': 'vtt',  # Prefer VTT format
            # 添加更真实的浏览器标识和反检测措施
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            },
            # 添加更多选项来避免检测
            'extractor_retries': 5,
            'socket_timeout': 60,
            'sleep_interval': 1,
            'max_sleep_interval': 3,
            # 额外的反检测选项
            'extractor_args': {
                'youtube': {
                    'player_client': ['web', 'android'],
                    'player_skip': ['webpage'],
                }
            },
        }
        
        # Check for cookies.txt in cache dir
        cookies_path = os.path.join(CACHE_DIR, 'cookies.txt')
        if os.path.exists(cookies_path):
            # 检查cookies文件的大小和修改时间
            file_size = os.path.getsize(cookies_path)
            file_mtime = os.path.getmtime(cookies_path)
            file_age_days = (time.time() - file_mtime) / (24 * 3600)
            
            print(f"[INFO] Using cookies from {cookies_path}")
            print(f"[INFO] Cookies file size: {file_size} bytes, age: {file_age_days:.1f} days")
            
            # 读取cookies文件内容进行基本验证
            try:
                with open(cookies_path, 'r', encoding='utf-8') as f:
                    cookies_content = f.read()
                    # 检查是否包含YouTube相关的cookies
                    if 'youtube.com' in cookies_content:
                        youtube_cookies_count = cookies_content.count('youtube.com')
                        print(f"[INFO] Found {youtube_cookies_count} YouTube cookies")
                    else:
                        print(f"[WARN] No YouTube cookies found in cookies file!")
                    
                    # 检查是否有登录相关的cookies
                    login_indicators = ['SAPISID', 'SSID', 'LOGIN_INFO', 'SID']
                    found_login_cookies = [indicator for indicator in login_indicators if indicator in cookies_content]
                    if found_login_cookies:
                        print(f"[INFO] Found login cookies: {', '.join(found_login_cookies)}")
                    else:
                        print(f"[WARN] No login cookies found - this may cause authentication issues")
                        
            except Exception as e:
                print(f"[ERROR] Failed to read cookies file: {e}")
            
            ydl_opts['cookiefile'] = cookies_path
        else:
            print(f"[INFO] No cookies.txt found in {CACHE_DIR}, proceeding without cookies.")
        
        # Download subtitles using yt-dlp (single attempt)
        print(f"[INFO] Downloading subtitles for video {video_id}")
        
        with open(os.devnull, 'w') as devnull, contextlib.redirect_stderr(devnull):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        
        # Look for downloaded VTT files
        vtt_files = glob.glob(os.path.join(CACHE_DIR, f"{video_id}*.vtt"))
        if not vtt_files:
            raise Exception("No VTT subtitle files were downloaded")
        
        # Use the first VTT file found (prefer manual subtitles over auto-generated)
        vtt_file = vtt_files[0]
        for file in vtt_files:
            if '.en.vtt' in file and 'auto' not in file:
                vtt_file = file
                break
        
        print(f"Found subtitles with yt-dlp: {os.path.basename(vtt_file)}")
        
        # Read and parse the VTT file
        with open(vtt_file, 'r', encoding='utf-8') as f:
            subtitle_content = f.read()
        
        if not subtitle_content.strip():
            raise Exception("Downloaded VTT file is empty")
        
        transcript = parse_vtt_content(subtitle_content)
        
        if len(transcript) > max_entries:
            step = max(1, len(transcript) // max_entries)
            sampled_transcript = [transcript[0]]
            for i in range(step, len(transcript) - 1, step):
                sampled_transcript.append(transcript[i])
            if transcript[-1] != sampled_transcript[-1]:
                sampled_transcript.append(transcript[-1])
            transcript = sampled_transcript
        
        transcript_text_length = sum(len(entry.get('text', '')) for entry in transcript)
        if transcript_text_length > max_chars:
            char_ratio = max_chars / transcript_text_length
            for i in range(len(transcript)):
                text = transcript[i].get('text', '')
                max_entry_chars = int(len(text) * char_ratio)
                if len(text) > max_entry_chars:
                    transcript[i]['text'] = text[:max_entry_chars] + "..."
        
        return transcript
    except Exception as e:
        raise Exception(f"Error retrieving transcript with yt-dlp: {str(e)}")

# Define global methods list for transcript retrieval
# Prioritize youtube_transcript_api first, then yt-dlp
methods = [
    ("youtube_transcript_api", get_transcript_with_youtube_api),
    ("yt-dlp", get_transcript_with_ytdlp)
]

def get_transcript(video_id: str, max_entries: int = 500, max_chars: int = 50000) -> List[Dict[str, Any]]:
    """
    Get YouTube video transcript with intelligent fallback
    Tries youtube_transcript_api first, then falls back to yt-dlp if needed
    Logs detailed error and performance info.
    
    Args:
        video_id: YouTube video ID
        max_entries: Maximum number of entries
        max_chars: Maximum character count
        
    Returns:
        List of dictionaries containing text, start and duration
        
    Raises:
        Exception: If all transcript retrieval methods fail
    """
    errors = []
    
    for i, (name, method) in enumerate(methods):
        try:
            print(f"[INFO] Trying to get transcript using {name}...")
            start_time = time.time()
            transcript = method(video_id, max_entries, max_chars)
            elapsed_time = time.time() - start_time
            print(f"[SUCCESS] Retrieved transcript using {name} in {elapsed_time:.2f} seconds. Segments: {len(transcript)}")
            return transcript
        except Exception as e:
            error_message = str(e)
            print(f"[ERROR] Failed with {name}: {error_message}")
            errors.append(f"{name}: {error_message}")
    
    # If we get here, all methods failed
    print(f"[FAILURE] All transcript retrieval methods failed. Details: {'; '.join(errors)}")
    raise Exception(f"All transcript retrieval methods failed: {'; '.join(errors)}")

def create_enhanced_text(transcript: List[Dict[str, Any]]) -> str:
    """
    Create enhanced text with timestamp markers from transcript
    
    Args:
        transcript: List of transcript entries
        
    Returns:
        Enhanced text string with timestamp markers
    """
    enhanced_text = ""
    
    # Convert each transcript entry to format with timestamp markers
    for entry in transcript:
        # Format time as MM:SS
        minutes = int(entry['start'] // 60)
        seconds = int(entry['start'] % 60)
        time_marker = f"[{minutes}:{seconds:02d}] "
        
        # Add text with timestamp marker
        enhanced_text += time_marker + entry.get('text', '') + " "
    
    # Add video end timestamp
    if transcript and len(transcript) > 0:
        last_entry = transcript[-1]
        video_duration = last_entry['start'] + last_entry['duration']
        minutes = int(video_duration // 60)
        seconds = int(video_duration % 60)
        enhanced_text += f"[{minutes}:{seconds:02d}] End of video."
    
    return enhanced_text 