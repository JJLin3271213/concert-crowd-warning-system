import requests

API_URL = "https://secure-achievement-production-a328.up.railway.app"

def get_zone_id(venue_id, zone_name):
    """获取分区ID"""
    resp = requests.get(f"{API_URL}/api/venues/{venue_id}/zones")
    if resp.status_code == 200:
        zones = resp.json()
        for z in zones:
            if z["name"] == zone_name:
                return z["id"]
    return None

def add_zone(venue_id, name, capacity, is_exit=0):
    """添加分区，如果已存在则跳过"""
    if get_zone_id(venue_id, name):
        print(f"  ⏭️ 分区已存在: {name}")
        return
    resp = requests.post(
        f"{API_URL}/api/zones",
        params={"venue_id": venue_id, "name": name, "capacity": capacity, "is_exit": is_exit}
    )
    if resp.status_code == 200:
        print(f"  ✅ 添加分区: {name} ({capacity}人)")
    else:
        print(f"  ❌ 添加失败: {name}")

def add_road(venue_id, from_name, to_name, distance=1):
    """添加路网连接"""
    from_id = get_zone_id(venue_id, from_name)
    to_id = get_zone_id(venue_id, to_name)
    if from_id and to_id:
        resp = requests.post(
            f"{API_URL}/api/road_network",
            params={"venue_id": venue_id, "from_zone_id": from_id, "to_zone_id": to_id, "distance": distance}
        )
        if resp.status_code == 200:
            print(f"  ✅ 连接: {from_name} → {to_name}")
        else:
            print(f"  ❌ 连接失败: {from_name} → {to_name}")
    else:
        print(f"  ❌ 找不到分区: {from_name} 或 {to_name}")

# ========== 1. 确保鸟巢场馆存在 ==========
print("检查鸟巢场馆...")
resp = requests.get(f"{API_URL}/api/venues")
venues = resp.json()
birdnest_id = None
for v in venues:
    if v["name"] == "国家体育场（鸟巢）":
        birdnest_id = v["id"]
        print(f"✅ 鸟巢场馆ID: {birdnest_id}")
        break
if not birdnest_id:
    print("❌ 鸟巢场馆不存在，请先运行 add_venues_direct.py")
    exit(1)

# ========== 2. 添加缺失的入口和出口分区 ==========
print("\n📌 添加鸟巢入口/出口分区...")
add_zone(birdnest_id, "西南入口", 0, is_exit=0)
add_zone(birdnest_id, "东南入口", 0, is_exit=0)
add_zone(birdnest_id, "东北入口", 0, is_exit=0)
add_zone(birdnest_id, "西北入口", 0, is_exit=0)
add_zone(birdnest_id, "出口", 0, is_exit=1)

# ========== 3. 添加所有看台和内场分区（如果尚未添加） ==========
print("\n📌 添加鸟巢看台/内场分区...")
zones = [
    ("一层看台A区", 5000), ("一层看台B区", 5000), ("一层看台C区", 6000),
    ("一层看台D区", 6000), ("一层看台E区", 6000), ("一层看台F区", 5000),
    ("一层看台G区", 5000), ("一层看台H区", 5000), ("一层看台J区", 5000),
    ("一层看台K区", 5000), ("一层看台L区", 5000), ("二层看台", 15000),
    ("三层看台", 12000), ("内场VIP区", 3000), ("内场普通A区", 2000),
    ("内场普通B区", 2000),
]
for name, cap in zones:
    add_zone(birdnest_id, name, cap)

# ========== 4. 添加路网连接 ==========
print("\n🔗 添加鸟巢路网...")

# 入口到看台
add_road(birdnest_id, "西南入口", "一层看台A区")
add_road(birdnest_id, "西南入口", "一层看台B区")
add_road(birdnest_id, "东南入口", "一层看台C区")
add_road(birdnest_id, "东南入口", "一层看台D区")
add_road(birdnest_id, "东北入口", "一层看台E区")
add_road(birdnest_id, "东北入口", "一层看台F区")
add_road(birdnest_id, "西北入口", "一层看台G区")
add_road(birdnest_id, "西北入口", "一层看台H区")

# 看台之间环形连接
adjacent = [
    ("一层看台A区", "一层看台B区"), ("一层看台B区", "一层看台C区"),
    ("一层看台C区", "一层看台D区"), ("一层看台D区", "一层看台E区"),
    ("一层看台E区", "一层看台F区"), ("一层看台F区", "一层看台G区"),
    ("一层看台G区", "一层看台H区"), ("一层看台H区", "一层看台J区"),
    ("一层看台J区", "一层看台K区"), ("一层看台K区", "一层看台L区"),
]
for f, t in adjacent:
    add_road(birdnest_id, f, t)
    add_road(birdnest_id, t, f)  # 双向

# 看台到二层、三层
add_road(birdnest_id, "一层看台A区", "二层看台")
add_road(birdnest_id, "一层看台B区", "二层看台")
add_road(birdnest_id, "二层看台", "三层看台")

# 看台到内场
add_road(birdnest_id, "一层看台A区", "内场VIP区")
add_road(birdnest_id, "一层看台C区", "内场VIP区")
add_road(birdnest_id, "一层看台E区", "内场普通A区")
add_road(birdnest_id, "一层看台G区", "内场普通B区")

# 内场之间
add_road(birdnest_id, "内场VIP区", "内场普通A区")
add_road(birdnest_id, "内场普通A区", "内场普通B区")

# 到出口
add_road(birdnest_id, "三层看台", "出口")
add_road(birdnest_id, "内场普通B区", "出口")
add_road(birdnest_id, "一层看台L区", "出口")

print("\n🎉 鸟巢初始化完成！")