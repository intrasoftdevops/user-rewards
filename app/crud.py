import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pytz
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
        "last_updated": datetime.datetime.now()
    })


def create_challenge(challenge_data: dict) -> dict:
    db = firestore.client()
    
    # Validar que el reward_id exista (implementación opcional)
    # if not reward_exists(challenge_data["reward_id"]):
    #     raise HTTPException(status_code=400, detail="El reward_id no existe")
    
    challenge_ref = db.collection("challenges").document()
    challenge_id = challenge_ref.id
    
    # Usamos datetime.now() para la respuesta, pero SERVER_TIMESTAMP para Firestore
    now = datetime.now()

    response_data = challenge_data.copy()
    response_data.update({
        "challenge_id": challenge_id,
        "date_creation": now,
        "status": challenge_data.get("status", "active")
    })

    firestore_data = challenge_data.copy()
    firestore_data.update({
        "challenge_id": challenge_id,
        "date_creation": firestore.SERVER_TIMESTAMP,
        "status": challenge_data.get("status", "active")
    })
    
    try:
        challenge_ref.set(firestore_data)

        response_data = challenge_data.copy()
        response_data.update({
            "challenge_id": challenge_id,
            "date_creation": datetime.now(pytz.timezone('America/Bogota')),
            "status": challenge_data.get("status", "active")
        })
        
        return response_data
            
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

def disable_expired_challenges() -> dict:
    db = firestore.client()
    now = datetime.now(pytz.utc)
    
    # Query for active challenges where max_date has passed
    expired_challenges_query = db.collection("challenges") \
        .where("status", "==", "active") \
        .where("max_date", "<", now)
        
    challenges_to_disable = list(expired_challenges_query.stream())
    
    if not challenges_to_disable:
        return {"disabled_count": 0, "message": "No hay challenges expirados para desactivar."}
        
    # Use a batch to update all expired challenges at once
    batch = db.batch()
    for challenge_doc in challenges_to_disable:
        batch.update(challenge_doc.reference, {"status": "disabled"})
        
    try:
        batch.commit()
        disabled_count = len(challenges_to_disable)
        return {"disabled_count": disabled_count, "message": f"{disabled_count} challenge(s) han sido desactivados."}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al desactivar challenges expirados: {str(e)}"
        )

def disable_challenge(challenge_id: str) -> dict:
    db = firestore.client()
    challenge_ref = db.collection("challenges").document(challenge_id)

    # Verificar que el challenge existe
    challenge_doc = challenge_ref.get()
    if not challenge_doc.exists:
        raise HTTPException(status_code=404, detail="Challenge no encontrado")

    challenge_data = challenge_doc.to_dict()
    if challenge_data.get("status") == "disabled":
        raise HTTPException(status_code=400, detail="El challenge ya se estaba desactivado")

    try:
        challenge_ref.update({"status": "disabled"})
        return {"message": "Challenge desactivado exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al desactivar el challenge: {str(e)}"
        )

def reactivate_challenge(challenge_id: str) -> dict:
    db = firestore.client()
    challenge_ref = db.collection("challenges").document(challenge_id)

    # Verificar que el challenge existe
    challenge_doc = challenge_ref.get()
    if not challenge_doc.exists:
        raise HTTPException(status_code=404, detail="Challenge no encontrado")

    challenge_data = challenge_doc.to_dict()
    if challenge_data.get("status") == "active":
        raise HTTPException(status_code=400, detail="El challenge ya se estaba activo")

    try:
        challenge_ref.update({"status": "active"})
        return {"message": "Challenge reactivado exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al reactivar el challenge: {str(e)}"
        )


# Crear Recompensas 

def create_reward(reward_data: dict) -> dict:
    db = firestore.client()
    reward_ref = db.collection("rewards").document()
    reward_id = reward_ref.id
    
    firestore_data = reward_data.copy()
    firestore_data.update({
        "reward_id": reward_id,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    
    try:
        reward_ref.set(firestore_data)

        response_data = reward_data.copy()
        response_data["reward_id"] = reward_id
        response_data["created_at"] = datetime.now(pytz.timezone('America/Bogota'))
        
        return response_data
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear recompensa: {str(e)}"
        )


# Obtener las listas de Recompensas

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
    challenge_doc = db.collection("challenges").document(instance_data["challenge_id"]).get()
    if not challenge_doc.exists:
        raise HTTPException(status_code=404, detail="Challenge no encontrado")
    
    challenge_data = challenge_doc.to_dict()
    
    # Verificar que el challenge esté activo
    if challenge_data.get("status") != "active":
        raise HTTPException(status_code=400, detail="El challenge no se encuentra activo")

    max_limit = challenge_data.get("max_limit", 0)

    # Crear la instancia
    instance_ref = db.collection("challenge_instances").document()
    instance_id = instance_ref.id
    
    # Usamos datetime.now() para la respuesta, pero SERVER_TIMESTAMP para Firestore
    now = datetime.now()
    
    instance_data.update({
        "instance_id": instance_id,
        "progress": max_limit,
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

        # Obtener instancias del usuario que no estén completadas
        instances = db.collection("challenge_instances")\
                    .where("user_id", "==", user_id)\
                    .where("completed", "==", False)\
                    .stream()
        
        challenges = []
        for instance in instances:
            instance_data = instance.to_dict()
            # Obtener detalles del challenge
            challenge_ref = db.collection("challenges").document(instance_data["challenge_id"])
            challenge_doc = challenge_ref.get()
            
            if challenge_doc.exists:
                challenge_data = challenge_doc.to_dict()
                # Asegurarse de que el challenge esté activo
                if challenge_data.get("status") == "active":
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


# Challenge Instances completados por usuario

def get_user_completed_challenges(user_id: str) -> list:
    db = firestore.client()
    try:
        # Verificar que el usuario existe
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Obtener instancias del usuario que estén completadas
        instances = db.collection("challenge_instances")\
                    .where("user_id", "==", user_id)\
                    .where("completed", "==", True)\
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
            detail=f"Error al obtener challenges completados del usuario: {str(e)}"
        )

def update_challenge_progress(instance_id: str) -> dict:
    db = firestore.client()
    instance_ref = db.collection("challenge_instances").document(instance_id)

    @firestore.transactional
    def update_in_transaction(transaction, instance_ref):
        # --- 1. Realizar todas las lecturas primero ---
        instance_doc = instance_ref.get(transaction=transaction)
        if not instance_doc.exists:
            return {'error': 'not_found', 'message': 'Instancia de challenge no encontrada'}
        
        instance_data = instance_doc.to_dict()

        challenge_id = instance_data.get('challenge_id')
        challenge_ref = db.collection('challenges').document(challenge_id)
        challenge_doc = challenge_ref.get(transaction=transaction)
        
        if not challenge_doc.exists:
            return {'error': 'challenge_not_found', 'message': 'Challenge asociado no encontrado'}
        
        challenge_data = challenge_doc.to_dict()
        
        user_id = instance_data.get('user_id')
        points_ref = None
        points_doc = None
        if user_id:
            points_ref = db.collection('user_points').document(user_id)
            points_doc = points_ref.get(transaction=transaction)

        # --- 2. Realizar todas las validaciones ---
        if instance_data.get('completed', False):
            return {'error': 'already_completed', 'message': 'El challenge ya esta completado'}

        if challenge_data.get('status') != 'active':
            return {'error': 'challenge_expired', 'message': 'El challenge ya expiro'}

        # --- 3. Realizar todas las escrituras al final ---
        new_progress = instance_data.get('progress', 0) - 1
        
        if new_progress <= 0:
            transaction.update(instance_ref, {
                'progress': 0,
                'completed': True
            })

            points_to_add = challenge_data.get('puntos', 0)
            if user_id and points_to_add > 0 and points_ref:
                if points_doc and points_doc.exists:
                    current_points = points_doc.to_dict().get('points', 0)
                    new_total_points = current_points + points_to_add
                    transaction.update(points_ref, {
                        'points': new_total_points,
                        'last_updated': firestore.SERVER_TIMESTAMP
                    })
                else:
                    transaction.set(points_ref, {
                        'user_id': user_id,
                        'points': points_to_add,
                        'last_updated': firestore.SERVER_TIMESTAMP
                    })
            
            return {'status': 'completed', 'message': 'completaste el challenge'}
        else:
            transaction.update(instance_ref, {
                'progress': new_progress
            })
            return {'status': 'updated', 'message': 'Progreso actualizado'}

    transaction = db.transaction()
    result = update_in_transaction(transaction, instance_ref)

    if 'error' in result:
        status_code = 404 if result['error'] in ['not_found', 'challenge_not_found'] else 400
        raise HTTPException(status_code=status_code, detail=result['message'])
    
    return result