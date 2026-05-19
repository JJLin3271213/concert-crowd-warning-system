from database import SessionLocal
from models import Venue, Zone, RoadNetwork
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db = SessionLocal()

# ========== 1. 北京鸟巢体育场（真实分区） ==========
print("正在添加：北京鸟巢体育场（真实分区）...")

venue_birdnest = Venue(
    name="国家体育场（鸟巢）",
    address="北京市朝阳区国家体育场南路1号",
    total_capacity=91000
)
db.add(venue_birdnest)
db.commit()

# 鸟巢看台区（12个字母区，每区约5000-8000人）
zones_birdnest = [
    # 看台区
    Zone(venue_id=venue_birdnest.id, name="A区看台", capacity=7000, sort_order=1),
    Zone(venue_id=venue_birdnest.id, name="B区看台", capacity=7000, sort_order=2),
    Zone(venue_id=venue_birdnest.id, name="C区看台", capacity=7000, sort_order=3),
    Zone(venue_id=venue_birdnest.id, name="D区看台", capacity=7000, sort_order=4),
    Zone(venue_id=venue_birdnest.id, name="E区看台", capacity=7000, sort_order=5),
    Zone(venue_id=venue_birdnest.id, name="F区看台", capacity=7000, sort_order=6),
    Zone(venue_id=venue_birdnest.id, name="G区看台", capacity=7000, sort_order=7),
    Zone(venue_id=venue_birdnest.id, name="H区看台", capacity=7000, sort_order=8),
    Zone(venue_id=venue_birdnest.id, name="J区看台", capacity=7000, sort_order=9),
    Zone(venue_id=venue_birdnest.id, name="K区看台", capacity=5000, sort_order=10),
    Zone(venue_id=venue_birdnest.id, name="L区看台", capacity=5000, sort_order=11),
    Zone(venue_id=venue_birdnest.id, name="M区看台", capacity=5000, sort_order=12),
    # 内场区
    Zone(venue_id=venue_birdnest.id, name="内场A区", capacity=4000, sort_order=13),
    Zone(venue_id=venue_birdnest.id, name="内场B区", capacity=4000, sort_order=14),
    Zone(venue_id=venue_birdnest.id, name="内场C区", capacity=3000, sort_order=15),
    Zone(venue_id=venue_birdnest.id, name="内场D区", capacity=3000, sort_order=16),
    # 出入口
    Zone(venue_id=venue_birdnest.id, name="西南入口", capacity=0, is_exit=0, sort_order=17),
    Zone(venue_id=venue_birdnest.id, name="东南入口", capacity=0, is_exit=0, sort_order=18),
    Zone(venue_id=venue_birdnest.id, name="东北入口", capacity=0, is_exit=0, sort_order=19),
    Zone(venue_id=venue_birdnest.id, name="西北入口", capacity=0, is_exit=0, sort_order=20),
    Zone(venue_id=venue_birdnest.id, name="出口", capacity=0, is_exit=1, sort_order=21),
]
db.add_all(zones_birdnest)
db.commit()

# 获取分区ID映射
zone_map_birdnest = {z.name: z.id for z in zones_birdnest}

# 更完整的鸟巢路网连接
roads_birdnest = [
    # 入口到各看台区
    (zone_map_birdnest["西南入口"], zone_map_birdnest["A区看台"]),
    (zone_map_birdnest["西南入口"], zone_map_birdnest["B区看台"]),
    (zone_map_birdnest["西南入口"], zone_map_birdnest["C区看台"]),
    (zone_map_birdnest["东南入口"], zone_map_birdnest["D区看台"]),
    (zone_map_birdnest["东南入口"], zone_map_birdnest["E区看台"]),
    (zone_map_birdnest["东北入口"], zone_map_birdnest["F区看台"]),
    (zone_map_birdnest["东北入口"], zone_map_birdnest["G区看台"]),
    (zone_map_birdnest["西北入口"], zone_map_birdnest["H区看台"]),
    (zone_map_birdnest["西北入口"], zone_map_birdnest["J区看台"]),
    # 看台区间双向连接（环形）
    (zone_map_birdnest["A区看台"], zone_map_birdnest["B区看台"]),
    (zone_map_birdnest["B区看台"], zone_map_birdnest["C区看台"]),
    (zone_map_birdnest["C区看台"], zone_map_birdnest["D区看台"]),
    (zone_map_birdnest["D区看台"], zone_map_birdnest["E区看台"]),
    (zone_map_birdnest["E区看台"], zone_map_birdnest["F区看台"]),
    (zone_map_birdnest["F区看台"], zone_map_birdnest["G区看台"]),
    (zone_map_birdnest["G区看台"], zone_map_birdnest["H区看台"]),
    (zone_map_birdnest["H区看台"], zone_map_birdnest["J区看台"]),
    (zone_map_birdnest["J区看台"], zone_map_birdnest["K区看台"]),
    (zone_map_birdnest["K区看台"], zone_map_birdnest["L区看台"]),
    (zone_map_birdnest["L区看台"], zone_map_birdnest["M区看台"]),
    # 反向连接
    (zone_map_birdnest["B区看台"], zone_map_birdnest["A区看台"]),
    (zone_map_birdnest["C区看台"], zone_map_birdnest["B区看台"]),
    (zone_map_birdnest["D区看台"], zone_map_birdnest["C区看台"]),
    (zone_map_birdnest["E区看台"], zone_map_birdnest["D区看台"]),
    (zone_map_birdnest["F区看台"], zone_map_birdnest["E区看台"]),
    (zone_map_birdnest["G区看台"], zone_map_birdnest["F区看台"]),
    (zone_map_birdnest["H区看台"], zone_map_birdnest["G区看台"]),
    (zone_map_birdnest["J区看台"], zone_map_birdnest["H区看台"]),
    (zone_map_birdnest["K区看台"], zone_map_birdnest["J区看台"]),
    (zone_map_birdnest["L区看台"], zone_map_birdnest["K区看台"]),
    (zone_map_birdnest["M区看台"], zone_map_birdnest["L区看台"]),
    # 看台到内场连接
    (zone_map_birdnest["A区看台"], zone_map_birdnest["内场A区"]),
    (zone_map_birdnest["C区看台"], zone_map_birdnest["内场B区"]),
    (zone_map_birdnest["E区看台"], zone_map_birdnest["内场C区"]),
    (zone_map_birdnest["G区看台"], zone_map_birdnest["内场D区"]),
    (zone_map_birdnest["内场A区"], zone_map_birdnest["A区看台"]),
    (zone_map_birdnest["内场B区"], zone_map_birdnest["C区看台"]),
    (zone_map_birdnest["内场C区"], zone_map_birdnest["E区看台"]),
    (zone_map_birdnest["内场D区"], zone_map_birdnest["G区看台"]),
    # 内场区间连接
    (zone_map_birdnest["内场A区"], zone_map_birdnest["内场B区"]),
    (zone_map_birdnest["内场B区"], zone_map_birdnest["内场C区"]),
    (zone_map_birdnest["内场C区"], zone_map_birdnest["内场D区"]),
    (zone_map_birdnest["内场B区"], zone_map_birdnest["内场A区"]),
    (zone_map_birdnest["内场C区"], zone_map_birdnest["内场B区"]),
    (zone_map_birdnest["内场D区"], zone_map_birdnest["内场C区"]),
    # 到出口
    (zone_map_birdnest["M区看台"], zone_map_birdnest["出口"]),
    (zone_map_birdnest["内场D区"], zone_map_birdnest["出口"]),
    (zone_map_birdnest["西南入口"], zone_map_birdnest["出口"]),
]
for from_id, to_id in roads_birdnest:
    road = RoadNetwork(venue_id=venue_birdnest.id, from_zone_id=from_id, to_zone_id=to_id, distance=1)
    db.add(road)
db.commit()

print(f"  ✅ 北京鸟巢：{len(zones_birdnest)} 个分区，{len(roads_birdnest)} 条路网")

# ========== 2. 郑州奥体中心（真实分区） ==========
print("正在添加：郑州奥林匹克体育中心（真实分区）...")

venue_zhengzhou = Venue(
    name="郑州奥林匹克体育中心",
    address="河南省郑州市中原区丹水大道与长椿路交叉口",
    total_capacity=60000
)
db.add(venue_zhengzhou)
db.commit()

zones_zhengzhou = [
    # 看台区
    Zone(venue_id=venue_zhengzhou.id, name="一层看台东区", capacity=8000, sort_order=1),
    Zone(venue_id=venue_zhengzhou.id, name="一层看台西区", capacity=8000, sort_order=2),
    Zone(venue_id=venue_zhengzhou.id, name="一层看台南区", capacity=6000, sort_order=3),
    Zone(venue_id=venue_zhengzhou.id, name="一层看台北区", capacity=6000, sort_order=4),
    Zone(venue_id=venue_zhengzhou.id, name="二层看台", capacity=15000, sort_order=5),
    Zone(venue_id=venue_zhengzhou.id, name="三层看台", capacity=17000, sort_order=6),
    # 内场区
    Zone(venue_id=venue_zhengzhou.id, name="内场A区", capacity=4000, sort_order=7),
    Zone(venue_id=venue_zhengzhou.id, name="内场B区", capacity=4000, sort_order=8),
    Zone(venue_id=venue_zhengzhou.id, name="内场C区", capacity=4000, sort_order=9),
    # 出入口
    Zone(venue_id=venue_zhengzhou.id, name="主入口", capacity=0, is_exit=0, sort_order=10),
    Zone(venue_id=venue_zhengzhou.id, name="出口", capacity=0, is_exit=1, sort_order=11),
]
db.add_all(zones_zhengzhou)
db.commit()

zone_map_zhengzhou = {z.name: z.id for z in zones_zhengzhou}

# 郑州奥体中心完整路网（双向）
roads_zhengzhou = [
    # 主入口到各看台区
    (zone_map_zhengzhou["主入口"], zone_map_zhengzhou["一层看台东区"]),
    (zone_map_zhengzhou["主入口"], zone_map_zhengzhou["一层看台西区"]),
    (zone_map_zhengzhou["主入口"], zone_map_zhengzhou["一层看台南区"]),
    (zone_map_zhengzhou["主入口"], zone_map_zhengzhou["一层看台北区"]),
    # 反向
    (zone_map_zhengzhou["一层看台东区"], zone_map_zhengzhou["主入口"]),
    (zone_map_zhengzhou["一层看台西区"], zone_map_zhengzhou["主入口"]),
    (zone_map_zhengzhou["一层看台南区"], zone_map_zhengzhou["主入口"]),
    (zone_map_zhengzhou["一层看台北区"], zone_map_zhengzhou["主入口"]),
    # 一层看台区间连接（环形）
    (zone_map_zhengzhou["一层看台东区"], zone_map_zhengzhou["一层看台南区"]),
    (zone_map_zhengzhou["一层看台南区"], zone_map_zhengzhou["一层看台西区"]),
    (zone_map_zhengzhou["一层看台西区"], zone_map_zhengzhou["一层看台北区"]),
    (zone_map_zhengzhou["一层看台北区"], zone_map_zhengzhou["一层看台东区"]),
    # 反向
    (zone_map_zhengzhou["一层看台南区"], zone_map_zhengzhou["一层看台东区"]),
    (zone_map_zhengzhou["一层看台西区"], zone_map_zhengzhou["一层看台南区"]),
    (zone_map_zhengzhou["一层看台北区"], zone_map_zhengzhou["一层看台西区"]),
    (zone_map_zhengzhou["一层看台东区"], zone_map_zhengzhou["一层看台北区"]),
    # 一层到二层看台
    (zone_map_zhengzhou["一层看台东区"], zone_map_zhengzhou["二层看台"]),
    (zone_map_zhengzhou["一层看台西区"], zone_map_zhengzhou["二层看台"]),
    (zone_map_zhengzhou["二层看台"], zone_map_zhengzhou["一层看台东区"]),
    (zone_map_zhengzhou["二层看台"], zone_map_zhengzhou["一层看台西区"]),
    # 二层到三层看台
    (zone_map_zhengzhou["二层看台"], zone_map_zhengzhou["三层看台"]),
    (zone_map_zhengzhou["三层看台"], zone_map_zhengzhou["二层看台"]),
    # 看台到内场连接
    (zone_map_zhengzhou["一层看台东区"], zone_map_zhengzhou["内场A区"]),
    (zone_map_zhengzhou["一层看台西区"], zone_map_zhengzhou["内场B区"]),
    (zone_map_zhengzhou["一层看台南区"], zone_map_zhengzhou["内场C区"]),
    (zone_map_zhengzhou["内场A区"], zone_map_zhengzhou["一层看台东区"]),
    (zone_map_zhengzhou["内场B区"], zone_map_zhengzhou["一层看台西区"]),
    (zone_map_zhengzhou["内场C区"], zone_map_zhengzhou["一层看台南区"]),
    # 内场区间连接
    (zone_map_zhengzhou["内场A区"], zone_map_zhengzhou["内场B区"]),
    (zone_map_zhengzhou["内场B区"], zone_map_zhengzhou["内场C区"]),
    (zone_map_zhengzhou["内场B区"], zone_map_zhengzhou["内场A区"]),
    (zone_map_zhengzhou["内场C区"], zone_map_zhengzhou["内场B区"]),
    # 到出口
    (zone_map_zhengzhou["三层看台"], zone_map_zhengzhou["出口"]),
    (zone_map_zhengzhou["内场C区"], zone_map_zhengzhou["出口"]),
    (zone_map_zhengzhou["出口"], zone_map_zhengzhou["三层看台"]),
    (zone_map_zhengzhou["出口"], zone_map_zhengzhou["内场C区"]),
]

for from_id, to_id in roads_zhengzhou:
    road = RoadNetwork(venue_id=venue_zhengzhou.id, from_zone_id=from_id, to_zone_id=to_id, distance=1)
    db.add(road)
db.commit()

print(f"  ✅ 郑州奥体：{len(zones_zhengzhou)} 个分区，{len(roads_zhengzhou)} 条路网")

db.close()
print("\n🎉 所有真实场馆添加完成！")
print("\n场馆列表：")
print("  1. 国家体育场（鸟巢）- 北京（16个分区+5个出入口）")
print("  2. 郑州奥林匹克体育中心 - 郑州（11个分区）")
print("  3. 示例场馆（原有）")