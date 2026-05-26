import requests
import random
import time
import datetime
import threading
import sys

API_URL = "http://localhost:8000"

running = True
paused = False
minute = 0
anomaly_zones = {}      # {zone_id: extra_ratio} — 异常拥堵分区
anomaly_label = ""       # 异常场景名称


def get_all_zones():
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


def three_phase_ratio(zone_type, minute):
    """三段式人流模型：入场攀升(0-30) → 演出平稳(30-90) → 散场骤降(90-120)"""
    if minute < 30:
        # 入场阶段：线性攀升
        progress = minute / 30.0
        if zone_type == "看台":
            base = 0.15 + progress * 0.60
        elif zone_type == "内场":
            base = 0.20 + progress * 0.70
        else:
            base = 0.20 + progress * 0.50
        noise = random.uniform(-0.03, 0.03)
    elif minute < 90:
        mid_progress = (minute - 30) / 60.0
        if zone_type == "看台":
            base = 0.72 + mid_progress * 0.06
        elif zone_type == "内场":
            base = 0.88 + mid_progress * 0.05
        else:
            base = 0.65 + mid_progress * 0.10
        noise = random.uniform(-0.04, 0.04)
    else:
        exit_progress = (minute - 90) / 30.0
        if zone_type == "看台":
            base = 0.78 * max(0, 1 - exit_progress * 1.05)
        elif zone_type == "内场":
            base = 0.93 * max(0, 1 - exit_progress * 1.1)
        else:
            base = 0.75 * max(0, 1 - exit_progress * 1.0)
        noise = random.uniform(-0.05, 0.05)

    return max(0.01, min(0.99, base + noise))


def generate_crowd_data(zones, minute):
    data_list = []
    for zone in zones:
        capacity = zone["capacity"]
        if "内场" in zone["name"] or "VIP" in zone["name"]:
            zone_type = "内场"
        elif "看台" in zone["name"]:
            zone_type = "看台"
        else:
            zone_type = "其他"

        ratio = three_phase_ratio(zone_type, minute)

        # 异常场景注入
        if zone["id"] in anomaly_zones:
            ratio += anomaly_zones[zone["id"]]
            ratio = min(0.99, ratio)

        current_count = int(capacity * ratio)
        data_list.append({
            "zone_id": zone["id"],
            "current_count": current_count,
            "timestamp": datetime.datetime.now().isoformat()
        })
    return data_list


def send_data(data_list):
    try:
        response = requests.post(f"{API_URL}/api/crowd/batch", json=data_list)
        return response.status_code == 200
    except Exception as e:
        print(f"  发送失败: {e}")
        return False


def print_phase_label(minute):
    if minute == 0:
        return "[入场阶段] 观众开始入场"
    elif minute == 30:
        return "[演出阶段] 演出开始，人流趋于稳定"
    elif minute == 90:
        return "[散场阶段] 演出结束，观众集中散场"
    return ""


def print_status(zones, data_list):
    total = sum(d["current_count"] for d in data_list)
    max_zone = max(data_list, key=lambda d: d["current_count"])
    max_ratio = round(max_zone["current_count"] / max(
        (z["capacity"] for z in zones if z["id"] == max_zone["zone_id"]), default=1) * 100)
    status = f"  总人数: {total:>6d}  |  最挤分区: {max_zone['zone_id']}号区({max_ratio}%)"
    if anomaly_zones:
        status += f"  |  [异常] {anomaly_label}"
    print(status)


def input_listener():
    global running, paused, minute, anomaly_zones, anomaly_label
    print("\n控制指令:")
    print("  [空格] 暂停/继续   [R] 重置   [Q] 退出")
    print("  [1] 模拟A区突发拥堵(+35%)   [2] 模拟B区突发拥堵(+35%)")
    print("  [3] 模拟VIP区拥堵(+40%)     [0] 清除所有异常")

    while running:
        try:
            cmd = sys.stdin.readline().strip().lower()
        except (EOFError, KeyboardInterrupt):
            running = False
            break

        if cmd == '' or cmd == ' ':
            paused = not paused
            print(f"\n>>> {'[已暂停]' if paused else '[继续运行]'}")
        elif cmd == 'r':
            minute = 0
            anomaly_zones = {}
            anomaly_label = ""
            print("\n>>> [已重置] 模拟回到第0分钟，异常已清除")
        elif cmd == 'q':
            running = False
            print("\n>>> [停止] 模拟结束")
            break
        elif cmd == '0':
            anomaly_zones = {}
            anomaly_label = ""
            print("\n>>> 所有异常场景已清除")
        elif cmd in ('1', '2', '3'):
            zones = get_all_zones()
            if cmd == '1':
                target = next((z for z in zones if "A" in z["name"] and "内场" in z["name"]), None)
                anomaly_zones = {target["id"]: 0.35} if target else {}
                anomaly_label = f"{target['name']}突发拥堵" if target else ""
            elif cmd == '2':
                target = next((z for z in zones if "B" in z["name"] and "内场" in z["name"]), None)
                anomaly_zones = {target["id"]: 0.35} if target else {}
                anomaly_label = f"{target['name']}突发拥堵" if target else ""
            elif cmd == '3':
                target = next((z for z in zones if "VIP" in z["name"] or "vip" in z["name"].lower()), None)
                anomaly_zones = {target["id"]: 0.40} if target else {}
                anomaly_label = f"{target['name']}突发拥堵" if target else ""
            print(f"\n>>> [异常注入] {anomaly_label}" if anomaly_zones else "\n>>> 未找到目标分区")


def run_simulator():
    global running, paused, minute

    print("=" * 56)
    print("  演唱会人流数据模拟器 v2.0")
    print("  三段式模型: 入场(0-30min) → 演出(30-90min) → 散场(90-120min)")
    print(f"  后端: {API_URL}")
    print("=" * 56)

    zones = get_all_zones()
    if not zones:
        print("无法获取分区数据，请确保后端已启动")
        return

    print(f"  已加载 {len(zones)} 个分区")
    for z in zones:
        print(f"    {z['venue_name']} / {z['name']} (容量:{z['capacity']})")

    t = threading.Thread(target=input_listener, daemon=True)
    t.start()

    print("\n  模拟开始... (每2秒=1分钟, 共120分钟)\n")

    try:
        while running and minute <= 120:
            if not paused:
                phase = print_phase_label(minute)
                if phase:
                    print(f"\n{'='*40}\n  {phase}\n{'='*40}")

                print(f"[{minute:>3}min]", end="")
                data_list = generate_crowd_data(zones, minute)
                if send_data(data_list):
                    print_status(zones, data_list)
                else:
                    print("  发送失败")
                minute += 1
                time.sleep(2)
            else:
                time.sleep(0.3)

        print(f"\n{'='*40}\n  模拟结束 (共{minute}分钟)\n{'='*40}")
    except KeyboardInterrupt:
        print("\n  模拟已停止")


if __name__ == "__main__":
    run_simulator()
