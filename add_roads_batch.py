import requests
import time

API_URL = "https://secure-achievement-production-a328.up.railway.app"
session = requests.Session()

def get_zone_map(venue_id):
    resp = session.get(f"{API_URL}/api/venues/{venue_id}/zones")
    if resp.status_code != 200:
        return {}
    return {z["name"]: z["id"] for z in resp.json()}

def add_roads_batch(venue_id, roads_batch, batch_name):
    zone_map = get_zone_map(venue_id)
    success = 0
    for from_name, to_name in roads_batch:
        from_id = zone_map.get(from_name)
        to_id = zone_map.get(to_name)
        if from_id and to_id:
            resp = session.post(f"{API_URL}/api/road_network", params={
                "venue_id": venue_id,
                "from_zone_id": from_id,
                "to_zone_id": to_id,
                "distance": 1
            })
            if resp.status_code == 200:
                success += 1
                print(f"  ✅ {from_name} → {to_name}")
            else:
                print(f"  ❌ {from_name} → {to_name}: {resp.status_code}")
        else:
            print(f"  ❌ 找不到分区: {from_name} 或 {to_name}")
        time.sleep(0.3)  # 每条请求后休息 0.3 秒
    print(f"📦 批次 {batch_name} 完成: {success}/{len(roads_batch)}")
    return success

# ========== 鸟巢路网（分成4批） ==========
birdnest_roads_batch1 = [
    ("西南入口", "一层看台A区"), ("一层看台A区", "西南入口"),
    ("西南入口", "一层看台B区"), ("一层看台B区", "西南入口"),
    ("东南入口", "一层看台C区"), ("一层看台C区", "东南入口"),
    ("东南入口", "一层看台D区"), ("一层看台D区", "东南入口"),
    ("东北入口", "一层看台E区"), ("一层看台E区", "东北入口"),
    ("东北入口", "一层看台F区"), ("一层看台F区", "东北入口"),
]

birdnest_roads_batch2 = [
    ("西北入口", "一层看台G区"), ("一层看台G区", "西北入口"),
    ("西北入口", "一层看台H区"), ("一层看台H区", "西北入口"),
    ("一层看台A区", "一层看台B区"), ("一层看台B区", "一层看台A区"),
    ("一层看台B区", "一层看台C区"), ("一层看台C区", "一层看台B区"),
    ("一层看台C区", "一层看台D区"), ("一层看台D区", "一层看台C区"),
]

birdnest_roads_batch3 = [
    ("一层看台D区", "一层看台E区"), ("一层看台E区", "一层看台D区"),
    ("一层看台E区", "一层看台F区"), ("一层看台F区", "一层看台E区"),
    ("一层看台F区", "一层看台G区"), ("一层看台G区", "一层看台F区"),
    ("一层看台G区", "一层看台H区"), ("一层看台H区", "一层看台G区"),
    ("一层看台A区", "二层看台"), ("二层看台", "一层看台A区"),
]

birdnest_roads_batch4 = [
    ("一层看台B区", "二层看台"), ("二层看台", "一层看台B区"),
    ("二层看台", "三层看台"), ("三层看台", "二层看台"),
    ("一层看台A区", "内场VIP区"), ("内场VIP区", "一层看台A区"),
    ("一层看台C区", "内场VIP区"), ("内场VIP区", "一层看台C区"),
    ("三层看台", "出口"), ("出口", "三层看台"),
    ("一层看台L区", "出口"), ("出口", "一层看台L区"),
]

print("🏟️ 开始分批添加鸟巢路网...")
add_roads_batch(2, birdnest_roads_batch1, "鸟巢-第1批")
time.sleep(2)
add_roads_batch(2, birdnest_roads_batch2, "鸟巢-第2批")
time.sleep(2)
add_roads_batch(2, birdnest_roads_batch3, "鸟巢-第3批")
time.sleep(2)
add_roads_batch(2, birdnest_roads_batch4, "鸟巢-第4批")

# ========== 郑州奥体路网（分成2批） ==========
zhengzhou_roads_batch1 = [
    ("主入口", "一层看台A区"), ("一层看台A区", "主入口"),
    ("主入口", "一层看台B区"), ("一层看台B区", "主入口"),
    ("主入口", "一层看台C区"), ("一层看台C区", "主入口"),
    ("主入口", "一层看台D区"), ("一层看台D区", "主入口"),
    ("一层看台A区", "一层看台B区"), ("一层看台B区", "一层看台A区"),
    ("一层看台B区", "一层看台C区"), ("一层看台C区", "一层看台B区"),
]

zhengzhou_roads_batch2 = [
    ("一层看台C区", "一层看台D区"), ("一层看台D区", "一层看台C区"),
    ("一层看台A区", "二层看台A区"), ("二层看台A区", "一层看台A区"),
    ("一层看台B区", "二层看台B区"), ("二层看台B区", "一层看台B区"),
    ("二层看台A区", "二层看台B区"), ("二层看台B区", "二层看台A区"),
    ("二层看台A区", "三层看台"), ("三层看台", "二层看台A区"),
    ("三层看台", "出口"), ("出口", "三层看台"),
]

print("\n🏟️ 开始分批添加郑州奥体路网...")
add_roads_batch(3, zhengzhou_roads_batch1, "郑州奥体-第1批")
time.sleep(2)
add_roads_batch(3, zhengzhou_roads_batch2, "郑州奥体-第2批")

print("\n🎉 所有路网添加完成！")