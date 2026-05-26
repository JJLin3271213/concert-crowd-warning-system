import requests

API_URL = "https://secure-achievement-production-a328.up.railway.app"

print("=" * 50)
print("添加场馆数据到云端后端")
print("=" * 50)

# 1. 检查现有场馆
print("\n📌 当前场馆列表:")
resp = requests.get(f"{API_URL}/api/venues")
venues = resp.json()
for v in venues:
    print(f"  - ID: {v['id']}, 名称: {v['name']}")

# 2. 添加鸟巢（如果不存在）
birdnest_exists = any(v["name"] == "国家体育场（鸟巢）" for v in venues)
if not birdnest_exists:
    print("\n📌 添加国家体育场（鸟巢）...")
    resp = requests.post(f"{API_URL}/api/venues", params={
        "name": "国家体育场（鸟巢）",
        "address": "北京市朝阳区国家体育场南路1号",
        "total_capacity": 91000
    })
    if resp.status_code == 200:
        print(f"  ✅ 添加成功: {resp.json()}")
    else:
        print(f"  ❌ 添加失败: {resp.status_code}")
else:
    print("\n✅ 鸟巢已存在，跳过添加")

# 3. 添加郑州奥体（如果不存在）
zhengzhou_exists = any(v["name"] == "郑州奥林匹克体育中心" for v in venues)
if not zhengzhou_exists:
    print("\n📌 添加郑州奥林匹克体育中心...")
    resp = requests.post(f"{API_URL}/api/venues", params={
        "name": "郑州奥林匹克体育中心",
        "address": "河南省郑州市中原区丹水大道与长椿路交叉口",
        "total_capacity": 60000
    })
    if resp.status_code == 200:
        print(f"  ✅ 添加成功: {resp.json()}")
    else:
        print(f"  ❌ 添加失败: {resp.status_code}")
else:
    print("\n✅ 郑州奥体已存在，跳过添加")

# 4. 验证最终结果
print("\n📌 最终场馆列表:")
resp = requests.get(f"{API_URL}/api/venues")
venues = resp.json()
for v in venues:
    print(f"  - ID: {v['id']}, 名称: {v['name']}, 容量: {v['total_capacity']}")

print("\n🎉 完成！")