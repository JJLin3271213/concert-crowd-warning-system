import requests
import time
import json
import os

API_URL = "https://secure-achievement-production-a328.up.railway.app"
session = requests.Session()
session.timeout = 10

# 进度文件
PROGRESS_FILE = "roads_progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_progress(completed):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(list(completed), f)

def get_zone_map(venue_id):
    """获取分区映射（带重试）"""
    for attempt in range(3):
        try:
            resp = session.get(f"{API_URL}/api/venues/{venue_id}/zones", timeout=8)
            if resp.status_code == 200:
                return {z["name"]: z["id"] for z in resp.json()}
        except Exception as e:
            print(f"  ⚠️ 获取分区列表尝试 {attempt+1} 失败: {e}")
        if attempt < 2:
            time.sleep(2)
    return {}

def get_existing_roads(venue_id):
    """获取已存在的路网连接"""
    try:
        resp = session.get(f"{API_URL}/api/venues/{venue_id}/road_network", timeout=8)
        if resp.status_code == 200:
            return {(r["from_zone_id"], r["to_zone_id"]) for r in resp.json()}
    except Exception as e:
        print(f"  ⚠️ 获取路网失败: {e}")
    return set()

def add_road(venue_id, from_name, to_name, zone_map, existing_roads):
    """添加单条路网（带重试和去重）"""
    from_id = zone_map.get(from_name)
    to_id = zone_map.get(to_name)
    
    if not from_id or not to_id:
        print(f"  ❌ 找不到分区: {from_name} 或 {to_name}")
        return False
    
    # 检查是否已存在
    if (from_id, to_id) in existing_roads:
        print(f"  ⏭️ 已存在: {from_name} → {to_name}")
        return True
    
    for attempt in range(3):
        try:
            resp = session.post(
                f"{API_URL}/api/road_network",
                params={
                    "venue_id": venue_id,
                    "from_zone_id": from_id,
                    "to_zone_id": to_id,
                    "distance": 1
                },
                timeout=8
            )
            if resp.status_code == 200:
                print(f"  ✅ {from_name} → {to_name}")
                return True
            else:
                print(f"  ⚠️ 尝试 {attempt+1}: {from_name} → {to_name} 状态码 {resp.status_code}")
        except Exception as e:
            print(f"  ⚠️ 尝试 {attempt+1}: {from_name} → {to_name} 超时")
        
        if attempt < 2:
            time.sleep(2)
    
    print(f"  ❌ 失败: {from_name} → {to_name}")
    return False

def add_roads_batch(venue_id, roads, batch_name):
    """批量添加路网"""
    print(f"\n📦 批次: {batch_name} ({len(roads)} 条)")
    
    # 获取分区映射和已存在路网
    zone_map = get_zone_map(venue_id)
    if not zone_map:
        print(f"  ❌ 无法获取分区映射")
        return 0
    
    existing_roads = get_existing_roads(venue_id)
    
    success = 0
    for i, (from_name, to_name) in enumerate(roads):
        print(f"  [{i+1}/{len(roads)}] ", end="")
        if add_road(venue_id, from_name, to_name, zone_map, existing_roads):
            success += 1
        if i < len(roads) - 1:
            time.sleep(1)  # 请求间隔
    
    print(f"  📊 完成: {success}/{len(roads)}")
    return success

# ========== 鸟巢剩余路网 ==========
birdnest_remaining = [
    ("西北入口", "一层看台G区"), ("一层看台G区", "西北入口"),
    ("西北入口", "一层看台H区"), ("一层看台H区", "西北入口"),
    ("一层看台A区", "二层看台"), ("二层看台", "一层看台A区"),
    ("一层看台B区", "二层看台"), ("二层看台", "一层看台B区"),
    ("二层看台", "三层看台"), ("三层看台", "二层看台"),
    ("一层看台A区", "内场VIP区"), ("内场VIP区", "一层看台A区"),
    ("一层看台C区", "内场VIP区"), ("内场VIP区", "一层看台C区"),
    ("一层看台E区", "内场普通A区"), ("内场普通A区", "一层看台E区"),
    ("一层看台G区", "内场普通B区"), ("内场普通B区", "一层看台G区"),
    ("内场VIP区", "内场普通A区"), ("内场普通A区", "内场VIP区"),
    ("内场普通A区", "内场普通B区"), ("内场普通B区", "内场普通A区"),
    ("三层看台", "出口"), ("出口", "三层看台"),
    ("内场普通B区", "出口"), ("出口", "内场普通B区"),
    ("一层看台L区", "出口"), ("出口", "一层看台L区"),
]

# ========== 郑州奥体全部路网 ==========
zhengzhou_all = [
    ("主入口", "一层看台A区"), ("一层看台A区", "主入口"),
    ("主入口", "一层看台B区"), ("一层看台B区", "主入口"),
    ("主入口", "一层看台C区"), ("一层看台C区", "主入口"),
    ("主入口", "一层看台D区"), ("一层看台D区", "主入口"),
    ("一层看台A区", "一层看台B区"), ("一层看台B区", "一层看台A区"),
    ("一层看台B区", "一层看台C区"), ("一层看台C区", "一层看台B区"),
    ("一层看台C区", "一层看台D区"), ("一层看台D区", "一层看台C区"),
    ("一层看台A区", "二层看台A区"), ("二层看台A区", "一层看台A区"),
    ("一层看台B区", "二层看台B区"), ("二层看台B区", "一层看台B区"),
    ("一层看台C区", "二层看台C区"), ("二层看台C区", "一层看台C区"),
    ("一层看台D区", "二层看台D区"), ("二层看台D区", "一层看台D区"),
    ("二层看台A区", "二层看台B区"), ("二层看台B区", "二层看台A区"),
    ("二层看台B区", "二层看台C区"), ("二层看台C区", "二层看台B区"),
    ("二层看台C区", "二层看台D区"), ("二层看台D区", "二层看台C区"),
    ("二层看台A区", "三层看台"), ("三层看台", "二层看台A区"),
    ("二层看台B区", "三层看台"), ("三层看台", "二层看台B区"),
    ("一层看台A区", "内场VIP区"), ("内场VIP区", "一层看台A区"),
    ("一层看台B区", "内场A区"), ("内场A区", "一层看台B区"),
    ("一层看台C区", "内场B区"), ("内场B区", "一层看台C区"),
    ("一层看台D区", "内场C区"), ("内场C区", "一层看台D区"),
    ("内场VIP区", "内场A区"), ("内场A区", "内场VIP区"),
    ("内场A区", "内场B区"), ("内场B区", "内场A区"),
    ("内场B区", "内场C区"), ("内场C区", "内场B区"),
    ("三层看台", "出口"), ("出口", "三层看台"),
    ("内场C区", "出口"), ("出口", "内场C区"),
    ("包厢区", "出口"), ("出口", "包厢区"),
]

print("=" * 60)
print("稳健版路网添加工具")
print("=" * 60)

# 添加鸟巢剩余路网
print("\n🏟️ 添加鸟巢剩余路网...")
add_roads_batch(2, birdnest_remaining, "鸟巢-剩余")

print("\n⏸️ 休息 5 秒...")
time.sleep(5)

# 添加郑州奥体路网
print("\n🏟️ 添加郑州奥体路网...")
# 分批处理，每批 20 条
batch_size = 20
for i in range(0, len(zhengzhou_all), batch_size):
    batch = zhengzhou_all[i:i+batch_size]
    add_roads_batch(3, batch, f"郑州奥体-第{i//batch_size + 1}批")
    if i + batch_size < len(zhengzhou_all):
        print("  ⏸️ 休息 3 秒...")
        time.sleep(3)

print("\n" + "=" * 60)
print("🎉 所有路网添加完成！")
print("=" * 60)