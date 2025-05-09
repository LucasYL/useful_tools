import sys
import os
import re
import subprocess
from typing import Optional, List, Dict, Any
import json
import traceback

# 确保能找到模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException, Query, status, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import openai
from openai import OpenAI
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# 更新导入路径
from database.db import get_db, Base, engine
from database.models import User, Video, Summary, Tag, VideoTag
from auth.routes import router as auth_router, get_current_user, get_current_user_optional
from auth.auth_utils import get_password_hash
from utils.youtube_utils import extract_video_id, get_video_metadata, get_transcript, create_enhanced_text

from summary_routes import router as summary_router

# 加载环境变量
load_dotenv()


# 创建FastAPI实例
app = FastAPI(title="YouTube Summary API", version="0.2.0")

# 注册认证路由 - 添加前缀以匹配前端请求
app.include_router(auth_router, prefix="/auth")

# 创建数据库表
Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

# Initialize API
openai_api_key = os.getenv("OPENROUTER_API_KEY")
if not openai_api_key:
    print("Warning: OPENROUTER_API_KEY not found in environment variables")

app.include_router(summary_router, prefix="/api/summaries")

# Define request and response models
class VideoRequest(BaseModel):
    video_id: str
    summary_type: str = "short"  
    language: str = "en" 

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
async def summarize_video(
    request: VideoRequest, 
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    try:
        # Extract video ID if a full URL was provided
        video_id = extract_video_id(request.video_id)
        
        # Get transcript using fallback (yt-dlp included)
        transcript = get_transcript(video_id)
        
        # Get video metadata
        metadata = get_video_metadata(video_id)
        
        # Create enhanced text with timestamps for each entry
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
        
        print(f"[DEBUG] Enhanced text length: {len(enhanced_text)} characters")
            
        # Add format explanation to the prompt
        format_note = "\nNOTE: The transcript contains timestamp markers in the format [MM:SS] indicating the start time of each segment in the video."
            
        # Generate summary with the enhanced text
        summary = generate_summary(enhanced_text, request.summary_type, metadata, request.language, format_note)
        
        # 如果用户已登录，保存摘要到数据库
        if current_user:
            try:
                # 查找或创建视频记录
                video_db = db.query(Video).filter(Video.youtube_id == video_id).first()
                
                if not video_db:
                    # 创建新视频记录
                    video_db = Video(
                        youtube_id=video_id,
                        title=metadata["title"],
                        channel=metadata.get("channel", ""),
                        duration=int(video_duration) if 'video_duration' in locals() else None,
                        thumbnail_url=metadata.get("thumbnail_url", "")
                    )
                    db.add(video_db)
                    db.commit()
                    db.refresh(video_db)
                
                # 检查是否已存在该用户对此视频的摘要
                existing_summary = db.query(Summary).filter(
                    Summary.user_id == current_user.id,
                    Summary.video_id == video_db.id
                ).first()
                
                # 已存在则更新，否则创建新记录
                if existing_summary:
                    existing_summary.summary_text = summary
                    existing_summary.transcript_text = enhanced_text
                    existing_summary.summary_type = request.summary_type
                    existing_summary.language = request.language
                    db.commit()
                    print(f"[DEBUG] Summary updated for user {current_user.username}")
                else:
                    # 创建新摘要
                    db_summary = Summary(
                        user_id=current_user.id,
                        video_id=video_db.id,
                        summary_text=summary,
                        transcript_text=enhanced_text,
                        summary_type=request.summary_type,
                        language=request.language
                    )
                    db.add(db_summary)
                    db.commit()
                    print(f"[DEBUG] Summary saved to database for user {current_user.username}")
            except Exception as db_err:
                print(f"[DEBUG] Error saving summary to database: {str(db_err)}")
                # Continue even if database save fails
        
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

# Function to generate summary using OpenRouter API with Claude 3.7 Sonnet
def generate_summary(text: str, summary_type: str, metadata: Optional[Dict[str, Any]] = None, language: str = "en", format_note: str = "") -> str:
    # Define enhanced prompts that include video metadata
    if metadata:
        title = metadata.get("title", "")
        description = metadata.get("description", "")
        chapters = metadata.get("chapters", [])
        
        # Calculate approximate video duration from transcript
        # The transcript contains entries with start time and duration
        transcript_duration = 0
        try:
            # Assuming 'text' is the full transcript joined together, but we need to extract timing information
            # from the original transcript which should be available in transcript_entries
            transcript_entries = []
            if not isinstance(text, str):
                # If text is the raw transcript list
                transcript_entries = text
            else:
                # Try to parse from the JSON string if it's embedded
                import re
                import json
                transcript_match = re.search(r'\[.*\]', text)
                if transcript_match:
                    try:
                        transcript_entries = json.loads(transcript_match.group(0))
                    except:
                        pass
                
            if transcript_entries:
                last_entry = transcript_entries[-1]
                if isinstance(last_entry, dict) and 'start' in last_entry and 'duration' in last_entry:
                    transcript_duration = last_entry['start'] + last_entry['duration']
        except:
            # Fallback to a reasonable default if we can't determine
            transcript_duration = 3600  # 1 hour default
            
        # Format chapters for the prompt if available
        chapters_text = ""
        if chapters:
            chapters_text = "Video chapters:\n"
            for chapter in chapters:
                time_formatted = f"{int(chapter['start_time'] // 60)}:{int(chapter['start_time'] % 60):02d}"
                chapters_text += f"- {time_formatted}: {chapter['title']}\n"
            
            chapters_text += f"\nNOTE: The video duration is approximately {int(transcript_duration // 60)}:{int(transcript_duration % 60):02d}."
        else:
            # If there are no chapters, still inform about the video duration
            chapters_text = f"NOTE: The video duration is approximately {int(transcript_duration // 60)}:{int(transcript_duration % 60):02d}."
        
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
            # Special instructions for different languages
            if language == "zh":
                # Chinese requires more characters to express equivalent content
                language_instructions = f"""
\nPlease provide your response in {target_language}.

LANGUAGE-SPECIFIC INSTRUCTIONS FOR CHINESE:
- Chinese summaries should be clear and concise, using appropriate character count
- Length requirements (must follow):
  * short summary type:
    - Videos under 10 minutes: ~50-70 characters per minute
    - 10-30 minute videos: ~40-60 characters per minute (minimum 500 characters total)
    - 30-60 minute videos: ~30-50 characters per minute (minimum 1200 characters total)
    - Videos over 60 minutes: ~25-40 characters per minute (minimum 2000 characters total)
  * detailed summary type:
    - Videos under 10 minutes: ~80-100 characters per minute
    - 10-30 minute videos: ~70-90 characters per minute (minimum 1000 characters total)
    - 30-60 minute videos: ~60-80 characters per minute (minimum 2500 characters total)
    - Videos over 60 minutes: ~50-70 characters per minute (minimum 3500 characters total)
- Use natural Chinese expressions, avoid direct translations from English
- Ensure each timestamp section is concise and appropriately detailed

Format example:
0:00 - [Section title]
Content summary... (control character count based on summary type)

2:15 - [Section title]
Content summary... (control character count based on summary type)
"""
            else:
                language_instructions = f"\nPlease provide your response in {target_language}."
        else:
            # 英文特殊指导
            language_instructions = """
ENGLISH-SPECIFIC INSTRUCTIONS:
- English summaries must be comprehensive and detailed
- For videos under 60 minutes, use the higher end of the word count range
- Include specific quotes and details from the video
- DO NOT make the summary too short - utilize the full context window
- If the video discusses complex topics, provide even more detailed explanations
"""
        
        # Add format note to instructions
        if format_note:
            if language_instructions:
                language_instructions = format_note + language_instructions
            else:
                language_instructions = format_note
        
        # Enhanced prompts using metadata
        prompts = {
            "short": f"""You are analyzing a YouTube video titled "{title}".

Video description:
{description}

{chapters_text}

Please create a concise summary of the video transcript. Your summary must:
1. Cover the ENTIRE video content (unless the video is over 2 hours, then you may summarize the first 2 hours)
2. Divide the content into sections based on natural topic shifts in the transcript
3. Start each section with an ACCURATE timestamp (MM:SS format) directly from the transcript markers
4. Each section must start with a short, descriptive section title summarizing the main point of that section.
5. Present timestamps in STRICT chronological order (from beginning to end)
6. LENGTH REQUIREMENT (CRITICAL):
   - For videos under 10 minutes: 40-60 words/characters per minute of video
   - For videos 10-30 minutes: 30-50 words/characters per minute (minimum 400 words total)
   - For videos 30-60 minutes: 25-40 words/characters per minute (minimum 900 words total)
   - For videos over 60 minutes: 20-30 words/characters per minute (minimum 1800 words total)
   - For Chinese content: character counts should be 1.5-2x the above word counts
7. Focus on main points, keep explanations brief but comprehensive

Example format:
0:00 - [Section Title]
Brief description of this section

2:15 - [Section Title]
Brief description of another section

etc.

CRITICAL RULES:
- Each line in the transcript has a timestamp in the [MM:SS] format. USE THESE TIMESTAMPS to mark the beginning of your summary sections.
- If the video has chapters, use those chapter timestamps as primary section dividers.
- For videos without chapters, identify natural topic shifts in the transcript and use the timestamps at those points.
- Your summary MUST cover the complete video content in chronological order.
- Ensure balanced coverage - don't focus too much on early parts and rush through later parts.
- YOU MUST MEET THE MINIMUM LENGTH REQUIREMENTS specified above. DO NOT make the summary too short.
- Never generate timestamps that exceed the video duration.
- Each section must start with a short, descriptive section title summarizing the main point of that section.

The summary should help viewers quickly understand the entire video's content.{language_instructions}""",
            
            "detailed": f"""You are analyzing a YouTube video titled "{title}".

Video description:
{description}

{chapters_text}

Please provide a detailed summary of the video transcript. Your summary must:
1. Cover the ENTIRE video content (unless the video is over 2 hours, then you may summarize the first 2 hours)
2. Organize the summary by natural content sections (topic changes in the transcript)
3. Start each section with an ACCURATE timestamp (MM:SS format) directly from the transcript markers
4. Each section must start with a short, descriptive section title summarizing the main point of that section.
5. Present timestamps in STRICT chronological order (from beginning to end)
6. LENGTH REQUIREMENT (CRITICAL):
   - For videos under 10 minutes: 80-120 words/characters per minute of video
   - For videos 10-30 minutes: 60-90 words/characters per minute (minimum 800 words total)
   - For videos 30-60 minutes: 50-70 words/characters per minute (minimum 1800 words total)
   - For videos over 60 minutes: 40-60 words/characters per minute (minimum 3000 words total)
   - For Chinese content: character counts should be 1.5-2x the above word counts
7. Include specific details, examples, and insights from each section

Your summary should follow this format:
0:00 - [Section Title]
Detailed summary of this section's content...

2:15 - [Section Title]
Detailed summary of this section's content...

etc.

CRITICAL RULES:
- Each line in the transcript has a timestamp in the [MM:SS] format. USE THESE TIMESTAMPS to mark the beginning of your summary sections.
- If the video has chapters, use those chapter timestamps as primary section dividers.
- For videos without chapters, identify natural topic shifts in the transcript and use the timestamps at those points.
- Your summary MUST cover the complete video content in chronological order.
- Ensure balanced coverage - don't focus too much on early parts and rush through later parts.
- YOU MUST MEET THE MINIMUM LENGTH REQUIREMENTS specified above. DO NOT make the summary too short.
- Include concrete details, quotes, examples and specific points from the video.
- Never generate timestamps that exceed the video duration.
- Each section must start with a short, descriptive section title summarizing the main point of that section.

The goal is to create a well-structured, comprehensive summary that covers the entire video's content while highlighting the most important information.{language_instructions}"""
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
                "ko": "Korean (한국어)",
            }
            target_language = language_map.get(language, language)
            # Special instructions for different languages
            if language == "zh":
                # Chinese requires more characters to express equivalent content
                language_instructions = f"""
\nPlease provide your response in {target_language}.

LANGUAGE-SPECIFIC INSTRUCTIONS FOR CHINESE:
- Chinese summaries should be clear and concise, using appropriate character count
- Length requirements (must follow):
  * short summary type:
    - Videos under 10 minutes: ~50-70 characters per minute
    - 10-30 minute videos: ~40-60 characters per minute (minimum 500 characters total)
    - 30-60 minute videos: ~30-50 characters per minute (minimum 1200 characters total)
    - Videos over 60 minutes: ~25-40 characters per minute (minimum 2000 characters total)
  * detailed summary type:
    - Videos under 10 minutes: ~80-100 characters per minute
    - 10-30 minute videos: ~70-90 characters per minute (minimum 1000 characters total)
    - 30-60 minute videos: ~60-80 characters per minute (minimum 2500 characters total)
    - Videos over 60 minutes: ~50-70 characters per minute (minimum 3500 characters total)
- Use natural Chinese expressions, avoid direct translations from English
- Ensure each timestamp section is concise and appropriately detailed

Format example:
0:00 - [Section title]
Content summary... (control character count based on summary type)

2:15 - [Section title]
Content summary... (control character count based on summary type)
"""
            else:
                language_instructions = f"\nPlease provide your response in {target_language}."
            
        # Add format note to instructions
        if format_note:
            if language_instructions:
                language_instructions = format_note + language_instructions
            else:
                language_instructions = format_note
            
        # Original prompts if no metadata is available
        prompts = {
            "short": f"""Please create a concise summary of the video transcript. Your summary must:
1. Cover the ENTIRE video content (unless the video is over 2 hours, then you may summarize the first 2 hours)
2. Divide the content into 3-5 sections based on natural topic shifts in the transcript
3. Start each section with an ACCURATE timestamp (MM:SS format) derived DIRECTLY from the transcript
4. Present timestamps in STRICT chronological order (from beginning to end)
5. Adjust summary length based on video duration - use approximately 20-30 words per minute of video
6. Focus on main points, keep explanations brief but comprehensive

Example format:
0:00 - Brief description of this section
2:15 - Brief description of another section
etc.

CRITICAL RULES:
- DO NOT INVENT OR HALLUCINATE ANY TIMESTAMPS. Only use timestamps that appear in the [MM:SS] format in the transcript.
- Your summary MUST cover the complete video content in chronological order
- Only use timestamps that are explicitly marked in the transcript
- Ensure balanced coverage - don't focus too much on early parts and rush through later parts
- Keep the total summary length proportional to video length (20-30 words per minute)
- Never introduce timestamps that exceed the video duration

The summary should help viewers quickly understand the entire video's content.{language_instructions}""",

            "detailed": f"""Please provide a detailed summary of the video transcript. Your summary must:
1. Cover the ENTIRE video content (unless the video is over 2 hours, then you may summarize the first 2 hours)
2. Organize the summary into 4-6 logical sections based on content shifts in the transcript
3. Start each section with an ACCURATE timestamp (MM:SS format) derived DIRECTLY from the transcript
4. Present timestamps in STRICT chronological order (from beginning to end)
5. Adjust summary length based on video duration - use approximately 40-70 words per minute of video
6. Include specific details, examples, and insights from each section

Your summary should follow this format:
0:00 - [Section Title]
Detailed summary of this section's content...

2:15 - [Section Title]
Detailed summary of this section's content...

etc.

CRITICAL RULES:
- DO NOT INVENT OR HALLUCINATE ANY TIMESTAMPS. Only use timestamps that appear in the [MM:SS] format in the transcript.
- Your summary MUST cover the complete video content in chronological order
- Only use timestamps that are explicitly marked in the transcript
- Ensure balanced coverage - don't focus too much on early parts and rush through later parts
- Keep the total summary length proportional to video length (40-70 words per minute)
- Provide more details than the concise summary, but still focus on what's most important
- Never introduce timestamps that exceed the video duration

The goal is to create a well-structured, comprehensive summary that covers the entire video's content while highlighting the most important information.{language_instructions}"""
        }
    
    try:
        # Calculate video duration directly from the text if possible
        match = re.search(r'\[(\d+:\d+)\]\s*End of video', text)
        if match:
            video_duration_str = match.group(1)
            # Add video duration to prompt
            video_duration_text = f"\nIMPORTANT: The video's EXACT duration is {video_duration_str}. DO NOT generate timestamps beyond this time."
            
            # Extract minutes and seconds for calculating expected output length
            duration_parts = video_duration_str.split(':')
            if len(duration_parts) == 2:
                minutes = int(duration_parts[0])
                seconds = int(duration_parts[1])
                total_minutes = minutes + seconds/60
                
                # Add expected length guidance based on video duration
                if summary_type == "detailed":
                    expected_words = 0
                    if total_minutes <= 10:
                        expected_words = int(total_minutes * 100)
                    elif total_minutes <= 30:
                        expected_words = int(10 * 100 + (total_minutes - 10) * 75)
                    elif total_minutes <= 60:
                        expected_words = int(10 * 100 + 20 * 75 + (total_minutes - 30) * 60)
                    else:
                        expected_words = int(10 * 100 + 20 * 75 + 30 * 60 + (total_minutes - 60) * 50)
                    
                    if language == "zh":
                        expected_words = int(expected_words * 1.7)  # 中文字符需要更多
                    
                    length_guidance = f"\nYour summary should be approximately {expected_words} words/characters in length to adequately cover this {int(total_minutes)}-minute video."
                else:
                    expected_words = 0
                    if total_minutes <= 10:
                        expected_words = int(total_minutes * 50)
                    elif total_minutes <= 30:
                        expected_words = int(10 * 50 + (total_minutes - 10) * 40)
                    elif total_minutes <= 60:
                        expected_words = int(10 * 50 + 20 * 40 + (total_minutes - 30) * 35)
                    else:
                        expected_words = int(10 * 50 + 20 * 40 + 30 * 35 + (total_minutes - 60) * 25)
                    
                    if language == "zh":
                        expected_words = int(expected_words * 1.7)  # 中文字符需要更多
                    
                    length_guidance = f"\nYour summary should be approximately {expected_words} words/characters in length to adequately cover this {int(total_minutes)}-minute video."
                
                # Add length guidance to prompts
                video_duration_text += length_guidance
            
            for summary_type_key in prompts:
                if isinstance(prompts[summary_type_key], dict) and "system_content" in prompts[summary_type_key]:
                    prompts[summary_type_key]["system_content"] += video_duration_text
                else:
                    prompts[summary_type_key] += video_duration_text
        
        # Extract reference timestamps to help the model
        time_points = []
        time_matches = re.finditer(r'\[(\d+:\d+)\]\s*([^\[]+)', text)
        
        # Take approximately 10 evenly spaced timestamps as reference points
        all_matches = list(time_matches)
        if all_matches:
            step = max(1, len(all_matches) // 10)
            for i in range(0, len(all_matches), step):
                if i < len(all_matches):
                    match = all_matches[i]
                    timestamp = match.group(1)
                    sample_text = match.group(2).strip()[:50] + ('...' if len(match.group(2).strip()) > 50 else '')
                    time_points.append(f"{timestamp} - \"{sample_text}\"")
        
            # Add reference timestamps to prompt
            if time_points:
                time_points_text = "\n\nReference timestamps in transcript (MM:SS - text sample):\n" + "\n".join(time_points)
                
                if isinstance(prompts[summary_type], dict) and "system_content" in prompts[summary_type]:
                    prompts[summary_type]["system_content"] += time_points_text
                else:
                    prompts[summary_type] += time_points_text
        
        # Use OpenRouter API to generate summary with Claude 3.7 Sonnet
        client = OpenAI(
            api_key=openai_api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        print(f"[DEBUG] System prompt length: {len(prompts[summary_type])}")
        print(f"[DEBUG] Transcript text length: {len(text)}")
        
        try:
            response = client.chat.completions.create(
                model="anthropic/claude-3.7-sonnet",
                messages=[
                    {"role": "system", "content": prompts[summary_type]},
                    {"role": "user", "content": text}
                ],
                max_tokens=10000,
                temperature=0.7,
            )
            
            print(f"[DEBUG] Received response from OpenRouter API")
            
            # Debug the response content
            response_content = response.choices[0].message.content
            print(f"[DEBUG] Summary length: {len(response_content)} characters")
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"[DEBUG] Error during API call: {str(e)}")
            raise e
    except Exception as e:
        # If API fails, return a placeholder
        print(f"Error generating summary: {str(e)}")
        return "Summary generation failed. Please try again later."

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 数据库测试端点
@app.get("/api/db-test")
async def test_db_connection(db: Session = Depends(get_db)):
    try:
        # 检查数据库连接
        db.execute("SELECT 1")
        
        # 获取表信息
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        # 获取用户数量
        user_count = db.query(User).count()
        
        # 获取摘要数量
        summary_count = db.query(Summary).count()
        
        return {
            "status": "connected",
            "tables": tables,
            "user_count": user_count,
            "summary_count": summary_count,
            "database_url": db.bind.url.render_as_string(hide_password=True)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

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
