from database import engine, Base
from models import Venue, Zone, RoadNetwork, User, Performance, EmergencyPoint, SystemConfig
from sqlalchemy.orm import Session
from auth import get_password_hash

print("正在创建数据库表...")
Base.metadata.create_all(bind=engine)
print("数据库表创建成功！")

db = Session(engine)

# 创建管理员账号
if db.query(User).count() == 0:
    admin = User(username="admin", hashed_password=get_password_hash("admin123"), is_admin=1)
    db.add(admin)
    print("管理员账号已创建: admin / admin123")

# 添加示例场馆
if db.query(Venue).count() == 0:
    venue = Venue(name="示例场馆", address="上海市浦东新区", total_capacity=10000)
    db.add(venue)
    db.commit()
    
    # 添加分区
    zones = [
        Zone(venue_id=venue.id, name="东看台", capacity=2000, sort_order=1),
        Zone(venue_id=venue.id, name="西看台", capacity=2000, sort_order=2),
        Zone(venue_id=venue.id, name="南看台", capacity=1500, sort_order=3),
        Zone(venue_id=venue.id, name="北看台", capacity=1500, sort_order=4),
        Zone(venue_id=venue.id, name="内场VIP区", capacity=800, sort_order=5),
        Zone(venue_id=venue.id, name="内场普通A区", capacity=1200, sort_order=6),
        Zone(venue_id=venue.id, name="内场普通B区", capacity=1200, sort_order=7),
        Zone(venue_id=venue.id, name="入口", capacity=0, is_exit=0, sort_order=8),
        Zone(venue_id=venue.id, name="出口", capacity=0, is_exit=1, sort_order=9),
    ]
    db.add_all(zones)
    db.commit()
    
    # 获取分区ID映射
    zone_map = {z.name: z.id for z in zones}
    
    # 添加路网连接（包含内场A区 ↔ 内场B区直接连接）
    road_edges = [
        # 入口的连接
        (zone_map["入口"], zone_map["东看台"]),
        (zone_map["入口"], zone_map["西看台"]),
        # 东看台的连接
        (zone_map["东看台"], zone_map["入口"]),
        (zone_map["东看台"], zone_map["北看台"]),
        (zone_map["东看台"], zone_map["内场VIP区"]),
        (zone_map["东看台"], zone_map["内场普通A区"]),
        # 西看台的连接
        (zone_map["西看台"], zone_map["入口"]),
        (zone_map["西看台"], zone_map["北看台"]),
        (zone_map["西看台"], zone_map["内场VIP区"]),
        (zone_map["西看台"], zone_map["内场普通B区"]),
        # 南看台的连接
        (zone_map["南看台"], zone_map["北看台"]),
        (zone_map["南看台"], zone_map["内场VIP区"]),
        (zone_map["南看台"], zone_map["内场普通A区"]),
        (zone_map["南看台"], zone_map["内场普通B区"]),
        # 北看台的连接
        (zone_map["北看台"], zone_map["东看台"]),
        (zone_map["北看台"], zone_map["西看台"]),
        (zone_map["北看台"], zone_map["南看台"]),
        (zone_map["北看台"], zone_map["出口"]),
        # 内场VIP的连接
        (zone_map["内场VIP区"], zone_map["东看台"]),
        (zone_map["内场VIP区"], zone_map["西看台"]),
        (zone_map["内场VIP区"], zone_map["南看台"]),
        (zone_map["内场VIP区"], zone_map["内场普通A区"]),
        (zone_map["内场VIP区"], zone_map["内场普通B区"]),
        # 内场A区的连接
        (zone_map["内场普通A区"], zone_map["东看台"]),
        (zone_map["内场普通A区"], zone_map["南看台"]),
        (zone_map["内场普通A区"], zone_map["内场VIP区"]),
        (zone_map["内场普通A区"], zone_map["内场普通B区"]),  # 新增：A区到B区直接连接
        # 内场B区的连接
        (zone_map["内场普通B区"], zone_map["西看台"]),
        (zone_map["内场普通B区"], zone_map["南看台"]),
        (zone_map["内场普通B区"], zone_map["内场VIP区"]),
        (zone_map["内场普通B区"], zone_map["内场普通A区"]),  # 新增：B区到A区直接连接
        # 出口的连接
        (zone_map["出口"], zone_map["北看台"]),
    ]
    
    for from_id, to_id in road_edges:
        road = RoadNetwork(venue_id=venue.id, from_zone_id=from_id, to_zone_id=to_id, distance=1)
        db.add(road)
    
    db.commit()
    print(f"示例场馆已创建: {venue.name}")
    print(f"分区数量: {len(zones)}")
    print(f"路网边数: {len(road_edges)}")

db.close()
print("初始化完成！")