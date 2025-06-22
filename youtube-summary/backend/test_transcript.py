#!/usr/bin/env python3
"""
Test script for transcript extraction methods
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.youtube_utils import get_transcript_with_youtube_api, get_transcript_with_ytdlp, extract_video_id

def test_transcript_extraction():
    """Test transcript extraction with different methods"""
    
    # Test URLs - use publicly available videos with known transcripts
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - should have transcripts
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo - first YouTube video
        "https://youtu.be/dQw4w9WgXcQ",  # Short URL format
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing URL: {url}")
        print(f"{'='*60}")
        
        # Extract video ID
        try:
            video_id = extract_video_id(url)
            print(f"✓ Video ID extracted: {video_id}")
        except Exception as e:
            print(f"✗ Failed to extract video ID: {e}")
            continue
        
        # Test Method 1: YouTube Transcript API
        print(f"\n--- Testing youtube_transcript_api ---")
        try:
            transcript = get_transcript_with_youtube_api(video_id)
            print(f"✓ SUCCESS: Retrieved {len(transcript)} segments")
            if transcript:
                print(f"  First segment: {transcript[0]}")
                print(f"  Last segment: {transcript[-1]}")
                # Check if segments have required fields
                required_fields = ['text', 'start']
                for field in required_fields:
                    if field in transcript[0]:
                        print(f"  ✓ Has '{field}' field")
                    else:
                        print(f"  ✗ Missing '{field}' field")
            else:
                print("  ✗ Empty transcript returned")
        except Exception as e:
            print(f"✗ FAILED: {e}")
        
        # Test Method 2: yt-dlp
        print(f"\n--- Testing yt-dlp ---")
        try:
            transcript = get_transcript_with_ytdlp(video_id)
            print(f"✓ SUCCESS: Retrieved {len(transcript)} segments")
            if transcript:
                print(f"  First segment: {transcript[0]}")
                print(f"  Last segment: {transcript[-1]}")
                # Check if segments have required fields
                required_fields = ['text', 'start']
                for field in required_fields:
                    if field in transcript[0]:
                        print(f"  ✓ Has '{field}' field")
                    else:
                        print(f"  ✗ Missing '{field}' field")
            else:
                print("  ✗ Empty transcript returned")
        except Exception as e:
            print(f"✗ FAILED: {e}")

if __name__ == "__main__":
    print("Starting transcript extraction tests...")
    test_transcript_extraction()
    print("\nTest completed!") 