import sys
import os
import argparse
import json
import time
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import requests

# 将父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.youtube_utils import extract_video_id

def test_transcript_with_youtube_api(video_id: str, debug_mode: bool = False):
    """
    Test retrieving YouTube video transcript using youtube_transcript_api
    
    Args:
        video_id: YouTube video ID
        debug_mode: Whether to show detailed information
    """
    try:
        # 记录开始时间
        start_time = time.time()
        
        # 获取字幕
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        if not transcript:
            print("无法获取字幕")
            return None
        
        # 计算字幕总时长
        total_duration = 0
        if transcript and len(transcript) > 0:
            last_segment = transcript[-1]
            total_duration = last_segment['start'] + last_segment['duration']
        
        # 显示字幕信息
        print("\n===== 字幕信息 (youtube_transcript_api) =====")
        print(f"获取耗时: {elapsed_time:.2f}秒")
        print(f"字幕片段数量: {len(transcript)}")
        print(f"字幕总时长: {int(total_duration//60)}分{int(total_duration%60)}秒")
        print(f"字幕总字符数: {sum(len(item['text']) for item in transcript)}")
        
        # 如果启用调试模式，显示更多详细信息
        if debug_mode and transcript:
            print("\nSample segments:")
            for i, segment in enumerate(transcript[:3]):  # Show first 3 segments
                print(f"{i+1}. [{int(segment['start']//60)}:{int(segment['start']%60):02d}] {segment['text']}")
            
            # Also show the last segment
            print(f"Last: [{int(transcript[-1]['start']//60)}:{int(transcript[-1]['start']%60):02d}] {transcript[-1]['text']}")
        
        return {
            "method": "youtube_transcript_api",
            "success": True,
            "transcript": transcript,
            "elapsed_time": elapsed_time
        }
        
    except Exception as e:
        print(f"Error with youtube_transcript_api: {str(e)}")
        return {
            "method": "youtube_transcript_api",
            "success": False,
            "error": str(e)
        }

def test_transcript_with_ytdlp(video_id: str, debug_mode: bool = False):
    """
    Test retrieving YouTube video transcript using yt-dlp
    
    Args:
        video_id: YouTube video ID
        debug_mode: Whether to show detailed information
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        # 记录开始时间
        start_time = time.time()
        
        # Configure yt-dlp options
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'skip_download': True,
            'quiet': not debug_mode,
        }
        
        # Extract information with yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Get subtitle data
        subtitles = {}
        subtitle_type = "unknown"
        if 'subtitles' in info and info['subtitles']:
            subtitles = info['subtitles']
            subtitle_type = "manual"
        elif 'automatic_captions' in info and info['automatic_captions']:
            subtitles = info['automatic_captions']
            subtitle_type = "automatic"
        else:
            print("No subtitles found with yt-dlp")
            return {
                "method": "yt-dlp",
                "success": False,
                "error": "No subtitles found"
            }
        
        # Display subtitle information
        print("\n===== 字幕信息 (yt-dlp) =====")
        print(f"获取耗时: {elapsed_time:.2f}秒")
        print(f"字幕类型: {subtitle_type}")
        print(f"可用语言: {', '.join(subtitles.keys())}")
        
        # Select a language (prefer English, otherwise the first available)
        selected_lang = 'en' if 'en' in subtitles else list(subtitles.keys())[0]
        formats = subtitles[selected_lang]
        
        print(f"\nSelected language: {selected_lang}")
        print(f"可用格式: {len(formats)}")
        
        if debug_mode:
            print("\nFormat details:")
            for i, fmt in enumerate(formats):
                print(f"{i+1}. Format: {fmt.get('ext', 'unknown')}, URL available: {'Yes' if 'url' in fmt else 'No'}")
        
        # Try to get VTT content
        subtitle_content = None
        for fmt in formats:
            if fmt.get('ext') == 'vtt' and 'url' in fmt:
                try:
                    response = requests.get(fmt['url'])
                    if response.status_code == 200:
                        subtitle_content = response.text
                        break
                except Exception as e:
                    print(f"Failed to download VTT content: {e}")
        
        return {
            "method": "yt-dlp",
            "success": True,
            "subtitle_data": subtitles,
            "selected_lang": selected_lang,
            "elapsed_time": elapsed_time,
            "subtitle_content": subtitle_content
        }
        
    except Exception as e:
        print(f"Error with yt-dlp: {str(e)}")
        return {
            "method": "yt-dlp",
            "success": False,
            "error": str(e)
        }

def compare_transcript_methods(video_id_or_url: str, debug_mode: bool = False):
    """
    Compare different methods of retrieving YouTube video transcripts
    
    Args:
        video_id_or_url: YouTube video ID or URL
        debug_mode: Whether to show detailed information
    """
    try:
        # 提取视频ID
        video_id = extract_video_id(video_id_or_url)
        print(f"Testing video ID: {video_id}")
        
        # Test with youtube_transcript_api
        result1 = test_transcript_with_youtube_api(video_id, debug_mode)
        
        # Test with yt-dlp
        result2 = test_transcript_with_ytdlp(video_id, debug_mode)
        
        # Compare results
        print("\n===== Comparison Results =====")
        print(f"youtube_transcript_api: {'✅ Success' if result1.get('success', False) else '❌ Failed'}")
        print(f"yt-dlp: {'✅ Success' if result2.get('success', False) else '❌ Failed'}")
        
        if result1.get('success', False) and result2.get('success', False):
            print("\nBoth methods succeeded!")
            print(f"youtube_transcript_api time: {result1.get('elapsed_time', 0):.2f}s")
            print(f"yt-dlp time: {result2.get('elapsed_time', 0):.2f}s")
            
            # Compare segment counts if possible
            if 'transcript' in result1:
                print(f"youtube_transcript_api segments: {len(result1['transcript'])}")
            
            # Save transcript data for further analysis
            output_api_file = f"{video_id}_youtube_api_transcript.json"
            with open(output_api_file, 'w', encoding='utf-8') as f:
                json.dump(result1.get('transcript', []), f, ensure_ascii=False, indent=2)
            print(f"youtube_transcript_api data saved to: {output_api_file}")
            
            # Save yt-dlp data for comparison
            output_ytdlp_file = f"{video_id}_ytdlp_transcript.json"
            with open(output_ytdlp_file, 'w', encoding='utf-8') as f:
                json.dump(result2.get('subtitle_data', {}), f, ensure_ascii=False, indent=2)
            print(f"yt-dlp data saved to: {output_ytdlp_file}")
            
            # Save raw VTT content if available
            if 'subtitle_content' in result2:
                output_vtt_file = f"{video_id}_ytdlp_raw.vtt"
                with open(output_vtt_file, 'w', encoding='utf-8') as f:
                    f.write(result2['subtitle_content'])
                print(f"Raw VTT content saved to: {output_vtt_file}")
        
        elif result1.get('success', False):
            print("\nOnly youtube_transcript_api succeeded.")
            print(f"yt-dlp error: {result2.get('error', 'Unknown error')}")
        
        elif result2.get('success', False):
            print("\nOnly yt-dlp succeeded.")
            print(f"youtube_transcript_api error: {result1.get('error', 'Unknown error')}")
        
        else:
            print("\n❌ Both methods failed!")
            print(f"youtube_transcript_api error: {result1.get('error', 'Unknown error')}")
            print(f"yt-dlp error: {result2.get('error', 'Unknown error')}")
        
        return {
            "youtube_api": result1,
            "yt-dlp": result2
        }
    except Exception as e:
        print(f"Error during comparison: {str(e)}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test YouTube transcript retrieval methods')
    parser.add_argument('url', nargs='?', help='YouTube video URL or ID')
    parser.add_argument('--debug', '-d', action='store_true', help='Show detailed information')
    
    args = parser.parse_args()
    video_url = args.url
    debug_mode = args.debug
    
    if not video_url:
        # If no URL provided, prompt for input
        video_url = input("Enter YouTube video URL or ID: ")
        if not video_url:
            # Default test video (Rick Astley - Never Gonna Give You Up)
            video_url = "dQw4w9WgXcQ"
    
    print(f"Testing video: {video_url}")
    results = compare_transcript_methods(video_url, debug_mode)
    
    print("\n===== Test Complete =====") 