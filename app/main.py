from fastapi import FastAPI, HTTPException
from app.crud import *
from firebase_admin import credentials
from fastapi import FastAPI, HTTPException, Path
from app.schemas import UserPointsResponse
from app.crud import get_user_points
from fastapi import FastAPI, HTTPException, status
from app.schemas import ChallengeCreate, ChallengeResponse
from app.crud import create_challenge
from fastapi import FastAPI, HTTPException, status
from app.schemas import RewardCreate, RewardResponse
from app.crud import create_reward, get_all_rewards
from app.schemas import ChallengeInstanceCreate, ChallengeInstanceResponse
from app.crud import assign_challenge_to_user
from app.schemas import ChallengesResponse
from app.schemas import UserAssignedChallengesResponse

# Configuración Firebase
cred = credentials.Certificate("app/firebase-key.json")
firebase_admin.initialize_app(cred)

app = FastAPI()

@app.get("/users", summary="Obtener todos los usuarios")
async def get_all_users():
    try:
        db = firestore.client()
        users_ref = db.collection("users")
        users = [doc.to_dict() for doc in users_ref.stream()]
        
        if not users:
            raise HTTPException(status_code=404, detail="No se encontraron usuarios")
            
        return {"users": users, "count": len(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint para obtener puntos de un usuario específico

@app.get("/users/{user_id}/points", 
         response_model=UserPointsResponse,
         tags=["User Points"])
async def get_points(
    user_id: str = Path(..., description="ID del usuario a consultar", min_length=1)
):
    try:
        points_data = get_user_points(user_id)
        return {
            "success": True,
            "data": points_data
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener puntos: {str(e)}"
        )


# Endpoint para inicializar puntos de un usuario

@app.post("/users/{user_id}/points/init", tags=["User Points"])
async def init_points(user_id: str):
    try:
        init_user_points(user_id)
        return {"success": True, "message": "Puntos inicializados a 0"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al inicializar puntos: {str(e)}"
        )

# Endpoint para crear un nuevo challenge

@app.post("/challenges",
         response_model=ChallengeResponse,
         status_code=status.HTTP_201_CREATED,
         tags=["Challenges"])
async def create_new_challenge(challenge: ChallengeCreate):
    try:
        challenge_data = challenge.dict()
        created_challenge = create_challenge(challenge_data)
        return created_challenge
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al crear el challenge: {str(e)}"
        )

# Endpoint para obtener todos los challenges

@app.get("/challenges",
         response_model=ChallengesResponse,
         tags=["Challenges"])
async def get_challenges():
    try:
        challenges = get_all_challenges()
        return {
            "success": True,
            "challenges": challenges,
            "count": len(challenges)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener challenges: {str(e)}"
        )


# Endpoint para obtener todas las recompensas y Crear nuevas recompensas

@app.post("/rewards",
         response_model=RewardResponse,
         status_code=status.HTTP_201_CREATED,
         tags=["Rewards"])
async def create_new_reward(reward: RewardCreate):
    try:
        reward_data = reward.dict()
        created_reward = create_reward(reward_data)
        return created_reward
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al crear la recompensa: {str(e)}"
        )

@app.get("/rewards",
        response_model=list[RewardResponse],
        tags=["Rewards"])
async def get_rewards():
    try:
        return get_all_rewards()
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener recompensas: {str(e)}"
        )

# Endpoints para asignar un challenge a un usuario

@app.post("/challenge-instances",
         response_model=ChallengeInstanceResponse,
         status_code=status.HTTP_201_CREATED,
         tags=["Challenge Instances"])
async def create_challenge_instance(instance: ChallengeInstanceCreate):
    try:
        instance_data = instance.dict()
        created_instance = assign_challenge_to_user(instance_data)
        return created_instance
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al asignar challenge: {str(e)}"
        )

# Endpoint para obtener los challenges asignados a un usuario específico

@app.get("/users/{user_id}/assigned-challenges",
         response_model=UserAssignedChallengesResponse,
         tags=["User Challenges"])
def get_user_assigned_challenges_endpoint(
    user_id: str = Path(..., description="ID del usuario para obtener sus challenges asignados", min_length=1)
):
    try:
        challenges = get_user_assigned_challenges(user_id)
        return {
            "success": True,
            "user_id": user_id,
            "challenges": challenges,
            "count": len(challenges)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener challenges del usuario: {str(e)}"
        )
