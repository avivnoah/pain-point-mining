from pydantic import BaseModel
from typing import List, Optional

class PainPoint(BaseModel):
    id: int
    description: str
    source: str
    timestamp: str

class State(BaseModel):
    pain_points: List[PainPoint]
    current_query: Optional[str] = None
    feedback_log: List[str] = []