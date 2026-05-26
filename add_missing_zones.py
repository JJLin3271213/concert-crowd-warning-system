import requests

API_URL = "https://secure-achievement-production-a328.up.railway.app"
session = requests.Session()

# 添加缺失的入口和出口
missing_zones = [
    ("主入口", 0, 0),
    ("出口", 0, 1),
]

print("📌 补充分区...")
for name, cap, is_exit in missing_zones:
    resp = session.post(f"{API_URL}/api/zones", params={
        "venue_id": 3,
        "name": name,
        "capacity": cap,
        "is_exit": is_exit
    })
    if resp.status_code == 200:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}: {resp.status_code}")

print("\n✅ 补充完成！")
