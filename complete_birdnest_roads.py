import requests
import time

API_URL = "https://secure-achievement-production-a328.up.railway.app"
session = requests.Session()

def get_zone_map(venue_id):
    """获取分区映射"""
    for attempt in range(3):
        try:
            resp = session.get(f"{API_URL}/api/venues/{venue_id}/zones", timeout=8)
            if resp.status_code == 200:
                zones = resp.json()
                result = {}
                for z in zones:
                    result[z["name"]] = z["id"]
                print(f"  📋 获取到 {len(result)} 个分区")
                return result
        except Exception as e:
            print(f"  ⚠️ 获取分区列表尝试 {attempt+1} 失败: {e}")
        if attempt < 2:
            time.sleep(2)
    return {}

def add_road(venue_id, from_name, to_name, zone_map):
    """添加单条路网"""
    from_id = zone_map.get(from_name)
    to_id = zone_map.get(to_name)
    
    if not from_id or not to_id:
        print(f"  ❌ 找不到分区: {from_name} 或 {to_name}")
        return False
    
    for attempt in range(2):
        try:
            resp = session.post(
                f"{API_URL}/api/road_network",
                params={
                    "venue_id": venue_id,
                    "from_zone_id": from_id,
                    "to_zone_id": to_id,
                    "distance": 1
                },
                timeout=10
            )
            if resp.status_code == 200:
                print(f"  ✅ {from_name} → {to_name}")
                return True
            elif resp.status_code == 400:
                # 可能已存在
                print(f"  ⏭️ {from_name} → {to_name} (可能已存在)")
                return True
        except Exception as e:
            print(f"  ⚠️ {from_name} → {to_name} 超时，尝试 {attempt+1}/2")
        
        if attempt == 0:
            time.sleep(2)
    
    print(f"  ❌ 失败: {from_name} → {to_name}")
    return False

# 所有需要确保存在的路网
# 格式: (起点, 终点)
all_roads = []

# 1. 入口到各看台区（已有，但确保存在）
entrances = ["西南入口", "东南入口", "东北入口", "西北入口"]
for entrance in entrances:
    if entrance == "西南入口":
        zones = ["一层看台A区", "一层看台B区"]
    elif entrance == "东南入口":
        zones = ["一层看台C区", "一层看台D区"]
    elif entrance == "东北入口":
        zones = ["一层看台E区", "一层看台F区"]
    else:  # 西北入口
        zones = ["一层看台G区", "一层看台H区"]
    for zone in zones:
        all_roads.append((entrance, zone))
        all_roads.append((zone, entrance))

# 2. 所有看台区列表
zone_names = [
    "一层看台A区", "一层看台B区", "一层看台C区", "一层看台D区",
    "一层看台E区", "一层看台F区", "一层看台G区", "一层看台H区",
    "一层看台J区", "一层看台K区", "一层看台L区"
]

# 3. 看台之间的环形连接（相邻）
for i in range(len(zone_names) - 1):
    all_roads.append((zone_names[i], zone_names[i+1]))
    all_roads.append((zone_names[i+1], zone_names[i]))

# 4. 看台到二层看台（所有看台）
for zone in zone_names:
    all_roads.append((zone, "二层看台"))
    all_roads.append(("二层看台", zone))

# 5. 二层看台到三层看台
all_roads.append(("二层看台", "三层看台"))
all_roads.append(("三层看台", "二层看台"))

# 6. 看台到内场（指定的几个）
inner_connections = [
    ("一层看台A区", "内场VIP区"),
    ("一层看台C区", "内场VIP区"),
    ("一层看台E区", "内场普通A区"),
    ("一层看台G区", "内场普通B区"),
]
for from_zone, to_zone in inner_connections:
    all_roads.append((from_zone, to_zone))
    all_roads.append((to_zone, from_zone))

# 7. 内场之间连接
inner_zones = ["内场VIP区", "内场普通A区", "内场普通B区"]
for i in range(len(inner_zones) - 1):
    all_roads.append((inner_zones[i], inner_zones[i+1]))
    all_roads.append((inner_zones[i+1], inner_zones[i]))

# 8. 到出口的连接
exit_connections = [
    ("三层看台", "出口"),
    ("内场普通B区", "出口"),
    ("一层看台L区", "出口"),
]
for from_zone, to_zone in exit_connections:
    all_roads.append((from_zone, to_zone))
    all_roads.append((to_zone, from_zone))

print("=" * 60)
print("🏟️ 鸟巢路网完整补全工具")
print("=" * 60)

print("\n📋 获取鸟巢分区...")
zone_map = get_zone_map(2)
if not zone_map:
    print("❌ 无法获取鸟巢分区")
    exit(1)

print(f"\n📌 将检查/添加 {len(all_roads)} 条路网连接...")
print("   (重复的会自动跳过)\n")

success = 0
for i, (from_name, to_name) in enumerate(all_roads):
    print(f"  [{i+1:3d}/{len(all_roads)}] ", end="")
    if add_road(2, from_name, to_name, zone_map):
        success += 1
    # 每10条休息一下
    if (i + 1) % 10 == 0:
        time.sleep(1)

print(f"\n📊 处理完成: {success}/{len(all_roads)}")
print("\n🎉 鸟巢路网补全完成！")
print("\n现在可以测试路线规划了。")