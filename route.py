from sqlalchemy.orm import Session
from models import RoadNetwork, Zone

def get_route_graph(db: Session, venue_id: int):
    """从数据库获取路网图"""
    roads = db.query(RoadNetwork).filter(RoadNetwork.venue_id == venue_id).all()
    
    graph = {}
    for road in roads:
        if road.from_zone_id not in graph:
            graph[road.from_zone_id] = []
        graph[road.from_zone_id].append(road.to_zone_id)
        # 确保 to_zone_id 也在图中，即使它没有出边
        if road.to_zone_id not in graph:
            graph[road.to_zone_id] = []

    return graph

def get_node_names(db: Session, venue_id: int):
    """获取节点名称映射"""
    zones = db.query(Zone).filter(Zone.venue_id == venue_id).all()
    return {zone.id: zone.name for zone in zones}

def dijkstra(graph, start, end, congestion_weights=None):
    """Dijkstra最短路径算法"""
    import heapq
    
    if congestion_weights is None:
        congestion_weights = {}
    
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    pq = [(0, start)]
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        if current == end:
            break
        
        if current_dist > distances[current]:
            continue
        
        for neighbor in graph.get(current, []):
            base_cost = 1
            congestion_cost = congestion_weights.get(neighbor, 0)
            new_dist = current_dist + base_cost + congestion_cost
            
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))
    
    path = []
    node = end
    while node is not None:
        path.insert(0, node)
        node = previous.get(node)
    
    return path if len(path) > 1 else []

def calculate_congestion_weight(zone_id, latest_data, alpha=2.0):
    """根据拥堵率计算动态权重 W = Wbase + α × C
    返回拥堵惩罚值 α × C（Wbase=1 在Dijkstra中作为base_cost）
    α默认=2.0，可通过系统配置调整"""
    if zone_id not in latest_data:
        return 0

    congestion_rate = latest_data[zone_id].get("congestion_rate", 0)
    C = congestion_rate / 100.0
    return alpha * C