import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

def test_database_connection():
    # 加载环境变量
    load_dotenv()
    
    # 获取数据库URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("错误: 未找到DATABASE_URL环境变量")
        sys.exit(1)
    
    print(f"测试连接到: {database_url.replace(':'.join(database_url.split(':')[2:3]), ':***')}")
    
    try:
        # 创建引擎
        engine = create_engine(database_url)
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("数据库连接成功!")
            
            # 获取表信息
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"数据库中的表: {tables}")
            
            # 检查是否存在用户和摘要表
            if 'users' in tables and 'summaries' in tables:
                # 获取表计数
                users_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                summaries_count = conn.execute(text("SELECT COUNT(*) FROM summaries")).scalar()
                
                print(f"用户表中的记录数: {users_count}")
                print(f"摘要表中的记录数: {summaries_count}")
            else:
                missing_tables = []
                if 'users' not in tables:
                    missing_tables.append('users')
                if 'summaries' not in tables:
                    missing_tables.append('summaries')
                print(f"警告: 未找到以下表: {', '.join(missing_tables)}")
                print("这可能意味着数据库表尚未创建。")
        
        return True
    except SQLAlchemyError as e:
        print(f"数据库连接错误: {e}")
        return False

if __name__ == "__main__":
    print("开始测试数据库连接...")
    success = test_database_connection()
    print("测试完成。" + ("成功!" if success else "失败!")) 