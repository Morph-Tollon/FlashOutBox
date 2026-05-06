from pydantic import BaseModel

class VersionModel(BaseModel):
    app_version: str
    
class PingResponseModel(BaseModel):
    round_trip_time_ms: float
    osc_latency_ms: float