import sys
import os
import argparse
import json
import time

# 将父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.youtube_utils import extract_video_id, get_transcript

def test_transcript(video_id_or_url: str, debug_mode: bool = False):
    """
    测试获取YouTube视频字幕
    
    Args:
        video_id_or_url: YouTube视频ID或URL
        debug_mode: 是否显示详细信息
    """
    try:
        # 提取视频ID
        video_id = extract_video_id(video_id_or_url)
        print(f"正在测试视频ID: {video_id}")
        
        # 记录开始时间
        start_time = time.time()
        
        # 获取字幕
        transcript = get_transcript(video_id)
        
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
        print(f"\n===== 字幕信息 =====")
        print(f"获取耗时: {elapsed_time:.2f}秒")
        print(f"字幕片段数量: {len(transcript)}")
        print(f"字幕总时长: {int(total_duration//60)}分{int(total_duration%60)}秒")
        print(f"字幕总字符数: {sum(len(item['text']) for item in transcript)}")
        
        # 如果启用调试模式，显示更多详细信息
        if debug_mode:
            print("\n===== 字幕详情 =====")
            # 显示前3个片段
            for i, segment in enumerate(transcript[:3]):
                print(f"片段 {i+1}: [{segment['start']:.2f} - {segment['start']+segment['duration']:.2f}] {segment['text']}")
            
            print("...")
            
            # 显示后3个片段
            for i, segment in enumerate(transcript[-3:]):
                idx = len(transcript) - 3 + i
                print(f"片段 {idx+1}: [{segment['start']:.2f} - {segment['start']+segment['duration']:.2f}] {segment['text']}")
                
            # 检查字幕覆盖情况
            gaps = []
            for i in range(1, len(transcript)):
                prev_end = transcript[i-1]['start'] + transcript[i-1]['duration']
                curr_start = transcript[i]['start']
                gap = curr_start - prev_end
                if gap > 1.0:  # 如果间隔超过1秒
                    gaps.append((i-1, i, gap))
            
            if gaps:
                print(f"\n发现 {len(gaps)} 个大于1秒的字幕间隔:")
                for prev_idx, curr_idx, gap in gaps[:5]:  # 只显示前5个
                    prev = transcript[prev_idx]
                    curr = transcript[curr_idx]
                    print(f"间隔 {gap:.2f}秒: 在时间 {prev['start']+prev['duration']:.2f} 到 {curr['start']:.2f} 之间")
                    print(f"  前一片段: {prev['text']}")
                    print(f"  后一片段: {curr['text']}")
            else:
                print("\n字幕覆盖良好，未发现明显间隔")
        
        # 返回字幕数据
        return transcript
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='测试YouTube视频字幕提取')
    parser.add_argument('url', nargs='?', help='YouTube视频URL或ID')
    parser.add_argument('--debug', '-d', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    video_url = args.url
    debug_mode = args.debug
    
    if not video_url:
        # 如果未提供URL，提示用户输入
        video_url = input("请输入YouTube视频URL或ID: ")
        if not video_url:
            # 默认测试视频
            video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"测试视频: {video_url}")
    transcript = test_transcript(video_url, debug_mode)
    
    if transcript:
        print("\n===== 测试完成 =====")
        
        # 保存字幕到JSON文件
        output_file = f"{extract_video_id(video_url)}_transcript.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)
        
        print(f"字幕已保存到: {output_file}")
    else:
        print("\n===== 测试失败 =====") 