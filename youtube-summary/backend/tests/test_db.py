#!/usr/bin/env python3
"""
Database Connection Test Script
这个脚本测试YouTube Summary数据库的连接并显示基本的表信息
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

# 将父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
load_dotenv()

def get_connection_string():
    """从环境变量获取数据库连接字符串或使用默认值"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("警告: 环境变量中未找到DATABASE_URL。使用默认连接字符串。")
        db_url = "postgresql://youtube_summary:password@localhost:5432/youtube_summary"
    return db_url

def test_sqlalchemy_connection():
    """使用SQLAlchemy测试数据库连接"""
    print("\n===== SQLAlchemy 连接测试 =====")
    
    # 获取数据库URL
    database_url = get_connection_string()
    masked_url = database_url.replace(':'.join(database_url.split(':')[2:3]), ':***')
    print(f"测试连接到: {masked_url}")
    
    try:
        # 创建引擎
        engine = create_engine(database_url)
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ 数据库连接成功!")
            
            # 获取表信息
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"数据库中的表: {', '.join(tables)}")
            
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
                print(f"⚠️ 警告: 未找到以下表: {', '.join(missing_tables)}")
                print("这可能意味着数据库表尚未创建。")
        
        return True
    except SQLAlchemyError as e:
        print(f"❌ 数据库连接错误: {e}")
        return False

def get_psycopg2_connection():
    """使用psycopg2建立数据库连接"""
    connection_string = get_connection_string()
    try:
        print(f"尝试连接到数据库...")
        conn = psycopg2.connect(connection_string)
        print("✅ 连接成功!")
        return conn
    except psycopg2.Error as e:
        print(f"❌ 连接数据库出错: {e}")
        return None

def display_table_info(cursor, table_name):
    """显示表的详细信息"""
    print(f"\n表: {table_name}")
    
    # 获取列信息
    cursor.execute(f"""
    SELECT column_name, data_type, character_maximum_length 
    FROM information_schema.columns 
    WHERE table_name = '{table_name}'
    """)
    columns = cursor.fetchall()
    
    print("列:")
    for col in columns:
        col_name, data_type, max_length = col
        if max_length:
            print(f"  - {col_name} ({data_type}({max_length}))")
        else:
            print(f"  - {col_name} ({data_type})")
    
    # 获取行数
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    print(f"总行数: {row_count}")
    
    # 如果表有数据则显示样例数据
    if row_count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        
        # 获取列名用于美观打印
        column_names = [desc[0] for desc in cursor.description]
        
        print("样例数据:")
        for row in rows:
            print("  行:")
            for i, value in enumerate(row):
                # 截断长文本值以便显示
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + "..."
                print(f"    {column_names[i]}: {value}")

def test_psycopg2_connection():
    """使用psycopg2测试数据库连接并显示架构信息"""
    print("\n===== Psycopg2 连接测试 =====")
    
    conn = get_psycopg2_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    success = True
    
    try:
        # 获取表列表
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        """)
        tables = cursor.fetchall()
        
        if not tables:
            print("⚠️ 数据库中未找到表。")
            return True
        
        print(f"\n在数据库中找到 {len(tables)} 个表:")
        for table in tables:
            table_name = table[0]
            display_table_info(cursor, table_name)
            
        print("\n✅ 数据库连接测试成功完成!")
            
    except psycopg2.Error as e:
        print(f"❌ 查询数据库出错: {e}")
        success = False
    finally:
        cursor.close()
        conn.close()
        print("数据库连接已关闭。")
    
    return success

def main():
    """主函数，运行所有数据库测试"""
    print("===== 开始数据库测试 =====")
    
    # 测试SQLAlchemy连接
    sqlalchemy_success = test_sqlalchemy_connection()
    
    # 测试Psycopg2连接和表信息
    psycopg2_success = test_psycopg2_connection()
    
    # 打印总结
    print("\n===== 测试结果 =====")
    print(f"SQLAlchemy 连接测试: {'✅ 成功' if sqlalchemy_success else '❌ 失败'}")
    print(f"Psycopg2 连接和表信息测试: {'✅ 成功' if psycopg2_success else '❌ 失败'}")
    
    if sqlalchemy_success and psycopg2_success:
        print("\n✅ 所有测试都成功完成!")
        return True
    else:
        print("\n⚠️ 部分测试失败，请查看上面的错误信息。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 