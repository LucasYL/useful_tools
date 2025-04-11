from youtube_transcript_api import YouTubeTranscriptApi

def test_transcript_api():
    """
    Test the YouTube Transcript API to ensure it can fetch transcripts
    """
    # Test video ID - This is from the example we tested earlier
    video_id = "Vd8szypWbKc"
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print(f"Successfully retrieved transcript for video ID: {video_id}")
        print(f"Transcript contains {len(transcript)} entries")
        print("\nFirst 3 entries:")
        for entry in transcript[:3]:
            print(f"- {entry['text']} (Start: {entry['start']}s, Duration: {entry['duration']}s)")
        return True
    except Exception as e:
        print(f"Error retrieving transcript: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing YouTube Transcript API...")
    test_transcript_api()
