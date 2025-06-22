#!/usr/bin/env python3
"""
YouTube Cookies Generator and Validator
用于生成和验证YouTube cookies的工具脚本

使用说明：
1. 首先确保你在Chrome中登录了YouTube
2. 运行此脚本生成cookies
3. 验证cookies是否有效
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# 设置路径
SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / 'transcripts_cache'
COOKIES_PATH = CACHE_DIR / 'cookies.txt'

def ensure_directories():
    """确保必要的目录存在"""
    CACHE_DIR.mkdir(exist_ok=True)
    print(f"✅ 缓存目录已创建: {CACHE_DIR}")

def check_prerequisites():
    """检查必要的工具是否安装"""
    print("🔍 检查必要工具...")
    
    # 检查yt-dlp
    try:
        result = subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ yt-dlp 已安装: {result.stdout.strip()}")
        else:
            print("❌ yt-dlp 未正确安装")
            return False
    except Exception as e:
        print(f"❌ yt-dlp 未安装或无法运行: {e}")
        print("请运行: pip install yt-dlp")
        return False
    
    return True

def generate_cookies_method1():
    """方法1: 使用yt-dlp从Chrome浏览器导出cookies"""
    print("\n🍪 方法1: 从Chrome浏览器导出cookies")
    print("⚠️  请确保:")
    print("   - Chrome浏览器已安装")
    print("   - 已在Chrome中登录YouTube")
    print("   - 在YouTube上看过几个视频")
    
    input("按Enter键继续...")
    
    try:
        # 构建命令
        cmd = [
            'yt-dlp',
            '--cookies-from-browser', 'chrome',
            '--cookies', str(COOKIES_PATH),
            '--skip-download',
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ'  # 使用一个测试视频
        ]
        
        print(f"🔄 执行命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Cookies 导出成功!")
            return True
        else:
            print(f"❌ Cookies 导出失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 导出过程出错: {e}")
        return False

def generate_cookies_method2():
    """方法2: 手动获取cookies（备用方法）"""
    print("\n🍪 方法2: 手动获取cookies")
    print("""
📝 手动步骤:
1. 打开Chrome浏览器
2. 登录YouTube (https://youtube.com)
3. 按F12打开开发者工具
4. 点击 Application 标签
5. 在左侧找到 Cookies > https://www.youtube.com
6. 复制所有cookies到文本文件
7. 将文件保存为cookies.txt格式

或者使用浏览器扩展:
- 安装 "Get cookies.txt LOCALLY" 扩展
- 在YouTube页面点击扩展图标
- 下载cookies.txt文件
""")
    
    choice = input("是否已经准备好cookies.txt文件? (y/n): ").lower()
    if choice == 'y':
        file_path = input("请输入cookies.txt文件的完整路径: ").strip()
        if os.path.exists(file_path):
            # 复制文件到正确位置
            import shutil
            shutil.copy(file_path, COOKIES_PATH)
            print(f"✅ Cookies文件已复制到: {COOKIES_PATH}")
            return True
        else:
            print("❌ 文件不存在")
            return False
    return False

def validate_cookies():
    """验证cookies是否有效"""
    print(f"\n🔍 验证cookies文件: {COOKIES_PATH}")
    
    if not COOKIES_PATH.exists():
        print("❌ Cookies文件不存在")
        return False
    
    # 检查文件大小
    file_size = COOKIES_PATH.stat().st_size
    print(f"📊 文件大小: {file_size} bytes")
    
    if file_size < 100:
        print("❌ Cookies文件太小，可能无效")
        return False
    
    # 检查文件内容
    try:
        with open(COOKIES_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 基本格式检查
        if 'youtube.com' not in content:
            print("❌ Cookies文件中没有YouTube相关内容")
            return False
        
        # 统计YouTube cookies数量
        youtube_count = content.count('youtube.com')
        print(f"📈 YouTube cookies数量: {youtube_count}")
        
        # 检查关键登录cookies
        login_cookies = ['SAPISID', 'SSID', 'SID', 'HSID', 'APISID']
        found_login = [cookie for cookie in login_cookies if cookie in content]
        
        if found_login:
            print(f"✅ 找到登录cookies: {', '.join(found_login)}")
        else:
            print("⚠️  未找到登录cookies，可能影响访问受限内容")
        
        # 检查文件年龄
        file_age = time.time() - COOKIES_PATH.stat().st_mtime
        age_hours = file_age / 3600
        print(f"⏰ Cookies文件年龄: {age_hours:.1f} 小时")
        
        if age_hours > 24:
            print("⚠️  Cookies文件较老，建议重新生成")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取cookies文件失败: {e}")
        return False

def test_cookies():
    """测试cookies是否能正常工作"""
    print("\n🧪 测试cookies有效性...")
    
    test_video_ids = [
        'dQw4w9WgXcQ',  # Rick Roll (公开视频)
        'JQIKobOcQ9k',  # 你之前测试失败的视频
    ]
    
    for video_id in test_video_ids:
        print(f"\n📹 测试视频: {video_id}")
        
        try:
            cmd = [
                'yt-dlp',
                '--cookies', str(COOKIES_PATH),
                '--list-subs',
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ 视频 {video_id} 可访问")
                if 'en' in result.stdout:
                    print("✅ 找到英文字幕")
                else:
                    print("⚠️  未找到英文字幕")
            else:
                print(f"❌ 视频 {video_id} 访问失败: {result.stderr}")
                
        except Exception as e:
            print(f"❌ 测试出错: {e}")

def backup_old_cookies():
    """备份旧的cookies文件"""
    if COOKIES_PATH.exists():
        backup_path = COOKIES_PATH.with_suffix('.txt.backup')
        import shutil
        shutil.copy(COOKIES_PATH, backup_path)
        print(f"📋 已备份旧cookies到: {backup_path}")

def main():
    """主函数"""
    print("🎯 YouTube Cookies 生成和验证工具")
    print("=" * 50)
    
    # 检查前置条件
    if not check_prerequisites():
        sys.exit(1)
    
    # 确保目录存在
    ensure_directories()
    
    # 备份旧cookies
    backup_old_cookies()
    
    # 选择生成方法
    print("\n🔧 选择cookies生成方法:")
    print("1. 从Chrome浏览器自动导出 (推荐)")
    print("2. 手动获取cookies")
    print("3. 只验证现有cookies")
    print("4. 只测试现有cookies")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    success = False
    
    if choice == '1':
        success = generate_cookies_method1()
    elif choice == '2':
        success = generate_cookies_method2()
    elif choice in ['3', '4']:
        success = True  # 跳过生成，直接验证
    else:
        print("❌ 无效选择")
        sys.exit(1)
    
    if success or choice in ['3', '4']:
        # 验证cookies
        if validate_cookies():
            print("\n✅ Cookies验证通过!")
            
            # 询问是否测试
            if choice != '4':
                test_choice = input("\n是否测试cookies有效性? (y/n): ").lower()
                if test_choice == 'y':
                    test_cookies()
            else:
                test_cookies()
            
            print(f"\n🎉 完成! Cookies文件位置: {COOKIES_PATH}")
            print("\n📝 下一步:")
            print("1. 将此cookies.txt文件提交到Git")
            print("2. 推送到GitHub让Render重新部署")
            print("3. 测试你的应用")
            
        else:
            print("\n❌ Cookies验证失败，请重试")
            sys.exit(1)
    else:
        print("\n❌ Cookies生成失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 