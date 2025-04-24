import os
import sys
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置API基础URL
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def test_user_registration():
    """测试用户注册功能"""
    print("测试用户注册...")
    
    # 用户数据
    user_data = {
        "username": f"testuser_{os.urandom(4).hex()}",
        "email": f"test_{os.urandom(4).hex()}@example.com",
        "password": "TestPassword123!"
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
            print("用户注册成功!")
            print(f"用户ID: {response.json().get('id')}")
            return user_data
        else:
            print(f"用户注册失败: {response.status_code}")
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"请求错误: {e}")
        return None

def test_user_login(username, password):
    """测试用户登录功能"""
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
            print("用户登录成功!")
            print(f"令牌类型: {token_data.get('token_type')}")
            print(f"访问令牌: {access_token[:10]}...")
            return access_token
        else:
            print(f"用户登录失败: {response.status_code}")
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"请求错误: {e}")
        return None

def get_user_info(token):
    """获取当前用户信息"""
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
            print("获取用户信息成功!")
            print(f"用户ID: {user_info.get('id')}")
            print(f"用户名: {user_info.get('username')}")
            print(f"电子邮箱: {user_info.get('email')}")
            print(f"创建时间: {user_info.get('created_at')}")
            return user_info
        else:
            print(f"获取用户信息失败: {response.status_code}")
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"请求错误: {e}")
        return None

if __name__ == "__main__":
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
    
    print("=" * 50)
    print("测试完成!") 