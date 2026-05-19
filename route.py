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

def calculate_congestion_weight(zone_id, latest_data):
    """根据拥堵等级计算权重"""
    if zone_id not in latest_data:
        return 0
    
    congestion_rate = latest_data[zone_id].get("congestion_rate", 0)
    
    if congestion_rate >= 80:
        return 100
    elif congestion_rate >= 60:
        return 50
    elif congestion_rate >= 40:
        return 10
    else:
        return 0