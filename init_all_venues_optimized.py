import requests
import time

API_URL = "https://secure-achievement-production-a328.up.railway.app"

# 创建 Session 对象，复用连接
session = requests.Session()

# ---------- 鸟巢数据 ----------
birdnest_data = {
    "name": "国家体育场（鸟巢）",
    "address": "北京市朝阳区国家体育场南路1号",
    "total_capacity": 91000,
    "zones": [
        {"name": "西南入口", "capacity": 0, "is_exit": 0},
        {"name": "东南入口", "capacity": 0, "is_exit": 0},
        {"name": "东北入口", "capacity": 0, "is_exit": 0},
        {"name": "西北入口", "capacity": 0, "is_exit": 0},
        {"name": "出口", "capacity": 0, "is_exit": 1},
        {"name": "一层看台A区", "capacity": 5000},
        {"name": "一层看台B区", "capacity": 5000},
        {"name": "一层看台C区", "capacity": 6000},
        {"name": "一层看台D区", "capacity": 6000},
        {"name": "一层看台E区", "capacity": 6000},
        {"name": "一层看台F区", "capacity": 5000},
        {"name": "一层看台G区", "capacity": 5000},
        {"name": "一层看台H区", "capacity": 5000},
        {"name": "一层看台J区", "capacity": 5000},
        {"name": "一层看台K区", "capacity": 5000},
        {"name": "一层看台L区", "capacity": 5000},
        {"name": "二层看台", "capacity": 15000},
        {"name": "三层看台", "capacity": 12000},
        {"name": "内场VIP区", "capacity": 3000},
        {"name": "内场普通A区", "capacity": 2000},
        {"name": "内场普通B区", "capacity": 2000},
    ],
    "roads": [
        ("西南入口", "一层看台A区"), ("西南入口", "一层看台B区"),
        ("东南入口", "一层看台C区"), ("东南入口", "一层看台D区"),
        ("东北入口", "一层看台E区"), ("东北入口", "一层看台F区"),
        ("西北入口", "一层看台G区"), ("西北入口", "一层看台H区"),
        ("一层看台A区", "一层看台B区"), ("一层看台B区", "一层看台A区"),
        ("一层看台B区", "一层看台C区"), ("一层看台C区", "一层看台B区"),
        ("一层看台C区", "一层看台D区"), ("一层看台D区", "一层看台C区"),
        ("一层看台D区", "一层看台E区"), ("一层看台E区", "一层看台D区"),
        ("一层看台E区", "一层看台F区"), ("一层看台F区", "一层看台E区"),
        ("一层看台F区", "一层看台G区"), ("一层看台G区", "一层看台F区"),
        ("一层看台G区", "一层看台H区"), ("一层看台H区", "一层看台G区"),
        ("一层看台H区", "一层看台J区"), ("一层看台J区", "一层看台H区"),
        ("一层看台J区", "一层看台K区"), ("一层看台K区", "一层看台J区"),
        ("一层看台K区", "一层看台L区"), ("一层看台L区", "一层看台K区"),
        ("一层看台A区", "二层看台"), ("一层看台B区", "二层看台"),
        ("二层看台", "三层看台"), ("三层看台", "二层看台"),
        ("一层看台A区", "内场VIP区"), ("一层看台C区", "内场VIP区"),
        ("一层看台E区", "内场普通A区"), ("一层看台G区", "内场普通B区"),
        ("内场VIP区", "内场普通A区"), ("内场普通A区", "内场VIP区"),
        ("内场普通A区", "内场普通B区"), ("内场普通B区", "内场普通A区"),
        ("三层看台", "出口"), ("内场普通B区", "出口"), ("一层看台L区", "出口"),
    ]
}

# ---------- 郑州奥体数据 ----------
zhengzhou_data = {
    "name": "郑州奥林匹克体育中心",
    "address": "河南省郑州市中原区丹水大道与长椿路交叉口",
    "total_capacity": 60000,
    "zones": [
        {"name": "主入口", "capacity": 0, "is_exit": 0},
        {"name": "出口", "capacity": 0, "is_exit": 1},
        {"name": "一层看台A区", "capacity": 4000},
        {"name": "一层看台B区", "capacity": 4000},
        {"name": "一层看台C区", "capacity": 3500},
        {"name": "一层看台D区", "capacity": 3500},
        {"name": "二层看台A区", "capacity": 5000},
        {"name": "二层看台B区", "capacity": 5000},
        {"name": "二层看台C区", "capacity": 4000},
        {"name": "二层看台D区", "capacity": 4000},
        {"name": "三层看台", "capacity": 12000},
        {"name": "内场VIP区", "capacity": 2000},
        {"name": "内场A区", "capacity": 3000},
        {"name": "内场B区", "capacity": 3000},
        {"name": "内场C区", "capacity": 4000},
        {"name": "包厢区", "capacity": 1500},
    ],
    "roads": [
        ("主入口", "一层看台A区"), ("主入口", "一层看台B区"),
        ("主入口", "一层看台C区"), ("主入口", "一层看台D区"),
        ("一层看台A区", "一层看台B区"), ("一层看台B区", "一层看台A区"),
        ("一层看台B区", "一层看台C区"), ("一层看台C区", "一层看台B区"),
        ("一层看台C区", "一层看台D区"), ("一层看台D区", "一层看台C区"),
        ("一层看台A区", "二层看台A区"), ("一层看台B区", "二层看台B区"),
        ("一层看台C区", "二层看台C区"), ("一层看台D区", "二层看台D区"),
        ("二层看台A区", "二层看台B区"), ("二层看台B区", "二层看台A区"),
        ("二层看台B区", "二层看台C区"), ("二层看台C区", "二层看台B区"),
        ("二层看台C区", "二层看台D区"), ("二层看台D区", "二层看台C区"),
        ("二层看台A区", "三层看台"), ("二层看台B区", "三层看台"),
        ("三层看台", "二层看台A区"), ("三层看台", "二层看台B区"),
        ("一层看台A区", "内场VIP区"), ("一层看台B区", "内场A区"),
        ("一层看台C区", "内场B区"), ("一层看台D区", "内场C区"),
        ("内场VIP区", "内场A区"), ("内场A区", "内场VIP区"),
        ("内场A区", "内场B区"), ("内场B区", "内场A区"),
        ("内场B区", "内场C区"), ("内场C区", "内场B区"),
        ("三层看台", "出口"), ("内场C区", "出口"), ("包厢区", "出口"),
    ]
}

def get_zone_map(venue_id):
    """获取场馆所有分区名称到ID的映射"""
    resp = session.get(f"{API_URL}/api/venues/{venue_id}/zones")
    if resp.status_code != 200:
        return {}
    return {z["name"]: z["id"] for z in resp.json()}

def add_venue(data):
    """批量添加场馆、分区、路网"""
    start = time.time()
    print(f"\n{'='*50}")
    print(f"🏟️ 初始化: {data['name']}")
    print(f"{'='*50}")
    
    # 1. 检查或创建场馆
    resp = session.get(f"{API_URL}/api/venues")
    venues = resp.json()
    venue_id = None
    for v in venues:
        if v["name"] == data["name"]:
            venue_id = v["id"]
            print(f"✅ 场馆已存在，ID: {venue_id}")
            break
    
    if not venue_id:
        print(f"📌 创建场馆...")
        resp = session.post(f"{API_URL}/api/venues", params={
            "name": data["name"],
            "address": data["address"],
            "total_capacity": data["total_capacity"]
        })
        if resp.status_code == 200:
            venue_id = resp.json()["id"]
            print(f"✅ 场馆创建成功，ID: {venue_id}")
        else:
            print(f"❌ 创建失败: {resp.status_code}")
            return
    
    # 2. 批量添加分区（使用 Session 复用连接）
    print(f"📌 添加 {len(data['zones'])} 个分区...")
    for zone in data["zones"]:
        resp = session.post(f"{API_URL}/api/zones", params={
            "venue_id": venue_id,
            "name": zone["name"],
            "capacity": zone["capacity"],
            "is_exit": zone.get("is_exit", 0)
        })
        if resp.status_code == 200:
            print(f"  ✅ {zone['name']}")
        else:
            print(f"  ❌ {zone['name']}: {resp.status_code}")
    
    # 3. 获取分区ID映射
    zone_map = get_zone_map(venue_id)
    
    # 4. 批量添加路网
    print(f"📌 添加 {len(data['roads'])} 条路网...")
    success_count = 0
    for from_name, to_name in data["roads"]:
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
                success_count += 1
    
    print(f"✅ 路网添加完成: {success_count}/{len(data['roads'])}")
    print(f"⏱️ 耗时: {time.time() - start:.1f} 秒")

# 运行
if __name__ == "__main__":
    print("=" * 50)
    print("开始初始化场馆数据（优化版）")
    print("=" * 50)
    
    add_venue(birdnest_data)
    add_venue(zhengzhou_data)
    
    print("\n🎉 所有场馆初始化完成！")