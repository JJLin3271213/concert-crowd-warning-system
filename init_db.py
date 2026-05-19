from database import engine, Base
from models import Zone, CrowdData, Alert, User
from sqlalchemy.orm import Session

# 创建所有数据表
print("正在创建数据库表...")
Base.metadata.create_all(bind=engine)
print("数据库表创建成功！")

# 添加测试分区数据
db = Session(engine)

if db.query(Zone).count() == 0:
    print("正在添加测试分区数据...")
    zones = [
        Zone(id=1, name="东看台", capacity=2000, center_lng=116.397128, center_lat=39.916527),
        Zone(id=2, name="西看台", capacity=2000, center_lng=116.396500, center_lat=39.916000),
        Zone(id=3, name="南看台", capacity=1500, center_lng=116.397000, center_lat=39.915500),
        Zone(id=4, name="北看台", capacity=1500, center_lng=116.397500, center_lat=39.917000),
        Zone(id=5, name="内场VIP区", capacity=800, center_lng=116.397300, center_lat=39.916200),
        Zone(id=6, name="内场普通A区", capacity=1200, center_lng=116.397200, center_lat=39.916000),
        Zone(id=7, name="内场普通B区", capacity=1200, center_lng=116.397400, center_lat=39.915800),
    ]
    db.add_all(zones)
    db.commit()
    print(f"已添加 {len(zones)} 个分区")
else:
    print("分区数据已存在，跳过添加")

# 创建管理员账号（简化版，直接插入）
if db.query(User).count() == 0:
    print("正在创建管理员账号...")
    admin = User(
        username="admin",
        hashed_password="admin123",  # 简化版，直接存密码
        is_admin=1
    )
    db.add(admin)
    db.commit()
    print("管理员账号已创建: admin / admin123")
else:
    print("管理员账号已存在，跳过")

db.close()
print("初始化完成！")