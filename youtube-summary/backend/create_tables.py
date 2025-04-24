import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from db import Base
from models import User, Summary

# 加载环境变量
load_dotenv()

# 获取数据库URL
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("错误: 未找到DATABASE_URL环境变量")
    exit(1)

print(f"正在连接到数据库: {database_url.replace(':'.join(database_url.split(':')[2:3]), ':***')}")

# 创建引擎
engine = create_engine(database_url)

# 创建表
print("正在创建数据库表...")
Base.metadata.create_all(bind=engine)

print("数据库表创建完成!")
print("已创建的表:")
for table in Base.metadata.tables:
    print(f" - {table}")

print("\n数据库初始化完成!") 