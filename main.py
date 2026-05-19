from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from database import get_db
from models import CrowdData, Zone, Venue, RoadNetwork, User, Performance, EmergencyPoint, SystemConfig
from schemas import CrowdDataCreate
from auth import authenticate_user, create_access_token, get_current_user

# 创建 FastAPI 应用
app = FastAPI(
    title="🎤 演唱会人流预警系统 API",
    description="""
## 系统简介

本系统为大型演唱会、音乐节等演艺活动提供人流监测、拥堵预警、智能路线规划等功能。

---

## 主要功能模块

### 📊 人流监测
- 实时获取各分区人流数据
- 自动判断拥堵等级（绿/黄/橙/红）
- 历史数据查询与趋势分析

### 🚨 预警推送
- 拥堵率达到80%时自动触发
- 邮件实时推送至管理员
- 5分钟内不重复发送

### 🗺️ 路线规划
- 基于 Dijkstra 算法
- 结合实时拥堵权重
- 支持应急出口导航

### 📈 数据导出
- 支持 Excel 格式导出
- 包含分区、人数、拥挤度等字段

### 🏟️ 场馆管理
- 多场馆动态配置
- 分区信息管理
- 路网拓扑管理

---

## 拥堵等级说明

| 等级 | 拥堵率 | 颜色 | 建议 |
|------|--------|------|------|
| 畅通 | < 40% | 🟢 绿色 | 正常通行 |
| 较堵 | 40% - 60% | 🟡 黄色 | 通行缓慢 |
| 拥堵 | 60% - 80% | 🟠 橙色 | 严重拥堵 |
| 严重拥堵 | ≥ 80% | 🔴 红色 | 需立即疏导 |

---
    """,
    version="1.0.0",
    contact={
        "name": "演唱会人流预警系统",
        "email": "admin@concert-system.com",
    },
    license_info={
        "name": "MIT License",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "本地开发服务器"},
    ],
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 系统接口 ==========
@app.get("/", tags=["系统"])
def root():
    return {"message": "演唱会人流预警系统运行中", "version": "1.0.0"}

@app.get("/api/health", tags=["系统"])
def health():
    return {"status": "ok", "message": "服务正常", "timestamp": datetime.now().isoformat()}

# ========== 人流数据接口 ==========
@app.post("/api/crowd", tags=["人流监测"])
def add_crowd_data(data: CrowdDataCreate, db: Session = Depends(get_db)):
    if data.timestamp is None:
        data.timestamp = datetime.now()
    crowd_record = CrowdData(
        zone_id=data.zone_id,
        current_count=data.current_count,
        timestamp=data.timestamp
    )
    db.add(crowd_record)
    db.commit()
    db.refresh(crowd_record)
    return {"message": "数据已保存", "id": crowd_record.id}

@app.post("/api/crowd/batch", tags=["人流监测"])
def add_crowd_data_batch(data_list: List[CrowdDataCreate], db: Session = Depends(get_db)):
    records = []
    for data in data_list:
        if data.timestamp is None:
            data.timestamp = datetime.now()
        record = CrowdData(
            zone_id=data.zone_id,
            current_count=data.current_count,
            timestamp=data.timestamp
        )
        records.append(record)
    db.add_all(records)
    db.commit()
    return {"message": f"已保存 {len(records)} 条数据"}

@app.get("/api/crowd/latest", tags=["人流监测"])
def get_latest_crowd(venue_id: int = 1, db: Session = Depends(get_db)):
    from sqlalchemy import desc
    
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    venue_name = venue.name if venue else "未知场馆"
    
    zones = db.query(Zone).filter(Zone.venue_id == venue_id).all()
    result = []
    for zone in zones:
        if zone.capacity == 0:
            continue
        latest = db.query(CrowdData).filter(
            CrowdData.zone_id == zone.id
        ).order_by(desc(CrowdData.timestamp)).first()
        if latest:
            congestion_rate = latest.current_count / zone.capacity
            if congestion_rate >= 0.8:
                level = "red"
            elif congestion_rate >= 0.6:
                level = "orange"
            elif congestion_rate >= 0.4:
                level = "yellow"
            else:
                level = "green"
            
            if level == "red":
                from notify import check_and_send_alert
                check_and_send_alert(zone.id, zone.name, round(congestion_rate * 100), latest.current_count, zone.capacity, venue_name)
            
            result.append({
                "zone_id": zone.id,
                "zone_name": zone.name,
                "current_count": latest.current_count,
                "capacity": zone.capacity,
                "congestion_rate": round(congestion_rate * 100),
                "level": level,
                "timestamp": latest.timestamp
            })
    return result

@app.get("/api/crowd/history/{zone_id}", tags=["人流监测"])
def get_crowd_history(zone_id: int, limit: int = 10, db: Session = Depends(get_db)):
    records = db.query(CrowdData).filter(
        CrowdData.zone_id == zone_id
    ).order_by(CrowdData.timestamp.desc()).limit(limit).all()
    return records

# ========== 认证接口 ==========
@app.post("/api/login", tags=["认证"])
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "is_admin": user.is_admin
    }

@app.get("/api/verify", tags=["认证"])
def verify_token(current_user: User = Depends(get_current_user)):
    return {"valid": True, "username": current_user.username, "is_admin": current_user.is_admin}

@app.get("/api/me", tags=["认证"])
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "is_admin": current_user.is_admin}

# ========== 导出报表 ==========
@app.get("/api/export/excel", tags=["报表导出"])
def export_excel(venue_id: int = 1, db: Session = Depends(get_db)):
    import io
    import pandas as pd
    zones = db.query(Zone).filter(Zone.venue_id == venue_id).all()
    data = []
    for zone in zones:
        if zone.capacity == 0:
            continue
        latest = db.query(CrowdData).filter(
            CrowdData.zone_id == zone.id
        ).order_by(CrowdData.timestamp.desc()).first()
        if latest:
            congestion_rate = latest.current_count / zone.capacity
            if congestion_rate >= 0.8:
                level = "严重拥堵"
            elif congestion_rate >= 0.6:
                level = "拥堵"
            elif congestion_rate >= 0.4:
                level = "较堵"
            else:
                level = "畅通"
            data.append({
                "分区名称": zone.name,
                "当前人数": latest.current_count,
                "总容量": zone.capacity,
                "拥挤度": f"{round(congestion_rate * 100)}%",
                "状态": level,
                "更新时间": latest.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='人流拥堵数据', index=False)
    output.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=crowd_data.xlsx"}
    )

# ========== 趋势图 ==========
@app.get("/api/trend/{zone_id}", tags=["数据分析"])
def get_zone_trend(zone_id: int, minutes: int = 30, db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    start_time = datetime.now() - timedelta(minutes=minutes)
    records = db.query(CrowdData).filter(
        CrowdData.zone_id == zone_id,
        CrowdData.timestamp >= start_time
    ).order_by(CrowdData.timestamp.asc()).all()
    trend_data = []
    for record in records:
        trend_data.append({
            "time": record.timestamp.strftime("%H:%M"),
            "count": record.current_count,
            "timestamp": record.timestamp.isoformat()
        })
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    return {
        "zone_id": zone_id,
        "zone_name": zone.name if zone else "未知",
        "capacity": zone.capacity if zone else 0,
        "minutes": minutes,
        "data": trend_data
    }

# ========== 场馆管理 ==========
@app.get("/api/venues", tags=["场馆管理"])
def get_venues(db: Session = Depends(get_db)):
    venues = db.query(Venue).all()
    return venues

@app.post("/api/venues", tags=["场馆管理"])
def create_venue(name: str, address: str = "", total_capacity: int = 0, db: Session = Depends(get_db)):
    venue = Venue(name=name, address=address, total_capacity=total_capacity)
    db.add(venue)
    db.commit()
    db.refresh(venue)
    return venue

@app.put("/api/venues/{venue_id}", tags=["场馆管理"])
def update_venue(venue_id: int, name: str, address: str = "", total_capacity: int = 0, db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="场馆不存在")
    venue.name = name
    venue.address = address
    venue.total_capacity = total_capacity
    db.commit()
    return venue

@app.delete("/api/venues/{venue_id}", tags=["场馆管理"])
def delete_venue(venue_id: int, db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="场馆不存在")
    db.delete(venue)
    db.commit()
    return {"message": "删除成功"}

# ========== 分区管理 ==========
@app.get("/api/venues/{venue_id}/zones", tags=["分区管理"])
def get_zones(venue_id: int, db: Session = Depends(get_db)):
    zones = db.query(Zone).filter(Zone.venue_id == venue_id).order_by(Zone.sort_order).all()
    return zones

@app.post("/api/zones", tags=["分区管理"])
def create_zone(venue_id: int, name: str, capacity: int, is_exit: int = 0, sort_order: int = 0, db: Session = Depends(get_db)):
    zone = Zone(venue_id=venue_id, name=name, capacity=capacity, is_exit=is_exit, sort_order=sort_order)
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone

@app.put("/api/zones/{zone_id}", tags=["分区管理"])
def update_zone(zone_id: int, name: str, capacity: int, is_exit: int = 0, sort_order: int = 0, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="分区不存在")
    zone.name = name
    zone.capacity = capacity
    zone.is_exit = is_exit
    zone.sort_order = sort_order
    db.commit()
    return zone

@app.delete("/api/zones/{zone_id}", tags=["分区管理"])
def delete_zone(zone_id: int, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="分区不存在")
    db.delete(zone)
    db.commit()
    return {"message": "删除成功"}

# ========== 路网管理 ==========
@app.get("/api/venues/{venue_id}/road_network", tags=["路网管理"])
def get_road_network(venue_id: int, db: Session = Depends(get_db)):
    roads = db.query(RoadNetwork).filter(RoadNetwork.venue_id == venue_id).all()
    return roads

@app.post("/api/road_network", tags=["路网管理"])
def add_road(from_zone_id: int, to_zone_id: int, venue_id: int = 1, distance: int = 1, db: Session = Depends(get_db)):
    road = RoadNetwork(venue_id=venue_id, from_zone_id=from_zone_id, to_zone_id=to_zone_id, distance=distance)
    db.add(road)
    db.commit()
    return road

@app.delete("/api/road_network/{road_id}", tags=["路网管理"])
def delete_road(road_id: int, db: Session = Depends(get_db)):
    road = db.query(RoadNetwork).filter(RoadNetwork.id == road_id).first()
    if not road:
        raise HTTPException(status_code=404, detail="路网连接不存在")
    db.delete(road)
    db.commit()
    return {"message": "删除成功"}

# ========== 路线规划 ==========
@app.get("/api/route/plan", tags=["路线规划"])
def plan_route(start: int, end: int, venue_id: int = 1, db: Session = Depends(get_db)):
    from route import get_route_graph, get_node_names, dijkstra, calculate_congestion_weight
    from sqlalchemy import desc
    
    graph = get_route_graph(db, venue_id)
    node_names = get_node_names(db, venue_id)
    
    if start not in node_names:
        return {"error": f"无效的起点: {start}"}
    if end not in node_names:
        return {"error": f"无效的终点: {end}"}
    
    zones = db.query(Zone).filter(Zone.venue_id == venue_id).all()
    latest_data = {}
    for zone in zones:
        latest = db.query(CrowdData).filter(
            CrowdData.zone_id == zone.id
        ).order_by(desc(CrowdData.timestamp)).first()
        if latest and zone.capacity > 0:
            congestion_rate = latest.current_count / zone.capacity
            latest_data[zone.id] = {
                "congestion_rate": round(congestion_rate * 100),
                "current_count": latest.current_count,
                "capacity": zone.capacity,
                "level": "red" if congestion_rate >= 0.8 else "orange" if congestion_rate >= 0.6 else "yellow" if congestion_rate >= 0.4 else "green"
            }
    
    congestion_weights = {}
    for node_id in graph.keys():
        if node_id in latest_data:
            weight = calculate_congestion_weight(node_id, latest_data)
            congestion_weights[node_id] = weight
    
    path = dijkstra(graph, start, end, congestion_weights)
    
    if not path or len(path) < 2:
        return {"error": "无法找到路径", "start": start, "end": end}
    
    path_names = [node_names.get(node, f"未知{node}") for node in path]
    
    path_details = []
    total_congestion = 0
    congestion_count = 0
    
    for node in path:
        if node in latest_data:
            data = latest_data[node]
            path_details.append({
                "node_id": node,
                "name": node_names.get(node, f"未知{node}"),
                "congestion_rate": data["congestion_rate"],
                "current_count": data["current_count"],
                "capacity": data["capacity"],
                "level": data["level"]
            })
            total_congestion += data["congestion_rate"]
            congestion_count += 1
        else:
            path_details.append({
                "node_id": node,
                "name": node_names.get(node, f"未知{node}"),
                "congestion_rate": 0,
                "current_count": 0,
                "capacity": 0,
                "level": "green"
            })
    
    avg_congestion = round(total_congestion / congestion_count, 1) if congestion_count > 0 else 0
    has_red = any(d.get("level") == "red" for d in path_details)
    is_congested = avg_congestion >= 60 or has_red
    
    return {
        "start": start,
        "start_name": node_names.get(start, "未知"),
        "end": end,
        "end_name": node_names.get(end, "未知"),
        "path": path,
        "path_names": path_names,
        "steps": len(path) - 1,
        "path_details": path_details,
        "avg_congestion": avg_congestion,
        "is_congested": is_congested
    }

@app.get("/api/route/nodes", tags=["路线规划"])
def get_route_nodes(venue_id: int = 1, db: Session = Depends(get_db)):
    """获取指定场馆的所有可用节点"""
    from route import get_node_names
    node_names = get_node_names(db, venue_id)
    return {"nodes": [{"id": k, "name": v} for k, v in node_names.items()]}

@app.get("/api/route/evacuate/{zone_id}", tags=["路线规划"])
def evacuate_route(zone_id: int, venue_id: int = 1, db: Session = Depends(get_db)):
    from route import get_route_graph, get_node_names, dijkstra, calculate_congestion_weight
    from sqlalchemy import desc
    graph = get_route_graph(db, venue_id)
    node_names = get_node_names(db, venue_id)
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        return {"error": f"分区 {zone_id} 不存在"}
    exits = db.query(Zone).filter(Zone.venue_id == venue_id, Zone.is_exit == 1).all()
    if not exits:
        return {"error": "未找到应急出口"}
    zones = db.query(Zone).filter(Zone.venue_id == venue_id).all()
    latest_data = {}
    for z in zones:
        latest = db.query(CrowdData).filter(CrowdData.zone_id == z.id).order_by(desc(CrowdData.timestamp)).first()
        if latest and z.capacity > 0:
            congestion_rate = latest.current_count / z.capacity
            latest_data[z.id] = {"congestion_rate": round(congestion_rate * 100)}
    congestion_weights = {}
    for node_id in graph.keys():
        if node_id in latest_data:
            weight = calculate_congestion_weight(node_id, latest_data)
            congestion_weights[node_id] = weight
    best_path = None
    best_exit = None
    for exit_node in exits:
        path = dijkstra(graph, zone_id, exit_node.id, congestion_weights)
        if path and len(path) > 1:
            if best_path is None or len(path) < len(best_path):
                best_path = path
                best_exit = exit_node
    if not best_path:
        return {"error": "无法找到应急出口路径"}
    path_names = [node_names.get(node, f"未知{node}") for node in best_path]
    return {"zone_id": zone_id, "zone_name": zone.name, "path_names": path_names, "steps": len(best_path) - 1}

# ========== 演出信息管理 ==========
@app.get("/api/performances", tags=["演出管理"])
def get_performances(venue_id: int = 1, db: Session = Depends(get_db)):
    performances = db.query(Performance).filter(Performance.venue_id == venue_id).order_by(Performance.performance_date.desc()).all()
    return performances

@app.post("/api/performances", tags=["演出管理"])
def add_performance(
    venue_id: int,
    artist_name: str,
    performance_date: str,
    start_time: str,
    end_time: str,
    ticket_price: str = "",
    description: str = "",
    poster_url: str = "",
    db: Session = Depends(get_db)
):
    performance = Performance(
        venue_id=venue_id,
        artist_name=artist_name,
        performance_date=performance_date,
        start_time=start_time,
        end_time=end_time,
        ticket_price=ticket_price,
        description=description,
        poster_url=poster_url
    )
    db.add(performance)
    db.commit()
    db.refresh(performance)
    return performance

@app.put("/api/performances/{performance_id}", tags=["演出管理"])
def update_performance(
    performance_id: int,
    artist_name: str,
    performance_date: str,
    start_time: str,
    end_time: str,
    ticket_price: str = "",
    description: str = "",
    poster_url: str = "",
    db: Session = Depends(get_db)
):
    performance = db.query(Performance).filter(Performance.id == performance_id).first()
    if not performance:
        raise HTTPException(status_code=404, detail="演出信息不存在")
    performance.artist_name = artist_name
    performance.performance_date = performance_date
    performance.start_time = start_time
    performance.end_time = end_time
    performance.ticket_price = ticket_price
    performance.description = description
    performance.poster_url = poster_url
    db.commit()
    return performance

@app.delete("/api/performances/{performance_id}", tags=["演出管理"])
def delete_performance(performance_id: int, db: Session = Depends(get_db)):
    performance = db.query(Performance).filter(Performance.id == performance_id).first()
    if not performance:
        raise HTTPException(status_code=404, detail="演出信息不存在")
    db.delete(performance)
    db.commit()
    return {"message": "删除成功"}

# ========== 应急点位管理 ==========
@app.get("/api/emergency/points", tags=["应急管理"])
def get_emergency_points(venue_id: int = 1, db: Session = Depends(get_db)):
    points = db.query(EmergencyPoint).filter(EmergencyPoint.venue_id == venue_id, EmergencyPoint.status == 1).all()
    return points

@app.post("/api/emergency/points", tags=["应急管理"])
def add_emergency_point(
    venue_id: int,
    name: str,
    type: str,
    zone_id: int = 0,
    lng: float = 0,
    lat: float = 0,
    phone: str = "",
    description: str = "",
    db: Session = Depends(get_db)
):
    point = EmergencyPoint(
        venue_id=venue_id,
        name=name,
        type=type,
        zone_id=zone_id,
        lng=lng,
        lat=lat,
        phone=phone,
        description=description
    )
    db.add(point)
    db.commit()
    db.refresh(point)
    return point

@app.put("/api/emergency/points/{point_id}", tags=["应急管理"])
def update_emergency_point(
    point_id: int,
    name: str,
    type: str,
    zone_id: int = 0,
    lng: float = 0,
    lat: float = 0,
    phone: str = "",
    description: str = "",
    status: int = 1,
    db: Session = Depends(get_db)
):
    point = db.query(EmergencyPoint).filter(EmergencyPoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="应急点位不存在")
    point.name = name
    point.type = type
    point.zone_id = zone_id
    point.lng = lng
    point.lat = lat
    point.phone = phone
    point.description = description
    point.status = status
    db.commit()
    return point

@app.delete("/api/emergency/points/{point_id}", tags=["应急管理"])
def delete_emergency_point(point_id: int, db: Session = Depends(get_db)):
    point = db.query(EmergencyPoint).filter(EmergencyPoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="应急点位不存在")
    db.delete(point)
    db.commit()
    return {"message": "删除成功"}

@app.get("/api/emergency/nearby", tags=["应急管理"])
def get_nearby_emergency(zone_id: int, venue_id: int = 1, db: Session = Depends(get_db)):
    from route import get_route_graph, dijkstra, calculate_congestion_weight
    from sqlalchemy import desc
    graph = get_route_graph(db, venue_id)
    zones = db.query(Zone).filter(Zone.venue_id == venue_id).all()
    latest_data = {}
    for zone in zones:
        latest = db.query(CrowdData).filter(
            CrowdData.zone_id == zone.id
        ).order_by(desc(CrowdData.timestamp)).first()
        if latest and zone.capacity > 0:
            congestion_rate = latest.current_count / zone.capacity
            latest_data[zone.id] = {"congestion_rate": round(congestion_rate * 100)}
    congestion_weights = {}
    for node_id in graph.keys():
        if node_id in latest_data:
            weight = calculate_congestion_weight(node_id, latest_data)
            congestion_weights[node_id] = weight
    points = db.query(EmergencyPoint).filter(
        EmergencyPoint.venue_id == venue_id,
        EmergencyPoint.status == 1
    ).all()
    result = []
    for point in points:
        if point.zone_id and point.zone_id in graph:
            path = dijkstra(graph, zone_id, point.zone_id, congestion_weights)
            if path:
                result.append({
                    "id": point.id,
                    "name": point.name,
                    "type": point.type,
                    "zone_id": point.zone_id,
                    "phone": point.phone,
                    "description": point.description,
                    "steps": len(path) - 1,
                    "path": path
                })
    result.sort(key=lambda x: x["steps"])
    return result[:5]

@app.post("/api/emergency/help", tags=["应急管理"])
def send_emergency_help(zone_id: int, message: str = "", db: Session = Depends(get_db)):
    from notify import send_alert_email
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    venue = db.query(Venue).filter(Venue.id == zone.venue_id).first() if zone else None
    zone_name = zone.name if zone else f"分区{zone_id}"
    venue_name = venue.name if venue else "未知场馆"
    help_message = f"""
    <h2>🚨 应急求助通知</h2>
    <p><strong>求助时间：</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>所属场馆：</strong> {venue_name}</p>
    <p><strong>求助位置：</strong> {zone_name}</p>
    <p><strong>补充说明：</strong> {message if message else '无'}</p>
    <hr>
    <p style="color: #f44336; font-weight: bold;">请立即处理！</p>
    """
    send_alert_email(zone_name, 0, 0, 0, venue_name, help_message)
    return {"message": "求助已发送", "zone_id": zone_id, "zone_name": zone_name, "venue_name": venue_name}

# ========== 系统配置管理 ==========
@app.get("/api/config", tags=["系统配置"])
def get_config(key: str = None, db: Session = Depends(get_db)):
    if key:
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        return {"key": key, "value": config.value if config else None}
    else:
        configs = db.query(SystemConfig).all()
        return configs

@app.post("/api/config", tags=["系统配置"])
def set_config(key: str, value: str, description: str = "", db: Session = Depends(get_db)):
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if config:
        config.value = value
        if description:
            config.description = description
    else:
        config = SystemConfig(key=key, value=value, description=description)
        db.add(config)
    db.commit()
    return {"message": "配置已保存", "key": key, "value": value}

# ========== 人流预测功能 ==========
@app.get("/api/predict/{zone_id}", tags=["人流预测"])
def predict_crowd(zone_id: int, minutes_ahead: int = 10, venue_id: int = 1, db: Session = Depends(get_db)):
    from sqlalchemy import desc
    from datetime import datetime, timedelta
    
    historical = db.query(CrowdData).filter(
        CrowdData.zone_id == zone_id
    ).order_by(desc(CrowdData.timestamp)).limit(30).all()
    
    if len(historical) < 5:
        return {"error": "历史数据不足，无法预测", "zone_id": zone_id}
    
    historical.reverse()
    counts = [h.current_count for h in historical]
    
    window = min(10, len(counts))
    moving_avg = sum(counts[-window:]) / window
    
    if len(counts) >= 5:
        recent_trend = (counts[-1] - counts[-5]) / 5
    else:
        recent_trend = 0
    
    predictions = []
    for i in range(1, minutes_ahead + 1):
        predicted = moving_avg + recent_trend * i
        predicted = max(0, int(predicted))
        predictions.append({
            "minute": i,
            "predicted_count": predicted,
            "timestamp": (datetime.now() + timedelta(minutes=i)).isoformat()
        })
    
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    
    return {
        "zone_id": zone_id,
        "zone_name": zone.name if zone else "未知",
        "capacity": zone.capacity if zone else 0,
        "current_count": counts[-1],
        "minutes_ahead": minutes_ahead,
        "predictions": predictions,
        "method": "moving_average"
    }

@app.get("/api/predict/all", tags=["人流预测"])
def predict_all_zones(minutes_ahead: int = 10, venue_id: int = 1, db: Session = Depends(get_db)):
    zones = db.query(Zone).filter(Zone.venue_id == venue_id, Zone.capacity > 0).all()
    results = []
    for zone in zones:
        pred = predict_crowd(zone.id, minutes_ahead, venue_id, db)
        if "error" not in pred:
            results.append(pred)
    return results