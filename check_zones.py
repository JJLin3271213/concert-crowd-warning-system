import requests

API_URL = "https://secure-achievement-production-a328.up.railway.app"

print("=== 鸟巢分区 ===")
resp = requests.get(f"{API_URL}/api/venues/2/zones")
for z in resp.json():
    print(z["id"], z["name"])

print("\n=== 郑州奥体分区 ===")
resp = requests.get(f"{API_URL}/api/venues/3/zones")
for z in resp.json():
    print(z["id"], z["name"])