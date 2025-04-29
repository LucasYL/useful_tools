import re
import os
import json
import subprocess
from typing import Dict, Any, List
from youtube_transcript_api import YouTubeTranscriptApi

# Function to extract video ID from URL
def extract_video_id(url: str) -> str:
    """
    从YouTube URL中提取视频ID
    
    Args:
        url: YouTube URL或直接的视频ID
        
    Returns:
        视频ID字符串
    """
    regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return url  # 如果无法匹配，假设输入已经是视频ID

# Function to get video metadata using yt-dlp
def get_video_metadata(video_url: str) -> Dict[str, Any]:
    """
    使用yt-dlp获取YouTube视频的元数据
    
    Args:
        video_url: YouTube URL或视频ID
        
    Returns:
        包含标题、描述和章节的字典
        
    Raises:
        Exception: 如果元数据获取失败
    """
    try:
        # 确保有一个完整的URL
        if not video_url.startswith(('http://', 'https://')):
            video_url = f"https://www.youtube.com/watch?v={video_url}"
            
        # 运行yt-dlp获取元数据
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--print', 'webpage_url',
            '--write-info-json',
            '--no-warnings',
            '--quiet',
            video_url
        ]
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 获取视频ID以查找信息文件
        video_id = extract_video_id(video_url)
        info_filename = f"{video_id}.info.json"
        
        # 读取信息文件
        if os.path.exists(info_filename):
            with open(info_filename, 'r') as f:
                info = json.load(f)
                
            # 清理文件
            os.remove(info_filename)
            
            # 提取相关信息
            title = info.get('title', 'Untitled Video')
            description = info.get('description', '')
            
            # 提取章节
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
            # 如果未创建信息文件，尝试替代方法
            cmd = [
                'yt-dlp',
                '--skip-download',
                '--dump-json',
                video_url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                
                # 提取相关信息
                title = info.get('title', 'Untitled Video')
                description = info.get('description', '')
                
                # 提取章节
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

def get_transcript(video_id: str, max_entries: int = 500, max_chars: int = 50000) -> List[Dict[str, Any]]:
    """
    获取YouTube视频的文本转录，并在必要时进行采样以避免过大的数据量
    
    Args:
        video_id: YouTube视频ID
        max_entries: 最大条目数，超过此数量将进行采样
        max_chars: 最大字符数，超过此数量将进行裁剪
        
    Returns:
        包含文本、开始时间和持续时间的字典列表
        
    Raises:
        Exception: 如果获取文本转录失败
    """
    try:
        # 获取原始转录
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # 检查transcript长度
        print(f"原始transcript长度: {len(transcript)} 条")
        total_duration = 0
        if transcript and len(transcript) > 0:
            last_entry = transcript[-1]
            total_duration = last_entry['start'] + last_entry['duration']
            print(f"根据transcript估计视频时长: {int(total_duration // 60)}:{int(total_duration % 60):02d}")

        # 计算transcript的总文本长度
        transcript_text_length = sum(len(entry.get('text', '')) for entry in transcript)
        print(f"原始transcript文本总长度: {transcript_text_length} 字符")

        # 当transcript过长时，需要采样
        if len(transcript) > max_entries or transcript_text_length > max_chars:
            print(f"Transcript太长，将进行采样")
            
            # 确保覆盖整个视频范围
            if len(transcript) > max_entries:
                # 计算采样间隔
                step = max(1, len(transcript) // max_entries)
                print(f"采样间隔: 每{step}条取1条")
                
                # 采样
                sampled_transcript = []
                # 确保取第一条和最后一条
                sampled_transcript.append(transcript[0])
                
                # 对中间部分进行采样
                for i in range(step, len(transcript) - 1, step):
                    sampled_transcript.append(transcript[i])
                
                # 确保添加最后一条
                if transcript[-1] != sampled_transcript[-1]:
                    sampled_transcript.append(transcript[-1])
                
                transcript = sampled_transcript
                print(f"采样后transcript长度: {len(transcript)} 条")
                
                # 重新计算文本长度
                transcript_text_length = sum(len(entry.get('text', '')) for entry in transcript)
                print(f"采样后transcript文本总长度: {transcript_text_length} 字符")
            
            # 如果总字符数仍然超出限制，进一步裁剪文本
            if transcript_text_length > max_chars:
                print(f"采样后文本仍然过长，将进行字符级裁剪")
                char_ratio = max_chars / transcript_text_length
                for i in range(len(transcript)):
                    text = transcript[i].get('text', '')
                    max_entry_chars = int(len(text) * char_ratio)
                    if len(text) > max_entry_chars:
                        transcript[i]['text'] = text[:max_entry_chars] + "..."
                
                # 最终文本长度验证
                final_length = sum(len(entry.get('text', '')) for entry in transcript)
                print(f"最终transcript文本总长度: {final_length} 字符")
                
        return transcript
                
    except Exception as e:
        raise Exception(f"Error retrieving transcript: {str(e)}")

def create_enhanced_text(transcript: List[Dict[str, Any]]) -> str:
    """
    从transcript创建带有时间戳标记的增强文本
    
    Args:
        transcript: 包含文本转录条目的列表
        
    Returns:
        带有时间戳标记的增强文本字符串
    """
    enhanced_text = ""
    
    # 将每个转录条目转换为带有时间戳标记的格式
    for entry in transcript:
        # 将时间格式化为MM:SS
        minutes = int(entry['start'] // 60)
        seconds = int(entry['start'] % 60)
        time_marker = f"[{minutes}:{seconds:02d}] "
        
        # 添加带有时间戳标记的文本
        enhanced_text += time_marker + entry.get('text', '') + " "
    
    # 添加视频结束时间戳
    if transcript and len(transcript) > 0:
        last_entry = transcript[-1]
        video_duration = last_entry['start'] + last_entry['duration']
        minutes = int(video_duration // 60)
        seconds = int(video_duration % 60)
        enhanced_text += f"[{minutes}:{seconds:02d}] End of video."
    
    return enhanced_text 