from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional



class User(BaseModel):
    user_id: str
    email: str
    name: str

class UsersResponse(BaseModel):
    users: List[User]
    count: int

class UserPoints(BaseModel):
    user_id: str
    points: int
    last_updated: datetime

class UserPointsResponse(BaseModel):
    success: bool
    data: UserPoints
    message: str = "Puntos obtenidos exitosamente"   

#####################################
class ChallengeBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=10, max_length=500)
    max_limit: int = Field(..., gt=0)
    reward_id: str = Field(..., min_length=1)
    max_users: int = Field(..., gt=0)
    status: Optional[str] = Field("active", pattern="^(active|inactive|completed|disabled)$")
    max_date: Optional[datetime] = None

class ChallengeCreate(ChallengeBase):
    puntos: int = Field(..., gt=0)

class ChallengeResponse(ChallengeBase):
    challenge_id: str
    date_creation: datetime
    puntos: int = 0
##################################### en listar challenges 
class ChallengesResponse(BaseModel):
    success: bool
    challenges: List[ChallengeResponse]
    count: int

######################################

class RewardCreate(BaseModel):
    type: str = Field(..., min_length=1, description="Tipo de recompensa (ej. 'points', 'badge', 'item')")
    value: str = Field(..., min_length=1, description="Valor de la recompensa")
    metadata: Optional[Dict] = Field(None, description="Metadatos adicionales")

class RewardResponse(RewardCreate):
    reward_id: str
    created_at: datetime


######################################

class ChallengeInstanceCreate(BaseModel):
    user_id: str = Field(..., min_length=1, description="ID del usuario")
    challenge_id: str = Field(..., min_length=1, description="ID del challenge")

class ChallengeInstanceResponse(ChallengeInstanceCreate):
    instance_id: str
    progress: int = 0
    completed: bool = False
    date_started: datetime


###################################

class UserAssignedChallengesResponse(BaseModel):
    success: bool
    user_id: str
    challenges: List[dict]
    count: int
    
    
###################################
class ChallengeProgressResponse(BaseModel):
    success: bool
    message: str

class ChallengeStatusResponse(BaseModel):
    success: bool
    message: str

class ExpiredChallengesResponse(BaseModel):
    success: bool
    message: str
    disabled_count: int

class UserRankingResponse(BaseModel):
    success: bool
    rank: int
    user_id: str
    message: str = "Ranking obtenido exitosamente"