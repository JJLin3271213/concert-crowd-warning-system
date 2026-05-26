import requests

API_URL = "https://secure-achievement-production-a328.up.railway.app"
session = requests.Session()

# 获取鸟巢所有分区
resp = session.get(f"{API_URL}/api/venues/2/zones")
zones = resp.json()

# 记录每个分区名称第一次出现的ID
first_occurrence = {}
to_delete = []

for zone in zones:
    name = zone["name"]
    if name not in first_occurrence:
        first_occurrence[name] = zone["id"]
    else:
        to_delete.append(zone["id"])

print(f"发现 {len(to_delete)} 个重复分区，开始删除...")

for zone_id in to_delete:
    resp = session.delete(f"{API_URL}/api/zones/{zone_id}")
    if resp.status_code == 200:
        print(f"  ✅ 删除分区ID: {zone_id}")
    else:
        print(f"  ❌ 删除失败: {zone_id}")

print("\n清理完成！保留的分区：")
for name, zone_id in first_occurrence.items():
    print(f"  {name}: ID {zone_id}")