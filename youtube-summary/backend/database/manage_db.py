import os
import sys
import time
import argparse
import getpass
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# 添加父目录到路径以便导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import Base
from database.models import User, Video, Summary, Tag, VideoTag
from auth.auth_utils import get_password_hash

# 获取数据库连接字符串
def get_connection_string():
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("警告: 环境变量中未找到DATABASE_URL。使用默认连接字符串。")
        db_url = "postgresql://youtube_summary:password@localhost:5432/youtube_summary"
    return db_url

# 创建数据库会话
def create_session():
    # 获取数据库连接字符串
    db_url = get_connection_string()
    
    # 创建引擎和会话
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    return session

# 打印分隔线
def print_separator(char="-", length=50):
    print(char * length)

# 用户相关功能
def create_user():
    """创建新用户"""
    session = create_session()
    
    try:
        # 获取用户输入
        username = input("请输入用户名: ")
        email = input("请输入电子邮件: ")
        password = getpass.getpass("请输入密码: ")
        
        # 检查用户名是否已存在
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"错误: 用户名 '{username}' 已存在")
            return False
        
        # 检查电子邮件是否已存在
        existing_email = session.query(User).filter(User.email == email).first()
        if existing_email:
            print(f"错误: 电子邮件 '{email}' 已存在")
            return False
        
        # 创建用户
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )
        
        # 添加并提交
        session.add(new_user)
        session.commit()
        
        print(f"成功创建用户 '{username}'!")
        return True
        
    except Exception as e:
        print(f"创建用户时出错: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def list_all_users():
    """列出所有用户"""
    session = create_session()
    
    try:
        users = session.query(User).all()
        
        if not users:
            print("没有找到用户")
            return
        
        print(f"找到 {len(users)} 个用户:")
        for user in users:
            print(f"ID: {user.id}, 用户名: {user.username}, 电子邮件: {user.email}, 创建时间: {user.created_at}")
            
    except Exception as e:
        print(f"列出用户时出错: {e}")
    finally:
        session.close()

def find_user_by_username(username):
    """通过用户名查找用户"""
    session = create_session()
    
    try:
        user = session.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"未找到用户名为 '{username}' 的用户")
            return None
        
        print(f"用户信息:")
        print(f"ID: {user.id}")
        print(f"用户名: {user.username}")
        print(f"电子邮件: {user.email}")
        print(f"创建时间: {user.created_at}")
        print(f"更新时间: {user.updated_at}")
        
        # 获取用户的摘要数量
        summary_count = session.query(func.count(Summary.id)).filter(Summary.user_id == user.id).scalar()
        print(f"摘要数量: {summary_count}")
        
        return user
            
    except Exception as e:
        print(f"查找用户时出错: {e}")
        return None
    finally:
        session.close()

def delete_user():
    """删除用户"""
    session = create_session()
    
    try:
        username = input("输入要删除的用户名: ")
        
        # 查找用户
        user = session.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"未找到用户名为 '{username}' 的用户")
            return False
        
        # 确认删除
        confirm = input(f"确定要删除用户 '{username}' 吗? 这将删除该用户的所有数据! (y/n): ")
        if confirm.lower() != 'y':
            print("取消删除")
            return False
        
        # 删除用户
        session.delete(user)
        session.commit()
        
        print(f"成功删除用户 '{username}'")
        return True
            
    except Exception as e:
        print(f"删除用户时出错: {e}")
        session.rollback()
        return False
    finally:
        session.close()

# 视频相关功能
def list_videos():
    """列出所有视频"""
    session = create_session()
    
    try:
        videos = session.query(Video).all()
        
        if not videos:
            print("没有找到视频")
            return
        
        print(f"找到 {len(videos)} 个视频:")
        for video in videos:
            print(f"ID: {video.id}, YouTube ID: {video.youtube_id}, 标题: {video.title}, 频道: {video.channel}")
            
    except Exception as e:
        print(f"列出视频时出错: {e}")
    finally:
        session.close()

def find_video(video_id=None, youtube_id=None):
    """通过ID或YouTube ID查找视频"""
    session = create_session()
    
    try:
        if video_id:
            video = session.query(Video).filter(Video.id == video_id).first()
        elif youtube_id:
            video = session.query(Video).filter(Video.youtube_id == youtube_id).first()
        else:
            print("错误: 必须提供视频ID或YouTube ID")
            return None
        
        if not video:
            print(f"未找到视频")
            return None
        
        print(f"视频信息:")
        print(f"ID: {video.id}")
        print(f"YouTube ID: {video.youtube_id}")
        print(f"标题: {video.title}")
        print(f"频道: {video.channel}")
        print(f"时长: {video.duration}秒")
        print(f"观看次数: {video.view_count}")
        print(f"点赞次数: {video.like_count}")
        
        # 获取视频的摘要数量
        summary_count = session.query(func.count(Summary.id)).filter(Summary.video_id == video.id).scalar()
        print(f"摘要数量: {summary_count}")
        
        # 获取视频的标签
        tags = [tag.name for tag in video.tags]
        print(f"标签: {', '.join(tags) if tags else '无'}")
        
        return video
            
    except Exception as e:
        print(f"查找视频时出错: {e}")
        return None
    finally:
        session.close()

def delete_video():
    """删除视频"""
    session = create_session()
    
    try:
        youtube_id = input("输入要删除的YouTube视频ID: ")
        
        # 查找视频
        video = session.query(Video).filter(Video.youtube_id == youtube_id).first()
        
        if not video:
            print(f"未找到YouTube ID为 '{youtube_id}' 的视频")
            return False
        
        # 确认删除
        confirm = input(f"确定要删除视频 '{video.title}' 吗? 这将删除与该视频相关的所有摘要! (y/n): ")
        if confirm.lower() != 'y':
            print("取消删除")
            return False
        
        # 删除视频
        session.delete(video)
        session.commit()
        
        print(f"成功删除视频 '{video.title}'")
        return True
            
    except Exception as e:
        print(f"删除视频时出错: {e}")
        session.rollback()
        return False
    finally:
        session.close()

# 摘要相关功能
def show_summary(summary_id):
    """显示特定摘要的详情"""
    session = create_session()
    
    try:
        summary = session.query(Summary).filter(Summary.id == summary_id).first()
        
        if not summary:
            print(f"未找到ID为 {summary_id} 的摘要")
            return None
        
        # 获取关联的视频和用户
        video = summary.video
        user = summary.user
        
        print(f"摘要ID: {summary.id}")
        print(f"视频: {video.title} (YouTube ID: {video.youtube_id})")
        print(f"用户: {user.username}")
        print(f"摘要类型: {summary.summary_type}")
        print(f"语言: {summary.language}")
        print(f"创建时间: {summary.created_at}")
        print(f"是否收藏: {'是' if summary.is_favorite else '否'}")
        print_separator()
        print("摘要内容:")
        print(summary.summary_text)
        
        return summary
            
    except Exception as e:
        print(f"显示摘要时出错: {e}")
        return None
    finally:
        session.close()

def list_user_summaries(username=None):
    """列出用户的摘要"""
    session = create_session()
    
    try:
        query = session.query(Summary, User, Video).\
            join(User, Summary.user_id == User.id).\
            join(Video, Summary.video_id == Video.id)
        
        if username:
            query = query.filter(User.username == username)
        
        results = query.all()
        
        if not results:
            print(f"没有找到摘要")
            return
        
        print(f"找到 {len(results)} 个摘要:")
        for summary, user, video in results:
            fav_mark = "★" if summary.is_favorite else " "
            print(f"{fav_mark} [ID: {summary.id}] {video.title} - 由 {user.username} 创建于 {summary.created_at}")
            
    except Exception as e:
        print(f"列出摘要时出错: {e}")
    finally:
        session.close()

def delete_summary():
    """删除摘要"""
    session = create_session()
    
    try:
        summary_id = input("输入要删除的摘要ID: ")
        
        try:
            summary_id = int(summary_id)
        except ValueError:
            print("错误: 摘要ID必须是数字")
            return False
        
        # 查找摘要
        summary = session.query(Summary).filter(Summary.id == summary_id).first()
        
        if not summary:
            print(f"未找到ID为 {summary_id} 的摘要")
            return False
        
        # 获取关联的视频和用户
        video = summary.video
        user = summary.user
        
        # 确认删除
        confirm = input(f"确定要删除视频 '{video.title}' 的摘要吗? (y/n): ")
        if confirm.lower() != 'y':
            print("取消删除")
            return False
        
        # 删除摘要
        session.delete(summary)
        session.commit()
        
        print(f"成功删除摘要")
        return True
            
    except Exception as e:
        print(f"删除摘要时出错: {e}")
        session.rollback()
        return False
    finally:
        session.close()

# 数据库统计
def show_database_stats():
    """显示数据库统计信息"""
    session = create_session()
    
    try:
        # 统计用户数量
        user_count = session.query(func.count(User.id)).scalar()
        print(f"用户数量: {user_count}")
        
        # 统计视频数量
        video_count = session.query(func.count(Video.id)).scalar()
        print(f"视频数量: {video_count}")
        
        # 统计摘要数量
        summary_count = session.query(func.count(Summary.id)).scalar()
        print(f"摘要数量: {summary_count}")
        
        # 统计标签数量
        tag_count = session.query(func.count(Tag.id)).scalar()
        print(f"标签数量: {tag_count}")
        
        if user_count > 0:
            # 查找拥有最多摘要的用户
            top_user = session.query(User, func.count(Summary.id).label('summary_count')).\
                outerjoin(Summary, User.id == Summary.user_id).\
                group_by(User.id).\
                order_by(func.count(Summary.id).desc()).\
                first()
            
            if top_user:
                user, count = top_user
                print(f"拥有最多摘要的用户: {user.username} ({count} 个摘要)")
        
        if video_count > 0:
            # 查找被最多人总结的视频
            top_video = session.query(Video, func.count(Summary.id).label('summary_count')).\
                outerjoin(Summary, Video.id == Summary.video_id).\
                group_by(Video.id).\
                order_by(func.count(Summary.id).desc()).\
                first()
            
            if top_video:
                video, count = top_video
                print(f"被最多人总结的视频: {video.title} ({count} 个摘要)")
            
    except Exception as e:
        print(f"显示统计信息时出错: {e}")
    finally:
        session.close()

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
        print("4. 删除摘要")
        print("0. 返回主菜单")
        print_separator()
        
        choice = input("选择操作 (0-4): ")
        
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
        sys.exit(0)
    except Exception as e:
        print(f"程序出错: {e}")
        sys.exit(1) 