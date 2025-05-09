import sys
import os
import argparse
import json
import time

# Add parent directory to module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.youtube_utils import extract_video_id, get_transcript, get_transcript_with_youtube_api, get_transcript_with_ytdlp

def test_fallback_mechanism(video_id_or_url: str, debug_mode: bool = False):
    """
    Test the fallback mechanism for retrieving YouTube transcripts
    
    Args:
        video_id_or_url: YouTube video ID or URL
        debug_mode: Whether to show detailed information
    """
    try:
        # Extract video ID
        video_id = extract_video_id(video_id_or_url)
        print(f"Testing video ID: {video_id}")
        
        # Record start time
        start_time = time.time()
        
        # Get transcript with fallback mechanism
        transcript = get_transcript(video_id)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Display transcript information
        print(f"\n===== Transcript retrieved successfully =====")
        print(f"Total time taken: {elapsed_time:.2f} seconds")
        print(f"Number of transcript segments: {len(transcript)}")
        
        # Calculate total duration
        if transcript and len(transcript) > 0:
            last_segment = transcript[-1]
            total_duration = last_segment['start'] + last_segment['duration']
            print(f"Total transcript duration: {int(total_duration//60)}m {int(total_duration%60)}s")
            print(f"Total character count: {sum(len(item['text']) for item in transcript)}")
        
        # Show sample if in debug mode
        if debug_mode and transcript:
            print("\nSample segments:")
            for i, segment in enumerate(transcript[:3]):  # Show first 3 segments
                print(f"{i+1}. [{int(segment['start']//60)}:{int(segment['start']%60):02d}] {segment['text']}")
            
            # Also show the last segment
            print(f"Last: [{int(transcript[-1]['start']//60)}:{int(transcript[-1]['start']%60):02d}] {transcript[-1]['text']}")
        
        # Save transcript for further analysis
        output_file = f"{video_id}_fallback_transcript.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)
        
        print(f"\nTranscript saved to: {output_file}")
        
        return transcript
    except Exception as e:
        print(f"Error during test: {str(e)}")
        return None

def test_forced_fallback(video_id_or_url: str, debug_mode: bool = False):
    """
    Test fallback mechanism by forcing the first method to fail
    
    Args:
        video_id_or_url: YouTube video ID or URL
        debug_mode: Whether to show detailed information
    """
    try:
        # Extract video ID
        video_id = extract_video_id(video_id_or_url)
        print(f"Testing video ID with forced fallback: {video_id}")
        
        # Define a failing version of the first method
        def failing_youtube_api(*args, **kwargs):
            print("First method (youtube_transcript_api) forced to fail")
            raise Exception("This is a simulated failure to test fallback")
        
        # Store original methods
        original_methods = [
            ("youtube_transcript_api", get_transcript_with_youtube_api),
            ("yt-dlp", get_transcript_with_ytdlp)
        ]
        
        # Override the methods list with our mock
        import utils.youtube_utils
        utils.youtube_utils.methods = [
            ("youtube_transcript_api", failing_youtube_api),
            ("yt-dlp", get_transcript_with_ytdlp)
        ]
        
        # Record start time
        start_time = time.time()
        
        # Call the function with fallback
        try:
            transcript = get_transcript(video_id)
            success = True
        except Exception as e:
            print(f"All methods failed: {e}")
            success = False
            transcript = None
        
        # Restore original methods
        utils.youtube_utils.methods = original_methods
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        if success:
            print(f"\n===== Fallback test successful =====")
            print(f"Total time: {elapsed_time:.2f} seconds")
            print(f"Number of segments: {len(transcript)}")
            return True
        else:
            print(f"\n===== Fallback test failed =====")
            return False
        
    except Exception as e:
        print(f"Error during fallback test: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test YouTube transcript fallback mechanism')
    parser.add_argument('url', nargs='?', help='YouTube video URL or ID')
    parser.add_argument('--debug', '-d', action='store_true', help='Show detailed information')
    parser.add_argument('--test-fallback', '-f', action='store_true', help='Force first method to fail to test fallback')
    
    args = parser.parse_args()
    video_url = args.url
    debug_mode = args.debug
    test_fallback = args.test_fallback
    
    if not video_url:
        # If no URL provided, prompt for input
        video_url = input("Enter YouTube video URL or ID: ")
        if not video_url:
            # Default test video (Rick Astley - Never Gonna Give You Up)
            video_url = "dQw4w9WgXcQ"
    
    print(f"Testing video: {video_url}")
    
    if test_fallback:
        success = test_forced_fallback(video_url, debug_mode)
        if success:
            print("\n===== Forced Fallback Test Successful =====")
            print("The fallback mechanism correctly used the second method when the first method failed")
        else:
            print("\n===== Forced Fallback Test Failed =====")
    else:
        transcript = test_fallback_mechanism(video_url, debug_mode)
        
        if transcript:
            print("\n===== Test Successful =====")
        else:
            print("\n===== Test Failed =====") 