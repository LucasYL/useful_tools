#!/usr/bin/env python3
"""
获取免费代理并测试是否可以访问YouTube
"""

import requests
import concurrent.futures
import sys
import time
from youtube_transcript_api import YouTubeTranscriptApi

# 测试视频ID - Rick Astley - Never Gonna Give You Up
TEST_VIDEO = "dQw4w9WgXcQ"

def get_free_proxies():
    """从公共API获取免费代理列表"""
    proxies = []
    try:
        # 尝试从多个公共列表获取代理
        sources = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt",
        ]
        
        for source in sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    # 解析代理列表
                    proxy_text = response.text
                    for line in proxy_text.split('\n'):
                        line = line.strip()
                        if line and ":" in line:
                            # 添加协议前缀，如果没有
                            if not line.startswith('http'):
                                proxy = f"http://{line}"
                            else:
                                proxy = line
                            proxies.append(proxy)
                    print(f"从 {source} 获取了 {len(proxies)} 个代理")
            except Exception as e:
                print(f"从 {source} 获取代理时出错: {str(e)}")
                
        # 去重
        proxies = list(set(proxies))
        print(f"总共获取了 {len(proxies)} 个唯一代理")
        return proxies
    except Exception as e:
        print(f"获取代理时出错: {str(e)}")
        return []

def test_proxy(proxy):
    """测试代理是否可以访问YouTube"""
    proxies = {
        'http': proxy,
        'https': proxy,
    }
    
    try:
        # 测试是否可以访问YouTube
        start_time = time.time()
        # 设置较短的超时时间
        response = requests.get('https://www.youtube.com', proxies=proxies, timeout=5)
        basic_time = time.time() - start_time
        
        if response.status_code == 200:
            # 测试是否可以获取视频字幕
            try:
                transcript_start = time.time()
                transcript = YouTubeTranscriptApi.get_transcript(TEST_VIDEO, proxies=proxies)
                transcript_time = time.time() - transcript_start
                
                return {
                    'proxy': proxy,
                    'success': True,
                    'status_code': response.status_code,
                    'basic_time': round(basic_time, 2),
                    'transcript_time': round(transcript_time, 2),
                    'transcript_entries': len(transcript)
                }
            except Exception as e:
                return {
                    'proxy': proxy,
                    'success': False,
                    'status_code': response.status_code,
                    'basic_time': round(basic_time, 2),
                    'error': str(e)
                }
        else:
            return {
                'proxy': proxy,
                'success': False,
                'status_code': response.status_code,
                'basic_time': round(basic_time, 2),
            }
    except Exception as e:
        return {
            'proxy': proxy,
            'success': False,
            'error': str(e)
        }

def main():
    """主函数"""
    print("获取免费代理...")
    proxies = get_free_proxies()
    
    if not proxies:
        print("没有找到代理，退出。")
        return
    
    print(f"测试 {len(proxies)} 个代理...")
    successful_proxies = []
    
    # 使用线程池并行测试代理
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in proxies}
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_proxy)):
            proxy = future_to_proxy[future]
            try:
                result = future.result()
                
                # 更新进度
                if (i + 1) % 10 == 0 or (i + 1) == len(proxies):
                    print(f"测试进度: {i+1}/{len(proxies)}")
                
                if result.get('success', False):
                    # 如果可以获取字幕，添加到成功列表
                    if 'transcript_entries' in result:
                        successful_proxies.append(result)
                        print(f"找到工作代理! {proxy} (响应时间: {result['basic_time']}s, 字幕时间: {result['transcript_time']}s)")
            except Exception as e:
                print(f"测试代理 {proxy} 时出错: {str(e)}")
    
    # 按照速度排序
    if successful_proxies:
        successful_proxies.sort(key=lambda x: x.get('transcript_time', float('inf')))
        
        print("\n==== 可以获取YouTube字幕的代理 ====")
        for i, proxy in enumerate(successful_proxies[:5], 1):
            print(f"{i}. {proxy['proxy']}")
            print(f"   响应时间: {proxy['basic_time']}s, 字幕获取时间: {proxy['transcript_time']}s")
            print(f"   字幕条目数: {proxy['transcript_entries']}")
            print("")
        
        print("\n配置指南:")
        print("1. 在 .env 文件中添加以下内容:")
        best_proxy = successful_proxies[0]['proxy']
        print(f"PROXY_HTTP={best_proxy}")
        print(f"PROXY_HTTPS={best_proxy}")
        print("\n2. 重启您的应用")
    else:
        print("\n没有找到可以获取YouTube字幕的代理。")
        print("建议:")
        print("1. 使用不同的网络尝试")
        print("2. 考虑购买专业代理服务")
        print("3. 尝试使用VPN")

if __name__ == "__main__":
    main() 