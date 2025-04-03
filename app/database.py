from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 从环境变量中获取数据库连接字符串
DATABASE_URL = os.getenv("DATABASE_URL")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建本地会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类，用于 ORM 模型继承
Base = declarative_base()

# 提供数据库会话的生成器
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()