from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Any, Optional
import os
import re
import subprocess
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI API
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY not found in environment variables")

app = FastAPI()

# Define request and response models
class VideoRequest(BaseModel):
    video_id: str
    summary_type: str = "short"  # 'short' or 'detailed'
    language: str = "en"  # 'en', 'zh', etc.

class TranscriptEntry(BaseModel):
    text: str
    start: float
    duration: float
    
class Chapter(BaseModel):
    start_time: float
    title: str

class SummaryResponse(BaseModel):
    video_id: str
    title: str
    description: str
    summary: str
    transcript: List[TranscriptEntry]
    chapters: List[Chapter]

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

# Route for video summarization
@app.post("/api/summarize", response_model=SummaryResponse)
async def summarize_video(request: VideoRequest):
    try:
        # Extract video ID if a full URL was provided
        video_id = extract_video_id(request.video_id)
        
        # Get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Get video metadata
        metadata = get_video_metadata(video_id)
        
        # Convert transcript to text
        full_text = " ".join([entry["text"] for entry in transcript])
        
        # Generate only the requested summary type
        summary = generate_summary(full_text, request.summary_type, metadata, request.language)
        
        # Return response
        return {
            "video_id": video_id,
            "title": metadata["title"],
            "description": metadata["description"],
            "summary": summary,
            "transcript": transcript,
            "chapters": metadata["chapters"]
        }
    except Exception as e:
        error_message = str(e)
        print(f"Error in summarize_video: {error_message}")
        # Return a properly formatted JSON error response
        raise HTTPException(
            status_code=400,
            detail={"error": error_message, "message": "Failed to process video"}
        )

# Function to generate summary using OpenAI API
def generate_summary(text: str, summary_type: str, metadata: Optional[Dict[str, Any]] = None, language: str = "en") -> str:
    # Define enhanced prompts that include video metadata
    if metadata:
        title = metadata.get("title", "")
        description = metadata.get("description", "")
        chapters = metadata.get("chapters", [])
        
        # Format chapters for the prompt if available
        chapters_text = ""
        if chapters:
            chapters_text = "Video chapters:\n"
            for chapter in chapters:
                time_formatted = f"{int(chapter['start_time'] // 60)}:{int(chapter['start_time'] % 60):02d}"
                chapters_text += f"- {time_formatted}: {chapter['title']}\n"
        
        # Language instructions
        language_instructions = ""
        if language != "en":
            language_map = {
                "zh": "Chinese (中文)",
                "es": "Spanish (Español)",
                "fr": "French (Français)",
                "de": "German (Deutsch)",
                "ja": "Japanese (日本語)",
                "ko": "Korean (한국어)",
            }
            target_language = language_map.get(language, language)
            language_instructions = f"\nPlease provide your response in {target_language}."
        
        # Enhanced prompts using metadata
        prompts = {
            "short": f"""You are analyzing a YouTube video titled "{title}".

Video description:
{description}

{chapters_text}

Please provide a concise summary of the following video transcript in 200 words or less, focusing on the main point and key takeaways.{language_instructions}""",
            
            "detailed": f"""You are analyzing a YouTube video titled "{title}".

Video description:
{description}

{chapters_text}

Please provide a detailed summary of the following video transcript, including:
1. Main points following the structure of the chapters when available
2. Key arguments and supporting evidence
3. Important data, facts, or examples mentioned
4. Conclusions, recommendations, or calls to action
5. The overall perspective or stance of the speaker

Your summary should be well-structured, comprehensive, and faithful to the original content.{language_instructions}"""
        }
    else:
        # Language instructions
        language_instructions = ""
        if language != "en":
            language_map = {
                "zh": "Chinese (中文)",
                "es": "Spanish (Español)",
                "fr": "French (Français)",
                "de": "German (Deutsch)",
                "ja": "Japanese (日本語)",
                "ko": "Korean (한国语)",
            }
            target_language = language_map.get(language, language)
            language_instructions = f"\nPlease provide your response in {target_language}."
            
        # Original prompts if no metadata is available
        prompts = {
            "short": f"Please provide a concise summary of the following video transcript in 100 words or less.{language_instructions}",
            "detailed": f"""
            Please provide a detailed summary of the following video transcript, including:
            1. Main points
            2. Key arguments
            3. Important data or facts
            4. Conclusions or recommendations
            {language_instructions}
            """
        }
    
    try:
        # Use OpenAI API to generate summary (synchronous version)
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompts[summary_type]},
                {"role": "user", "content": text}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        # If OpenAI API fails, return a placeholder
        print(f"Error generating summary: {str(e)}")
        return "Summary generation failed. Please try again later."

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# CORS middleware to allow frontend requests
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
