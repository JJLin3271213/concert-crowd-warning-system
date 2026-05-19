from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 用于接收人流数据的格式
class CrowdDataCreate(BaseModel):
    zone_id: int
    current_count: int
    timestamp: Optional[datetime] = None

# 用于返回人流数据的格式
class CrowdDataResponse(BaseModel):
    id: int
    zone_id: int
    current_count: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# 拥堵等级响应
class AlertResponse(BaseModel):
    zone_id: int
    level: str
    message: str
    created_at: datetime