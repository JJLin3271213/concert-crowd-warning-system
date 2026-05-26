import requests
import random
import time
import datetime
import threading
import keyboard

API_URL = "https://secure-achievement-production-a328.up.railway.app"

running = True
paused = False
minute = 0

def get_all_zones():
    """获取所有分区"""
    try:
        venues_response = requests.get(f"{API_URL}/api/venues")
        venues = venues_response.json()
        
        all_zones = []
        for venue in venues:
            zones_response = requests.get(f"{API_URL}/api/venues/{venue['id']}/zones")
            zones = zones_response.json()
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
        capacity = zone["capacity"]
        
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
        current_count = int(capacity * ratio)
        
        data_list.append({
            "zone_id": zone["id"],
            "current_count": current_count,
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    return data_list

def send_data(data_list):
    """发送数据"""
    try:
        response = requests.post(f"{API_URL}/api/crowd/batch", json=data_list)
        return response.status_code == 200
    except Exception as e:
        print(f"发送失败: {e}")
        return False

def control_listener():
    """监听键盘控制"""
    global running, paused
    print("\n控制指令：")
    print("  [空格] - 暂停/继续")
    print("  [ESC]  - 停止模拟")
    print("  [R]    - 重置模拟")
    
    while running:
        if keyboard.is_pressed('space'):
            paused = not paused
            status = "已暂停" if paused else "继续运行"
            print(f"\n⏸️ {status}")
            time.sleep(0.5)
        elif keyboard.is_pressed('esc'):
            running = False
            print("\n🛑 停止模拟")
            break
        elif keyboard.is_pressed('r'):
            global minute
            minute = 0
            print("\n🔄 重置模拟，回到第 0 分钟")
            time.sleep(0.5)
        time.sleep(0.1)

def run_simulator():
    """运行可控模拟器"""
    global running, paused, minute
    
    print("=" * 50)
    print("演唱会人流数据模拟器（可控版）")
    print(f"后端地址: {API_URL}")
    print("=" * 50)
    
    zones = get_all_zones()
    if not zones:
        print("无法获取分区数据，请检查后端")
        return
    
    print(f"发现 {len(zones)} 个分区")
    
    # 启动控制监听线程
    control_thread = threading.Thread(target=control_listener, daemon=True)
    control_thread.start()
    
    print("\n模拟开始...")
    print("按空格暂停/继续，ESC停止，R重置\n")
    
    try:
        while running and minute <= 120:
            if not paused:
                print(f"\n--- 第 {minute} 分钟 ---")
                
                data_list = generate_crowd_data(zones, minute)
                if send_data(data_list):
                    print(f"✓ 数据发送成功: {len(data_list)} 条")
                else:
                    print(f"✗ 数据发送失败")
                
                minute += 1
                time.sleep(2)
            else:
                time.sleep(0.5)
        
        print("\n模拟完成！")
        
    except KeyboardInterrupt:
        print("\n\n模拟已停止")

if __name__ == "__main__":
    # 检查是否安装了 keyboard 库
    try:
        import keyboard
    except ImportError:
        print("正在安装 keyboard 库...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'keyboard'])
        import keyboard
    
    run_simulator()