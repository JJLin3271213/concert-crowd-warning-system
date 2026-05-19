import requests
import random
import time
import datetime

API_URL = "http://localhost:8000"

def get_all_zones():
    """获取所有场馆的所有分区"""
    try:
        # 获取所有场馆
        venues_response = requests.get(f"{API_URL}/api/venues")
        venues = venues_response.json()
        
        all_zones = []
        for venue in venues:
            # 获取每个场馆的分区
            zones_response = requests.get(f"{API_URL}/api/venues/{venue['id']}/zones")
            zones = zones_response.json()
            # 只保留有容量的分区（排除入口/出口）
            for zone in zones:
                if zone['capacity'] > 0:
                    all_zones.append({
                        "id": zone['id'],
                        "name": zone['name'],
                        "capacity": zone['capacity'],
                        "venue_id": venue['id'],
                        "venue_name": venue['name']
                    })
        return all_zones
    except Exception as e:
        print(f"获取分区失败: {e}")
        return []

def generate_crowd_data(zones, minute):
    """生成人流数据"""
    data_list = []
    
    for zone in zones:
        zone_id = zone["id"]
        capacity = zone["capacity"]
        
        # 根据场馆和分区类型计算人流比例
        if "看台" in zone["name"]:
            if minute < 30:
                ratio = 0.3 + (minute / 30) * 0.5
            elif minute < 90:
                ratio = 0.75 + random.uniform(-0.1, 0.1)
            else:
                progress = (minute - 90) / 30
                ratio = 0.75 * (1 - progress) + random.uniform(-0.1, 0.1)
        elif "内场" in zone["name"] or "VIP" in zone["name"]:
            if minute < 30:
                ratio = 0.4 + (minute / 30) * 0.55
            elif minute < 90:
                ratio = 0.9 + random.uniform(-0.05, 0.05)
            else:
                progress = (minute - 90) / 30
                ratio = 0.9 * (1 - progress) + random.uniform(-0.05, 0.05)
        else:
            ratio = 0.5 + random.uniform(-0.2, 0.2)
        
        ratio = max(0.05, min(0.98, ratio))
        ratio += random.uniform(-0.05, 0.05)
        ratio = max(0, min(1, ratio))
        
        current_count = int(capacity * ratio)
        
        data_list.append({
            "zone_id": zone_id,
            "current_count": current_count,
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    return data_list

def send_data_to_backend(data_list):
    """发送数据到后端"""
    try:
        response = requests.post(f"{API_URL}/api/crowd/batch", json=data_list)
        if response.status_code == 200:
            print(f"✓ 数据发送成功: {len(data_list)} 条记录")
            return True
        else:
            print(f"✗ 发送失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False

def run_simulator():
    """运行模拟器"""
    print("=" * 50)
    print("演唱会人流数据模拟器（多场馆版）")
    print("=" * 50)
    
    # 获取所有分区
    zones = get_all_zones()
    if not zones:
        print("无法获取分区数据，请确保后端已启动")
        return
    
    print(f"发现 {len(zones)} 个分区")
    for zone in zones:
        print(f"  - {zone['venue_name']} / {zone['name']} (容量: {zone['capacity']})")
    
    print("\n模拟时长: 120分钟")
    print("每2秒生成一次数据 (模拟1分钟)")
    print("按 Ctrl+C 停止模拟")
    print("=" * 50)
    
    minute = 0
    try:
        while minute <= 120:
            print(f"\n--- 第 {minute} 分钟 ---")
            
            data_list = generate_crowd_data(zones, minute)
            send_data_to_backend(data_list)
            
            time.sleep(2)
            minute += 1
        
        print("\n模拟完成！")
        
    except KeyboardInterrupt:
        print("\n\n模拟已停止")

if __name__ == "__main__":
    run_simulator()