import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from fastapi import HTTPException

def get_user_points(user_id: str) -> dict:
    db = firestore.client()
    doc_ref = db.collection("user_points").document(user_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail=f"El usuario con ID {user_id} no tiene registro de puntos"
        )
    
    return doc.to_dict()

def init_user_points(user_id: str):
    db = firestore.client()
    doc_ref = db.collection("user_points").document(user_id)
    doc_ref.set({
        "user_id": user_id,
        "points": 0,
        "last_updated": firestore.SERVER_TIMESTAMP
    })


def create_challenge(challenge_data: dict) -> dict:
    db = firestore.client()
    
    # Validar que el reward_id exista (implementación opcional)
    # if not reward_exists(challenge_data["reward_id"]):
    #     raise HTTPException(status_code=400, detail="El reward_id no existe")
    
    challenge_ref = db.collection("challenges").document()
    challenge_id = challenge_ref.id
    
    challenge_data.update({
        "challenge_id": challenge_id,
        "date_creation": firestore.SERVER_TIMESTAMP,
        "status": challenge_data.get("status", "active")
    })
    
    try:
        challenge_ref.set(challenge_data)
        return challenge_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear challenge: {str(e)}"
        )

def reward_exists(reward_id: str) -> bool:
    """Validar que el reward exista en otra colección"""
    db = firestore.client()
    # reward_ref = db.collection("rewards").document(reward_id).get()
    # return reward_ref.exists
    return True  # Implementación temporal

# traer todos los challenges

def get_all_challenges() -> list:
    db = firestore.client()
    try:
        challenges_ref = db.collection("challenges").stream()
        return [doc.to_dict() for doc in challenges_ref]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener challenges: {str(e)}"
        )


# Crear Recompensas y Obtener las listas de Recompensas

def create_reward(reward_data: dict) -> dict:
    db = firestore.client()
    reward_ref = db.collection("rewards").document()
    reward_id = reward_ref.id
    
    reward_data.update({
        "reward_id": reward_id,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    
    try:
        reward_ref.set(reward_data)
        return reward_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear recompensa: {str(e)}"
        )

def get_all_rewards() -> list:
    db = firestore.client()
    try:
        rewards_ref = db.collection("rewards").stream()
        return [doc.to_dict() for doc in rewards_ref]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener recompensas: {str(e)}"
        )


# Crear Instancias de Challenge 

def assign_challenge_to_user(instance_data: dict) -> dict:
    db = firestore.client()
    
    # Verificar que el usuario existe
    user_ref = db.collection("users").document(instance_data["user_id"]).get()
    if not user_ref.exists:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar que el challenge existe
    challenge_ref = db.collection("challenges").document(instance_data["challenge_id"]).get()
    if not challenge_ref.exists:
        raise HTTPException(status_code=404, detail="Challenge no encontrado")
    
    # Crear la instancia
    instance_ref = db.collection("challenge_instances").document()
    instance_id = instance_ref.id
    
    # Usamos datetime.now() para la respuesta, pero SERVER_TIMESTAMP para Firestore
    now = datetime.now()
    
    instance_data.update({
        "instance_id": instance_id,
        "progress": 0,
        "completed": False,
        "date_started": now  # Usamos datetime.now() para la respuesta
    })
    
    try:
        # Aquí usamos SERVER_TIMESTAMP para Firestore
        firestore_data = instance_data.copy()
        firestore_data["date_started"] = firestore.SERVER_TIMESTAMP
        instance_ref.set(firestore_data)
        
        return instance_data  # Devuelve los datos con datetime.now()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al asignar challenge: {str(e)}"
        )


# Challenge Instances por usuario

def get_user_assigned_challenges(user_id: str) -> list:
    db = firestore.client()
    try:
        # Verificar que el usuario existe
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Obtener instancias del usuario
        instances = db.collection("challenge_instances")\
                    .where("user_id", "==", user_id)\
                    .stream()
        
        challenges = []
        for instance in instances:
            instance_data = instance.to_dict()
            # Obtener detalles del challenge
            challenge_ref = db.collection("challenges").document(instance_data["challenge_id"])
            challenge_doc = challenge_ref.get()
            
            if challenge_doc.exists:
                challenge_data = challenge_doc.to_dict()
                merged_data = {
                    "instance_id": instance.id,
                    **instance_data,
                    **challenge_data
                }
                challenges.append(merged_data)
        
        return challenges
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener challenges del usuario: {str(e)}"
        )