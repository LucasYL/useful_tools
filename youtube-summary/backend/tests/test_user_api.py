#!/usr/bin/env python3
"""
用户API测试脚本

这个脚本测试YouTube Summary应用的用户相关API:
- 用户注册
- 用户登录
- 获取用户信息
"""
import os
import sys
import json
import requests
import argparse
from dotenv import load_dotenv

# 将父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
load_dotenv()

# 设置API基础URL
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def test_user_registration(username=None, email=None, password=None):
    """
    测试用户注册功能
    
    Args:
        username: 可选的指定用户名，如果不提供将生成随机用户名
        email: 可选的指定邮箱，如果不提供将生成随机邮箱
        password: 可选的指定密码，如果不提供将使用默认密码
        
    Returns:
        成功时返回用户数据字典，失败时返回None
    """
    print("测试用户注册...")
    
    # 用户数据
    user_data = {
        "username": username or f"testuser_{os.urandom(4).hex()}",
        "email": email or f"test_{os.urandom(4).hex()}@example.com",
        "password": password or "TestPassword123!"
    }
    
    print(f"注册用户: {user_data['username']} ({user_data['email']})")
    
    try:
        # 发送注册请求
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=user_data
        )
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 用户注册成功!")
            print(f"用户ID: {response.json().get('id')}")
            return user_data
        else:
            print(f"❌ 用户注册失败: {response.status_code}")
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求错误: {e}")
        return None

def test_user_login(username, password):
    """
    测试用户登录功能
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        成功时返回访问令牌，失败时返回None
    """
    print(f"\n测试用户登录 ({username})...")
    
    try:
        # 准备表单数据
        form_data = {
            "username": username,
            "password": password
        }
        
        # 发送登录请求
        response = requests.post(
            f"{API_BASE}/auth/token",
            data=form_data
        )
        
        # 检查响应
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print("✅ 用户登录成功!")
            print(f"令牌类型: {token_data.get('token_type')}")
            print(f"访问令牌: {access_token[:10]}...")
            return access_token
        else:
            print(f"❌ 用户登录失败: {response.status_code}")
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求错误: {e}")
        return None

def get_user_info(token):
    """
    获取当前用户信息
    
    Args:
        token: 访问令牌
        
    Returns:
        成功时返回用户信息字典，失败时返回None
    """
    print("\n获取用户信息...")
    
    try:
        # 发送请求
        response = requests.get(
            f"{API_BASE}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 检查响应
        if response.status_code == 200:
            user_info = response.json()
            print("✅ 获取用户信息成功!")
            print(f"用户ID: {user_info.get('id')}")
            print(f"用户名: {user_info.get('username')}")
            print(f"电子邮箱: {user_info.get('email')}")
            print(f"创建时间: {user_info.get('created_at')}")
            print(f"更新时间: {user_info.get('updated_at')}")
            if user_info.get('api_key'):
                print(f"API密钥: {user_info.get('api_key')[:8]}...")
            return user_info
        else:
            print(f"❌ 获取用户信息失败: {response.status_code}")
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求错误: {e}")
        return None

def test_existing_user(username, password):
    """测试已存在用户的登录和信息获取"""
    print(f"\n===== 测试已存在用户 =====")
    print(f"用户名: {username}")
    
    # 测试登录
    token = test_user_login(username, password)
    
    if token:
        # 获取用户信息
        user_info = get_user_info(token)
        return user_info
    
    return None

def run_full_test():
    """运行完整的用户API测试"""
    print(f"===== 用户API测试 =====")
    print(f"使用API端点: {API_BASE}")
    print("=" * 50)
    
    # 测试注册
    user_data = test_user_registration()
    
    if user_data:
        # 测试登录
        token = test_user_login(user_data["username"], user_data["password"])
        
        if token:
            # 获取用户信息
            user_info = get_user_info(token)
            
            if user_info:
                print("\n✅ 完整用户流程测试成功!")
            else:
                print("\n❌ 获取用户信息失败!")
        else:
            print("\n❌ 用户登录失败!")
    else:
        print("\n❌ 用户注册失败!")
    
    print("=" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='测试YouTube Summary用户API')
    parser.add_argument('--username', help='测试用户名')
    parser.add_argument('--password', help='测试用户密码')
    parser.add_argument('--email', help='测试用户邮箱')
    
    args = parser.parse_args()
    
    # 如果提供了用户名和密码，测试已存在的用户
    if args.username and args.password:
        test_existing_user(args.username, args.password)
    # 如果提供了用户名或邮箱，但没有足够的信息，报错
    elif args.username or args.email:
        if not (args.username and args.email and args.password):
            print("❌ 错误: 如果要测试特定用户，请同时提供用户名、密码和邮箱!")
            sys.exit(1)
        # 测试注册指定用户
        user_data = test_user_registration(args.username, args.email, args.password)
        if user_data:
            test_user_login(user_data["username"], user_data["password"])
    else:
        # 运行完整测试
        run_full_test()
    
    print("\n测试完成!") 