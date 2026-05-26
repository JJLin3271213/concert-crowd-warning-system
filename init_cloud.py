import requests

API_URL = "https://secure-achievement-production-a328.up.railway.app"

# 1. 初始化数据库表
print("初始化数据库表...")
r = requests.get(f"{API_URL}/api/init-db")
print(f"初始化结果: {r.json()}")

# 2. 添加场馆
print("\n添加场馆...")
venues = [
    ("示例场馆", "上海市浦东新区", 10000),
]
for name, addr, cap in venues:
    r = requests.post(f"{API_URL}/api/venues", params={
        "name": name,
        "address": addr,
        "total_capacity": cap
    })
    print(f"添加场馆 {name}: {r.status_code}")

# 3. 获取场馆ID
r = requests.get(f"{API_URL}/api/venues")
venues_data = r.json()
if venues_data:
    venue_id = venues_data[0]["id"]
    print(f"场馆ID: {venue_id}")

    # 4. 添加分区
    print("\n添加分区...")
    zones = [
        ("东看台", 2000, 0),
        ("西看台", 2000, 0),
        ("南看台", 1500, 0),
        ("北看台", 1500, 0),
        ("入口", 0, 0),
        ("出口", 0, 1),
    ]
    for name, cap, is_exit in zones:
        r = requests.post(f"{API_URL}/api/zones", params={
            "venue_id": venue_id,
            "name": name,
            "capacity": cap,
            "is_exit": is_exit
        })
        print(f"添加分区 {name}: {r.status_code}")

print("\n完成！")