import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 修改Python路径以包含backend目录
sys.path.append(os.path.join(os.path.dirname(__file__), 'youtube-summary/backend'))

# 使用相对导入
from auth_utils import get_password_hash  
from models import User, Summary, Base

# 加载环境变量
load_dotenv()

# 获取数据库URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("错误: 未设置DATABASE_URL环境变量")
    sys.exit(1)

# 如果URL开始于"postgres://"，将其转换为"postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 创建数据库引擎和会话
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 用户管理功能
def list_users():
    """列出所有用户"""
    session = SessionLocal()
    try:
        users = session.query(User).all()
        if not users:
            print("没有找到用户。")
            return
        
        print("\n用户列表:")
        print("-" * 60)
        print(f"{'ID':<5} {'用户名':<15} {'电子邮件':<25} {'已验证':<10}")
        print("-" * 60)
        
        for user in users:
            print(f"{user.id:<5} {user.username:<15} {user.email:<25} {'是' if user.is_verified else '否':<10}")
        
        print("-" * 60)
    finally:
        session.close()

def find_user():
    """查找用户"""
    search_term = input("请输入用户名或电子邮件: ")
    session = SessionLocal()
    try:
        users = session.query(User).filter(
            (User.username.ilike(f"%{search_term}%")) | 
            (User.email.ilike(f"%{search_term}%"))
        ).all()
        
        if not users:
            print(f"没有找到匹配 '{search_term}' 的用户。")
            return
        
        print("\n查找结果:")
        print("-" * 60)
        print(f"{'ID':<5} {'用户名':<15} {'电子邮件':<25} {'已验证':<10}")
        print("-" * 60)
        
        for user in users:
            print(f"{user.id:<5} {user.username:<15} {user.email:<25} {'是' if user.is_verified else '否':<10}")
        
        print("-" * 60)
    finally:
        session.close()

def create_user():
    """创建新用户"""
    username = input("输入用户名: ")
    email = input("输入电子邮件: ")
    password = input("输入密码: ")
    
    session = SessionLocal()
    try:
        # 检查用户名是否已存在
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"错误: 用户名 '{username}' 已被使用。")
            return
        
        # 检查电子邮件是否已存在
        existing_email = session.query(User).filter(User.email == email).first()
        if existing_email:
            print(f"错误: 电子邮件 '{email}' 已被使用。")
            return
        
        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_verified=False
        )
        
        session.add(new_user)
        session.commit()
        print(f"成功创建用户: {username}")
    except Exception as e:
        session.rollback()
        print(f"创建用户时出错: {str(e)}")
    finally:
        session.close()

def delete_user():
    """删除用户"""
    user_id = input("输入要删除的用户ID: ")
    try:
        user_id = int(user_id)
    except ValueError:
        print("错误: 用户ID必须是一个数字。")
        return
    
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"错误: 未找到ID为 {user_id} 的用户。")
            return
        
        confirm = input(f"确认删除用户 '{user.username}' (y/n): ").lower()
        if confirm != 'y':
            print("操作已取消。")
            return
        
        # 删除用户的所有总结
        summaries = session.query(Summary).filter(Summary.user_id == user_id).all()
        for summary in summaries:
            session.delete(summary)
        
        # 删除用户
        session.delete(user)
        session.commit()
        print(f"已成功删除用户 '{user.username}' 及其所有内容。")
    except Exception as e:
        session.rollback()
        print(f"删除用户时出错: {str(e)}")
    finally:
        session.close()

# 总结管理功能
def list_summaries(user_id=None):
    """列出总结"""
    session = SessionLocal()
    try:
        query = session.query(Summary)
        if user_id:
            query = query.filter(Summary.user_id == user_id)
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                print(f"错误: 未找到ID为 {user_id} 的用户。")
                return
            print(f"\n用户 '{user.username}' 的总结:")
        else:
            print("\n所有总结:")
        
        summaries = query.all()
        if not summaries:
            print("没有找到总结。")
            return
        
        print("-" * 100)
        print(f"{'ID':<5} {'标题':<30} {'用户ID':<8} {'创建时间':<20} {'收藏':<5}")
        print("-" * 100)
        
        for summary in summaries:
            title = summary.title if len(summary.title) <= 27 else summary.title[:27] + "..."
            created_at = summary.created_at.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{summary.id:<5} {title:<30} {summary.user_id:<8} {created_at:<20} {'是' if summary.is_favorite else '否':<5}")
        
        print("-" * 100)
    finally:
        session.close()

def show_summary():
    """显示总结详情"""
    summary_id = input("输入要查看的总结ID: ")
    try:
        summary_id = int(summary_id)
    except ValueError:
        print("错误: 总结ID必须是一个数字。")
        return
    
    session = SessionLocal()
    try:
        summary = session.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            print(f"错误: 未找到ID为 {summary_id} 的总结。")
            return
        
        user = session.query(User).filter(User.id == summary.user_id).first()
        username = user.username if user else "未知用户"
        
        print("\n总结详情:")
        print("-" * 80)
        print(f"ID: {summary.id}")
        print(f"标题: {summary.title}")
        print(f"用户: {username} (ID: {summary.user_id})")
        print(f"YouTube链接: {summary.youtube_link}")
        print(f"创建时间: {summary.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"收藏: {'是' if summary.is_favorite else '否'}")
        print("-" * 80)
        print("内容:")
        print(summary.content)
        print("-" * 80)
    finally:
        session.close()

def delete_summary():
    """删除总结"""
    summary_id = input("输入要删除的总结ID: ")
    try:
        summary_id = int(summary_id)
    except ValueError:
        print("错误: 总结ID必须是一个数字。")
        return
    
    session = SessionLocal()
    try:
        summary = session.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            print(f"错误: 未找到ID为 {summary_id} 的总结。")
            return
        
        confirm = input(f"确认删除标题为 '{summary.title}' 的总结 (y/n): ").lower()
        if confirm != 'y':
            print("操作已取消。")
            return
        
        session.delete(summary)
        session.commit()
        print(f"已成功删除总结 '{summary.title}'。")
    except Exception as e:
        session.rollback()
        print(f"删除总结时出错: {str(e)}")
    finally:
        session.close()

def toggle_favorite():
    """切换总结的收藏状态"""
    summary_id = input("输入要切换收藏状态的总结ID: ")
    try:
        summary_id = int(summary_id)
    except ValueError:
        print("错误: 总结ID必须是一个数字。")
        return
    
    session = SessionLocal()
    try:
        summary = session.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            print(f"错误: 未找到ID为 {summary_id} 的总结。")
            return
        
        summary.is_favorite = not summary.is_favorite
        session.commit()
        status = "收藏" if summary.is_favorite else "取消收藏"
        print(f"已成功{status}总结 '{summary.title}'。")
    except Exception as e:
        session.rollback()
        print(f"更新收藏状态时出错: {str(e)}")
    finally:
        session.close()

def list_user_summaries():
    """列出特定用户的总结"""
    user_id = input("输入用户ID: ")
    try:
        user_id = int(user_id)
    except ValueError:
        print("错误: 用户ID必须是一个数字。")
        return
    
    list_summaries(user_id)

# 主菜单
def main_menu():
    while True:
        print("\n数据库管理工具")
        print("=" * 20)
        print("用户管理:")
        print("1. 列出所有用户")
        print("2. 查找用户")
        print("3. 创建新用户")
        print("4. 删除用户")
        print("\n总结管理:")
        print("5. 列出所有总结")
        print("6. 列出特定用户的总结")
        print("7. 显示总结详情")
        print("8. 删除总结")
        print("9. 切换总结收藏状态")
        print("\n0. 退出")
        
        choice = input("\n请选择操作 (0-9): ")
        
        if choice == '0':
            print("退出程序。")
            break
        elif choice == '1':
            list_users()
        elif choice == '2':
            find_user()
        elif choice == '3':
            create_user()
        elif choice == '4':
            delete_user()
        elif choice == '5':
            list_summaries()
        elif choice == '6':
            list_user_summaries()
        elif choice == '7':
            show_summary()
        elif choice == '8':
            delete_summary()
        elif choice == '9':
            toggle_favorite()
        else:
            print("无效选择，请重试。")

if __name__ == "__main__":
    # 检查数据库中是否存在表
    inspector = inspect(engine)
    if not inspector.has_table("users") or not inspector.has_table("summaries"):
        print("警告: 数据库中缺少必要的表。")
        create_tables = input("是否创建所需的表? (y/n): ").lower()
        if create_tables == 'y':
            Base.metadata.create_all(bind=engine)
            print("已成功创建表。")
        else:
            print("未创建表，程序可能无法正常运行。")
    
    main_menu() 