import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db import Base
from models import User, Summary
from auth_utils import get_password_hash
from datetime import datetime

# 加载环境变量
load_dotenv()

# 获取数据库URL
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("错误: 未找到DATABASE_URL环境变量")
    sys.exit(1)

# 创建数据库引擎和会话
print(f"连接到数据库: {database_url.replace(':'.join(database_url.split(':')[2:3]), ':***')}")
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

def print_separator():
    """打印分隔线"""
    print("=" * 50)

# 用户管理函数
def list_all_users():
    """列出所有用户"""
    try:
        users = session.query(User).all()
        print(f"用户总数: {len(users)}")
        if users:
            print(f"{'ID':<5} {'用户名':<20} {'邮箱':<30} {'创建时间':<20}")
            print("-" * 80)
            for user in users:
                print(f"{user.id:<5} {user.username:<20} {user.email:<30} {user.created_at}")
        return users
    except Exception as e:
        print(f"列出用户时出错: {e}")
        return []

def find_user_by_username(username):
    """根据用户名查找用户"""
    try:
        user = session.query(User).filter(User.username == username).first()
        if user:
            print(f"找到用户:")
            print(f"ID: {user.id}")
            print(f"用户名: {user.username}")
            print(f"邮箱: {user.email}")
            print(f"创建时间: {user.created_at}")
            if user.last_login:
                print(f"最后登录时间: {user.last_login}")
        else:
            print(f"未找到用户: {username}")
        return user
    except Exception as e:
        print(f"查找用户时出错: {e}")
        return None

def create_user():
    """创建新用户"""
    try:
        username = input("输入新用户名: ")
        email = input("输入电子邮箱: ")
        password = input("输入密码: ")
        
        # 检查用户名是否已存在
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"错误: 用户名 '{username}' 已存在")
            return None
            
        # 检查邮箱是否已存在
        existing_email = session.query(User).filter(User.email == email).first()
        if existing_email:
            print(f"错误: 邮箱 '{email}' 已被注册")
            return None
        
        # 创建新用户
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            created_at=datetime.utcnow()
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        print(f"已创建用户 {username} (ID: {new_user.id})")
        return new_user
    except Exception as e:
        session.rollback()
        print(f"创建用户时出错: {e}")
        return None

def delete_user():
    """删除用户"""
    try:
        username = input("输入要删除的用户名: ")
        user = session.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"未找到用户: {username}")
            return False
            
        # 显示用户信息并确认删除
        print(f"用户信息:")
        print(f"ID: {user.id}")
        print(f"用户名: {user.username}")
        print(f"邮箱: {user.email}")
        
        confirm = input(f"确定要删除用户 '{username}' 吗? 此操作将删除所有相关摘要。(y/n): ")
        if confirm.lower() != 'y':
            print("取消删除操作")
            return False
            
        # 删除用户及其摘要
        session.delete(user)  # 由于在模型中设置了级联删除，这会自动删除关联的摘要
        session.commit()
        
        print(f"已删除用户 '{username}' 及其所有摘要")
        return True
    except Exception as e:
        session.rollback()
        print(f"删除用户时出错: {e}")
        return False

# 摘要管理函数
def list_user_summaries(user_id=None, username=None):
    """列出用户的摘要"""
    try:
        # 如果提供了用户名而不是ID，则通过用户名查找用户
        if username and not user_id:
            user = session.query(User).filter(User.username == username).first()
            if not user:
                print(f"未找到用户: {username}")
                return []
            user_id = user.id
            
        # 构建查询
        query = session.query(Summary)
        if user_id:
            query = query.filter(Summary.user_id == user_id)
            
        # 执行查询
        summaries = query.all()
        
        # 显示结果
        user_info = f"用户ID {user_id}" if user_id else "所有用户"
        print(f"{user_info} 的摘要数量: {len(summaries)}")
        
        if summaries:
            print(f"{'ID':<5} {'用户ID':<10} {'视频ID':<15} {'标题':<30} {'类型':<10} {'语言':<5} {'创建时间':<20}")
            print("-" * 100)
            for summary in summaries:
                title = summary.video_title[:27] + "..." if len(summary.video_title) > 30 else summary.video_title
                print(f"{summary.id:<5} {summary.user_id:<10} {summary.video_id:<15} {title:<30} {summary.summary_type:<10} {summary.language:<5} {summary.created_at}")
        
        return summaries
    except Exception as e:
        print(f"列出摘要时出错: {e}")
        return []

def show_summary(summary_id):
    """显示特定摘要的详细内容"""
    try:
        summary = session.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            print(f"未找到ID为 {summary_id} 的摘要")
            return None
            
        # 显示摘要信息
        print(f"摘要ID: {summary.id}")
        print(f"用户ID: {summary.user_id}")
        print(f"视频ID: {summary.video_id}")
        print(f"视频标题: {summary.video_title}")
        print(f"摘要类型: {summary.summary_type}")
        print(f"语言: {summary.language}")
        print(f"创建时间: {summary.created_at}")
        print(f"收藏状态: {'已收藏' if summary.is_favorite else '未收藏'}")
        print(f"\n摘要内容:")
        print("-" * 50)
        print(summary.summary_text)
        print("-" * 50)
        
        return summary
    except Exception as e:
        print(f"显示摘要时出错: {e}")
        return None

def delete_summary():
    """删除特定摘要"""
    try:
        summary_id = input("输入要删除的摘要ID: ")
        try:
            summary_id = int(summary_id)
        except ValueError:
            print("错误: 摘要ID必须是数字")
            return False
            
        summary = session.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            print(f"未找到ID为 {summary_id} 的摘要")
            return False
            
        # 显示摘要信息并确认删除
        print(f"摘要信息:")
        print(f"ID: {summary.id}")
        print(f"视频标题: {summary.video_title}")
        print(f"用户ID: {summary.user_id}")
        
        confirm = input(f"确定要删除这个摘要吗? (y/n): ")
        if confirm.lower() != 'y':
            print("取消删除操作")
            return False
            
        # 删除摘要
        session.delete(summary)
        session.commit()
        
        print(f"已删除ID为 {summary_id} 的摘要")
        return True
    except Exception as e:
        session.rollback()
        print(f"删除摘要时出错: {e}")
        return False

def toggle_favorite():
    """切换摘要的收藏状态"""
    try:
        summary_id = input("输入要切换收藏状态的摘要ID: ")
        try:
            summary_id = int(summary_id)
        except ValueError:
            print("错误: 摘要ID必须是数字")
            return False
            
        summary = session.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            print(f"未找到ID为 {summary_id} 的摘要")
            return False
            
        # 切换收藏状态
        summary.is_favorite = not summary.is_favorite
        session.commit()
        
        new_status = "已收藏" if summary.is_favorite else "未收藏"
        print(f"ID为 {summary_id} 的摘要收藏状态已更改为: {new_status}")
        return True
    except Exception as e:
        session.rollback()
        print(f"切换收藏状态时出错: {e}")
        return False

# 数据库统计和信息
def show_database_stats():
    """显示数据库统计信息"""
    try:
        user_count = session.query(User).count()
        summary_count = session.query(Summary).count()
        
        print("数据库统计:")
        print(f"用户数量: {user_count}")
        print(f"摘要数量: {summary_count}")
        
        if user_count > 0:
            # 获取最近注册的用户
            latest_user = session.query(User).order_by(User.created_at.desc()).first()
            print(f"最近注册用户: {latest_user.username} (注册于 {latest_user.created_at})")
            
        if summary_count > 0:
            # 获取最近创建的摘要
            latest_summary = session.query(Summary).order_by(Summary.created_at.desc()).first()
            print(f"最近创建摘要: {latest_summary.video_title} (创建于 {latest_summary.created_at})")
            
            # 获取收藏的摘要数量
            favorited_count = session.query(Summary).filter(Summary.is_favorite == True).count()
            print(f"收藏的摘要数量: {favorited_count}")
    except Exception as e:
        print(f"显示数据库统计时出错: {e}")

# 主菜单
def main_menu():
    """显示主菜单并处理用户输入"""
    while True:
        print_separator()
        print("YouTube视频摘要工具 - 数据库管理")
        print_separator()
        print("1. 用户管理")
        print("2. 摘要管理")
        print("3. 数据库统计")
        print("0. 退出")
        print_separator()
        
        choice = input("选择操作 (0-3): ")
        
        if choice == '1':
            user_menu()
        elif choice == '2':
            summary_menu()
        elif choice == '3':
            print_separator()
            show_database_stats()
            input("按Enter键继续...")
        elif choice == '0':
            print("退出程序...")
            session.close()
            sys.exit(0)
        else:
            print("无效的选择，请重试")

def user_menu():
    """用户管理菜单"""
    while True:
        print_separator()
        print("用户管理")
        print_separator()
        print("1. 列出所有用户")
        print("2. 查找用户")
        print("3. 创建新用户")
        print("4. 删除用户")
        print("0. 返回主菜单")
        print_separator()
        
        choice = input("选择操作 (0-4): ")
        
        if choice == '1':
            print_separator()
            list_all_users()
            input("按Enter键继续...")
        elif choice == '2':
            print_separator()
            username = input("输入要查找的用户名: ")
            find_user_by_username(username)
            input("按Enter键继续...")
        elif choice == '3':
            print_separator()
            create_user()
            input("按Enter键继续...")
        elif choice == '4':
            print_separator()
            delete_user()
            input("按Enter键继续...")
        elif choice == '0':
            return
        else:
            print("无效的选择，请重试")

def summary_menu():
    """摘要管理菜单"""
    while True:
        print_separator()
        print("摘要管理")
        print_separator()
        print("1. 列出所有摘要")
        print("2. 列出特定用户的摘要")
        print("3. 查看摘要详情")
        print("4. 切换摘要收藏状态")
        print("5. 删除摘要")
        print("0. 返回主菜单")
        print_separator()
        
        choice = input("选择操作 (0-5): ")
        
        if choice == '1':
            print_separator()
            list_user_summaries()
            input("按Enter键继续...")
        elif choice == '2':
            print_separator()
            username = input("输入用户名: ")
            list_user_summaries(username=username)
            input("按Enter键继续...")
        elif choice == '3':
            print_separator()
            summary_id = input("输入摘要ID: ")
            try:
                show_summary(int(summary_id))
            except ValueError:
                print("错误: 摘要ID必须是数字")
            input("按Enter键继续...")
        elif choice == '4':
            print_separator()
            toggle_favorite()
            input("按Enter键继续...")
        elif choice == '5':
            print_separator()
            delete_summary()
            input("按Enter键继续...")
        elif choice == '0':
            return
        else:
            print("无效的选择，请重试")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        session.close()
        sys.exit(0)
    except Exception as e:
        print(f"程序出错: {e}")
        session.close()
        sys.exit(1)
    finally:
        session.close() 