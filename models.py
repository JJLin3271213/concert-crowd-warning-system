from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from database import Base
import datetime

# 场馆表
class Venue(Base):
    __tablename__ = "venues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 场馆名称
    address = Column(String(200))  # 地址
    total_capacity = Column(Integer, default=0)  # 总容量
    created_at = Column(DateTime, default=datetime.datetime.now)

# 分区表
class Zone(Base):
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, nullable=False)  # 所属场馆ID
    name = Column(String(50), nullable=False)  # 分区名称
    capacity = Column(Integer, nullable=False)  # 最大容量
    center_lng = Column(Float, default=0)  # 中心经度
    center_lat = Column(Float, default=0)  # 中心纬度
    is_exit = Column(Integer, default=0)  # 是否为出口 (1=是)
    sort_order = Column(Integer, default=0)  # 排序顺序

# 路网表（节点连接关系）
class RoadNetwork(Base):
    __tablename__ = "road_network"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, nullable=False)  # 所属场馆ID
    from_zone_id = Column(Integer, nullable=False)  # 起点分区ID
    to_zone_id = Column(Integer, nullable=False)    # 终点分区ID
    distance = Column(Integer, default=1)  # 距离权重

# 人流记录表
class CrowdData(Base):
    __tablename__ = "crowd_data"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, nullable=False)
    current_count = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now)

# 预警记录表
class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, nullable=False)
    level = Column(String(20))
    message = Column(String(200))
    created_at = Column(DateTime, default=datetime.datetime.now)

# 用户表（管理员）
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_admin = Column(Integer, default=1)
    # 应急点位表
class EmergencyPoint(Base):
    __tablename__ = "emergency_points"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, nullable=False)  # 所属场馆ID
    name = Column(String(100), nullable=False)  # 点位名称（如"急救站A"）
    type = Column(String(50), default="medical")  # 类型: medical, security, fire, exit
    zone_id = Column(Integer)  # 关联的分区ID
    lng = Column(Float)  # 经度
    lat = Column(Float)  # 纬度
    phone = Column(String(20))  # 联系电话
    description = Column(String(200))  # 描述
    status = Column(Integer, default=1)  # 状态: 1正常, 0停用

# 系统配置表
class SystemConfig(Base):
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(500))
    description = Column(String(200))
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    # 演出信息表
class Performance(Base):
    __tablename__ = "performances"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, nullable=False)
    artist_name = Column(String(100), nullable=False)
    performance_date = Column(String(50))
    start_time = Column(String(20))
    end_time = Column(String(20))
    ticket_price = Column(String(200))
    description = Column(String(500))
    poster_url = Column(String(500))
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)


# 应急求助记录表
class EmergencyHelp(Base):
    __tablename__ = "emergency_help"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, nullable=False)
    venue_id = Column(Integer, nullable=False)
    message = Column(String(500))
    status = Column(String(20), default="pending")  # pending: 待处理, confirmed: 已确认
    created_at = Column(DateTime, default=datetime.datetime.now)
    confirmed_at = Column(DateTime, nullable=True)