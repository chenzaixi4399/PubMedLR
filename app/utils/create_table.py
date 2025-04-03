from sqlalchemy import inspect
from sqlalchemy.schema import CreateTable
from app.models import User, Article  # 确保导入所有模型
from app.database import engine, Base

# 检查数据库连接是否正常
try:
    with engine.connect() as connection:
        print("Database connection successful.")
except Exception as e:
    print(f"Database connection failed: {e}")
    exit(1)  # 如果连接失败，退出脚本

# 检查 Base.metadata 中是否包含表
print("\nTables registered in Base.metadata:")
for table_name in Base.metadata.tables.keys():
    print(f"- {table_name}")

# 打印生成的 SQL 语句（用于调试）
print("\nGenerated SQL for table creation:")
print(CreateTable(User.__table__).compile(engine))
print(CreateTable(Article.__table__).compile(engine))

# 检查数据库中现有的表
inspector = inspect(engine)
existing_tables = inspector.get_table_names()
print("\nExisting tables in database:")
if existing_tables:
    for table_name in existing_tables:
        print(f"- {table_name}")
else:
    print("- No tables found.")

# 创建所有表
print("\nAttempting to create tables...")
Base.metadata.create_all(bind=engine)

# 再次检查数据库中的表
new_existing_tables = inspector.get_table_names()
print("\nTables after creation attempt:")
if new_existing_tables:
    for table_name in new_existing_tables:
        print(f"- {table_name}")
else:
    print("- No tables were created.")