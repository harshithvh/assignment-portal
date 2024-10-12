from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Submission(BaseModel):
    id: Optional[str]
    userId: str
    task: str
    admin: str
    status: Optional[str] = "pending"
    timestamp: Optional[datetime] = datetime.now()