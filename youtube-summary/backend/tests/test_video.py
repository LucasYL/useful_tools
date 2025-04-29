import sys
import os
import argparse
import json

# 将父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.youtube_utils import extract_video_id, get_video_metadata

def test_video_metadata(video_id_or_url: str):
    """
    测试获取YouTube视频元数据
    
    Args:
        video_id_or_url: YouTube视频ID或URL
    """
    try:
        # 提取视频ID
        video_id = extract_video_id(video_id_or_url)
        print(f"正在测试视频ID: {video_id}")
        
        # 获取视频元数据
        metadata = get_video_metadata(video_id)
        
        # 显示元数据
        print("\n===== 视频元数据 =====")
        print(f"标题: {metadata['title']}")
        print(f"频道: {metadata.get('channel', '未知')}")
        
        # 显示描述的前200个字符
        description = metadata.get('description', '')
        if description:
            print(f"描述: {description[:200]}...")
        else:
            print("描述: 无")
        
        # 显示章节信息
        chapters = metadata.get('chapters', [])
        if chapters:
            print(f"\n===== 章节信息 ({len(chapters)}个章节) =====")
            for i, chapter in enumerate(chapters):
                min_val = int(chapter['start_time'] // 60)
                sec_val = int(chapter['start_time'] % 60)
                print(f"{i+1}. [{min_val}:{sec_val:02d}] {chapter['title']}")
        else:
            print("\n视频没有章节信息")
        
        # 返回元数据
        return metadata
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='测试YouTube视频元数据提取')
    parser.add_argument('url', nargs='?', help='YouTube视频URL或ID')
    
    args = parser.parse_args()
    video_url = args.url
    
    if not video_url:
        # 如果未提供URL，提示用户输入
        video_url = input("请输入YouTube视频URL或ID: ")
        if not video_url:
            # 默认测试视频
            video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"测试视频: {video_url}")
    metadata = test_video_metadata(video_url)
    
    if metadata:
        print("\n===== 测试完成 =====")
        
        # 保存元数据到JSON文件
        output_file = f"{extract_video_id(video_url)}_metadata.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"元数据已保存到: {output_file}")
    else:
        print("\n===== 测试失败 =====") 