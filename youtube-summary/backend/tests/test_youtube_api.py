#!/usr/bin/env python3
"""
YouTube API测试脚本

这个脚本测试YouTube视频元数据和文本转录提取功能:
- 提取视频ID
- 获取视频元数据(标题、描述、章节)
- 生成带时间戳的增强文本
"""
import sys
import os
import json
import argparse
import time

# 将父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.youtube_utils import extract_video_id, get_video_metadata, get_transcript, create_enhanced_text

def test_enhanced_text_generation(video_id_or_url: str, save_output: bool = True):
    """
    测试YouTube视频的增强文本生成
    
    Args:
        video_id_or_url: YouTube视频URL或ID
        save_output: 是否保存测试结果到文件
        
    Returns:
        包含测试结果的字典，测试失败时返回None
    """
    try:
        print(f"===== YouTube增强文本生成测试 =====")
        
        # 提取视频ID
        video_id = extract_video_id(video_id_or_url)
        print(f"测试视频ID: {video_id}")
        
        start_time = time.time()
        
        # 获取视频元数据
        print("\n获取视频元数据...")
        metadata = get_video_metadata(video_id)
        print(f"✅ 成功获取视频元数据: {metadata['title']}")
        
        # 获取文本转录
        print("\n获取视频文本转录...")
        transcript = get_transcript(video_id)
        print(f"✅ 成功获取文本转录，共 {len(transcript)} 条记录")
        
        # 生成增强文本
        print("\n生成增强文本...")
        enhanced_text = create_enhanced_text(transcript)
        print(f"✅ 成功生成增强文本，长度 {len(enhanced_text)} 字符")
        
        # 计算视频时长
        if transcript and len(transcript) > 0:
            last_entry = transcript[-1]
            video_duration = last_entry['start'] + last_entry['duration']
            duration_str = f"{int(video_duration // 60)}:{int(video_duration % 60):02d}"
        else:
            duration_str = "未知"
            
        # 计算处理耗时
        elapsed_time = time.time() - start_time
        
        # 打印测试结果
        print("\n===== 测试结果 =====")
        print(f"视频标题: {metadata['title']}")
        print(f"频道: {metadata.get('channel', '未知')}")
        print(f"视频时长: {duration_str}")
        print(f"包含章节: {'是' if metadata.get('chapters') else '否'}")
        
        if metadata.get('chapters'):
            print(f"\n章节信息 ({len(metadata['chapters'])} 个章节):")
            for i, chapter in enumerate(metadata['chapters'][:5]):  # 只显示前5个
                mins = int(chapter['start_time'] // 60)
                secs = int(chapter['start_time'] % 60)
                print(f"- [{mins}:{secs:02d}] {chapter['title']}")
            if len(metadata['chapters']) > 5:
                print(f"... 还有 {len(metadata['chapters']) - 5} 个章节")
        
        print(f"\n文本转录样本 (前3条):")
        for i, entry in enumerate(transcript[:3]):
            print(f"- [{format_time(entry['start'])}] {entry['text']}")
        
        print(f"\n增强文本样本 (前200字符):")
        sample_text = enhanced_text[:200] + "..." if len(enhanced_text) > 200 else enhanced_text
        print(sample_text)
        
        print(f"\n处理耗时: {elapsed_time:.2f}秒")
        
        # 保存测试结果
        result = {
            "video_id": video_id,
            "title": metadata["title"],
            "channel": metadata.get("channel", ""),
            "has_chapters": bool(metadata.get("chapters")),
            "chapters_count": len(metadata.get("chapters", [])),
            "transcript_count": len(transcript),
            "enhanced_text_length": len(enhanced_text),
            "duration": duration_str,
            "processing_time": f"{elapsed_time:.2f}秒"
        }
        
        if save_output:
            save_test_results(video_id, metadata, transcript, enhanced_text)
            
        return result
        
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        return None

def format_time(seconds):
    """将秒数格式化为MM:SS格式"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

def save_test_results(video_id, metadata, transcript, enhanced_text):
    """保存测试结果到文件"""
    # 创建输出目录
    output_dir = f"output/{video_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存元数据
    with open(f"{output_dir}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # 保存文本转录
    with open(f"{output_dir}/transcript.json", "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)
    
    # 保存增强文本
    with open(f"{output_dir}/enhanced_text.txt", "w", encoding="utf-8") as f:
        f.write(enhanced_text)
    
    print(f"\n✅ 测试结果已保存到目录: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='测试YouTube视频元数据和文本转录提取')
    parser.add_argument('url', nargs='?', help='YouTube视频URL或ID')
    parser.add_argument('--no-save', action='store_true', help='不保存测试结果')
    
    args = parser.parse_args()
    video_url = args.url
    
    if not video_url:
        # 如果未提供URL，提示用户输入
        video_url = input("请输入YouTube视频URL或ID: ")
        if not video_url:
            # 默认测试视频 - Rick Astley - Never Gonna Give You Up
            video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"测试视频: {video_url}")
    result = test_enhanced_text_generation(video_url, not args.no_save)
    
    if result:
        print("\n✅ 测试成功完成!")
    else:
        print("\n❌ 测试失败，请查看上面的错误信息。") 