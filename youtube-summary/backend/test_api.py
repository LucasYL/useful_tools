import re
import os
import json
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Dict, Any, Optional, List

# Function to extract video ID from URL
def extract_video_id(url: str) -> str:
    """
    Extract the video ID from a YouTube URL
    """
    regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return url  # If no match, assume the url is already a video ID

# Function to get video metadata using yt-dlp
def get_video_metadata(video_url: str) -> Dict[str, Any]:
    """
    Fetches metadata for a YouTube video using yt-dlp
    
    Args:
        video_url: YouTube URL or video ID
        
    Returns:
        Dictionary containing title, description, and chapters
        
    Raises:
        Exception: If metadata retrieval fails
    """
    try:
        # Ensure we have a full URL
        if not video_url.startswith(('http://', 'https://')):
            video_url = f"https://www.youtube.com/watch?v={video_url}"
            
        # Run yt-dlp to extract metadata
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--print', 'webpage_url',
            '--write-info-json',
            '--no-warnings',
            '--quiet',
            video_url
        ]
        
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Get the video ID to find the info file
        video_id = extract_video_id(video_url)
        info_filename = f"{video_id}.info.json"
        
        # Read the info file
        if os.path.exists(info_filename):
            with open(info_filename, 'r') as f:
                info = json.load(f)
                
            # Clean up the file
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
                'chapters': chapters
            }
        else:
            # Try alternative approach if info file wasn't created
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
                    'chapters': chapters
                }
            else:
                raise Exception(f"Failed to extract metadata: {result.stderr}")
    except Exception as e:
        raise Exception(f"Error retrieving video metadata: {str(e)}")

def generate_enhanced_text(transcript):
    """
    Generate enhanced text with timestamp markers from transcript
    """
    enhanced_text = ""
    
    # Convert each transcript entry to a format with timestamp markers
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

def extract_reference_timestamps(enhanced_text, num_samples=10):
    """
    Extract reference timestamps from enhanced text
    """
    time_points = []
    time_matches = re.finditer(r'\[(\d+:\d+)\]\s*([^\[]+)', enhanced_text)
    
    # Take approximately num_samples evenly spaced timestamps as reference points
    all_matches = list(time_matches)
    if all_matches:
        step = max(1, len(all_matches) // num_samples)
        for i in range(0, len(all_matches), step):
            if i < len(all_matches):
                match = all_matches[i]
                timestamp = match.group(1)
                sample_text = match.group(2).strip()[:50] + ('...' if len(match.group(2).strip()) > 50 else '')
                time_points.append(f"{timestamp} - \"{sample_text}\"")
    
    return time_points

def test_enhanced_text_generation(video_id_or_url: str):
    """
    Test the enhanced text generation for a YouTube video
    """
    try:
        # Extract video ID if a full URL was provided
        video_id = extract_video_id(video_id_or_url)
        print(f"Testing enhanced text generation for video ID: {video_id}")
        
        # Get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print(f"Successfully retrieved transcript with {len(transcript)} entries")
        
        # Get video metadata
        metadata = get_video_metadata(video_id)
        print(f"Successfully retrieved metadata for video: {metadata['title']}")
        
        # Generate enhanced text
        enhanced_text = generate_enhanced_text(transcript)
        
        # Extract reference timestamps
        reference_timestamps = extract_reference_timestamps(enhanced_text)
        
        # Calculate video duration
        if transcript and len(transcript) > 0:
            last_entry = transcript[-1]
            video_duration = last_entry['start'] + last_entry['duration']
            duration_str = f"{int(video_duration // 60)}:{int(video_duration % 60):02d}"
        else:
            duration_str = "Unknown"
        
        # Print results
        print("\n--- ENHANCED TEXT GENERATION TEST RESULTS ---")
        print(f"Video Title: {metadata['title']}")
        print(f"Video Duration: {duration_str}")
        print(f"Has Chapters: {'Yes' if metadata['chapters'] else 'No'}")
        if metadata['chapters']:
            print("\nChapters:")
            for chapter in metadata['chapters']:
                mins = int(chapter['start_time'] // 60)
                secs = int(chapter['start_time'] % 60)
                print(f"- [{mins}:{secs:02d}] {chapter['title']}")
        
        print("\nTranscript Sample (first 3 entries):")
        for i, entry in enumerate(transcript[:3]):
            print(f"- {entry['text']} (Start: {entry['start']}s, Duration: {entry['duration']}s)")
        
        print("\nEnhanced Text Sample (first 500 chars):")
        print(enhanced_text[:500] + "..." if len(enhanced_text) > 500 else enhanced_text)
        
        print("\nReference Timestamps Sample:")
        for timestamp in reference_timestamps[:5]:
            print(f"- {timestamp}")
        
        return {
            "video_id": video_id,
            "title": metadata["title"],
            "has_chapters": bool(metadata["chapters"]),
            "chapters_count": len(metadata["chapters"]),
            "transcript_length": len(transcript),
            "enhanced_text_length": len(enhanced_text),
            "duration": duration_str
        }
    except Exception as e:
        print(f"Error in test_enhanced_text_generation: {str(e)}")
        return None

if __name__ == "__main__":
    # Test with a video ID or URL
    video_input = input("Enter YouTube video ID or URL: ")
    if not video_input:
        # Default test video if none provided
        video_input = "Vd8szypWbKc"  # Default test video
    
    result = test_enhanced_text_generation(video_input)
    
    if result:
        print("\n--- TEST SUMMARY ---")
        for key, value in result.items():
            print(f"{key}: {value}")
        print("\nTest completed successfully!")
    else:
        print("\nTest failed. Please check the errors above.")
