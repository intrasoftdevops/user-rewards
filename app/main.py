from fastapi import FastAPI, HTTPException
from app.crud import *
from firebase_admin import credentials
from fastapi import FastAPI, HTTPException, Path
from app.schemas import UserPointsResponse
from app.crud import get_user_points
from fastapi import FastAPI, HTTPException, status
from app.schemas import ChallengeCreate, ChallengeResponse, ChallengeStatusResponse, ExpiredChallengesResponse
from app.crud import create_challenge
from fastapi import FastAPI, HTTPException, status
from app.schemas import RewardCreate, RewardResponse
from app.schemas import ChallengeInstanceCreate, ChallengeInstanceResponse, ChallengeProgressResponse
from app.crud import assign_challenge_to_user
from app.schemas import ChallengesResponse
from app.schemas import UserAssignedChallengesResponse
from app.schemas import UserRankingResponse

# Configuración Firebase
cred = credentials.Certificate("app/firebase-key.json")
firebase_admin.initialize_app(cred)

app = FastAPI()

@app.get("/usuarios", summary="Obtener todos los usuarios", tags=["Usuarios"])
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

@app.get("/usuarios/{user_id}/puntos", 
         response_model=UserPointsResponse,
         tags=["Puntos de Usuario"],
         summary="Obtener los puntos de un usuario")
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

@app.post("/usuarios/{user_id}/puntos/iniciar", tags=["Puntos de Usuario"], summary="Inicializar los puntos de un usuario a cero")
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

@app.post("/retos",
         response_model=ChallengeResponse,
         status_code=status.HTTP_201_CREATED,
         tags=["Retos"],
         summary="Crear un nuevo reto")
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

@app.get("/retos",
         response_model=ChallengesResponse,
         tags=["Retos"],
         summary="Obtener todos los retos")
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

@app.post("/retos/deshabilitar-expirados",
          response_model=ExpiredChallengesResponse,
          tags=["Retos"],
          summary="Desactivar challenges con fecha expirada")
async def disable_expired_challenges_endpoint():
    try:
        result = disable_expired_challenges()
        return {
            "success": True, 
            "message": result.get("message"), 
            "disabled_count": result.get("disabled_count")
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la desactivación de challenges: {str(e)}"
        )

@app.put("/retos/{challenge_id}/desactivar",
         response_model=ChallengeStatusResponse,
         tags=["Retos"],
         summary="Desactivar un reto")
async def disable_challenge_endpoint(
    challenge_id: str = Path(..., description="ID del challenge a desactivar")
):
    try:
        result = disable_challenge(challenge_id)
        return {"success": True, "message": result.get("message")}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al desactivar el challenge: {str(e)}"
        )

@app.put("/retos/{challenge_id}/reactivar",
         response_model=ChallengeStatusResponse,
         tags=["Retos"],
         summary="Reactivar un reto")
async def reactivate_challenge_endpoint(
    challenge_id: str = Path(..., description="ID del challenge a reactivar")
):
    try:
        result = reactivate_challenge(challenge_id)
        return {"success": True, "message": result.get("message")}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al reactivar el challenge: {str(e)}"
        )


# Endpoint para obtener todas las recompensas y Crear nuevas recompensas

@app.post("/recompensas",
         response_model=RewardResponse,
         status_code=status.HTTP_201_CREATED,
         tags=["Recompensas"],
         summary="Crear una nueva recompensa")
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

@app.get("/recompensas",
        response_model=list[RewardResponse],
        tags=["Recompensas"],
        summary="Obtener todas las recompensas")
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

@app.post("/instancias-retos",
         response_model=ChallengeInstanceResponse,
         status_code=status.HTTP_201_CREATED,
         tags=["Instancias de Retos"],
         summary="Asignar un reto a un usuario")
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

@app.get("/usuarios/{user_id}/retos-asignados",
         response_model=UserAssignedChallengesResponse,
         tags=["Retos de Usuario"],
         summary="Obtener los retos asignados a un usuario")
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


@app.get("/usuarios/{user_id}/retos-completados",
         response_model=UserAssignedChallengesResponse,
         tags=["Retos de Usuario"],
         summary="Obtener los retos completados de un usuario")
def get_user_completed_challenges_endpoint(
    user_id: str = Path(..., description="ID del usuario para obtener sus challenges completados", min_length=1)
):
    try:
        challenges = get_user_completed_challenges(user_id)
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
            detail=f"Error al obtener challenges completados del usuario: {str(e)}"
        )


@app.post("/progreso-reto/{instance_id}",
         response_model=ChallengeProgressResponse,
         tags=["Instancias de Retos"],
         summary="Actualizar progreso en un reto")
async def progress_in_challenge_endpoint(
    instance_id: str = Path(..., description="ID de la instancia del challenge")
):
    try:
        result = update_challenge_progress(instance_id)
        return {"success": True, "message": result.get("message")}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar el progreso: {str(e)}"
        )


@app.get("/ranking/{user_id}",
         response_model=UserRankingResponse,
         tags=["Ranking"],
         summary="Obtener el ranking de un usuario")
async def get_user_ranking(
    user_id: str = Path(..., description="ID del usuario para consultar su ranking", min_length=1)
):
    try:
        rank = get_user_rank(user_id)
        return {
            "success": True,
            "user_id": user_id,
            "rank": rank
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el ranking del usuario: {str(e)}"
        )


@app.get("/ranking/ciudad/{user_id}",
         response_model=UserRankingResponse,
         tags=["Ranking"],
         summary="Obtener el ranking de un usuario por ciudad")
async def get_user_ranking_by_city(
    user_id: str = Path(..., description="ID del usuario para consultar su ranking por ciudad", min_length=1)
):
    try:
        rank = get_user_rank_by_city(user_id)
        return {
            "success": True,
            "user_id": user_id,
            "rank": rank,
            "message": "Ranking por ciudad obtenido exitosamente"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el ranking por ciudad: {str(e)}"
        )


@app.get("/ranking/departamento/{user_id}",
         response_model=UserRankingResponse,
         tags=["Ranking"],
         summary="Obtener el ranking de un usuario por departamento")
async def get_user_ranking_by_state(
    user_id: str = Path(..., description="ID del usuario para consultar su ranking por departamento", min_length=1)
):
    try:
        rank = get_user_rank_by_state(user_id)
        return {
            "success": True,
            "user_id": user_id,
            "rank": rank,
            "message": "Ranking por departamento obtenido exitosamente"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el ranking por departamento: {str(e)}"
        )


