# 🏆 API de Sistema de Recompensas y Challenges

Una API RESTful desarrollada con **FastAPI** y **Firebase** para gestionar un sistema de recompensas, challenges y puntos de usuarios.

## 📋 Descripción

Este proyecto implementa un sistema completo de gamificación que permite:
- Gestionar usuarios y sus puntos
- Crear y administrar challenges
- Asignar recompensas
- Asignar challenges a usuarios específicos
- Rastrear el progreso de los usuarios

## 🚀 Tecnologías Utilizadas

- **FastAPI** - Framework web moderno y rápido para APIs
- **Firebase Firestore** - Base de datos NoSQL en la nube
- **Pydantic** - Validación de datos y serialización
- **Uvicorn** - Servidor ASGI para FastAPI
- **Python 3.12+** - Lenguaje de programación

## 📁 Estructura del Proyecto

```
Prueba Tecnica/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal FastAPI
│   ├── crud.py              # Operaciones de base de datos
│   ├── schemas.py           # Modelos Pydantic
│   ├── utils.py             # Utilidades
│   └── firebase-key.json    # Credenciales de Firebase
├── entorno/                 # Entorno virtual
├── .gitignore
└── README.md
```

## 🛠️ Instalación y Configuración

### Prerrequisitos

- Python 3.12 o superior
- Cuenta de Firebase con Firestore habilitado

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd "Prueba Tecnica"
   ```

2. **Activar el entorno virtual**
   ```bash
   # Windows
   .\entorno\Scripts\Activate.ps1
   
   # Linux/Mac
   source entorno/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install fastapi uvicorn firebase-admin pydantic
   ```

4. **Configurar Firebase**
   - Descarga tu archivo de credenciales de Firebase
   - Reemplaza `app/firebase-key.json` con tu archivo de credenciales

5. **Ejecutar la aplicación**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📚 Endpoints de la API

### 👥 Usuarios

#### Obtener todos los usuarios
```http
GET /users
```

#### Obtener puntos de un usuario
```http
GET /users/{user_id}/points
```

#### Inicializar puntos de un usuario
```http
POST /users/{user_id}/points/init
```

### 🎯 Challenges

#### Crear un nuevo challenge
```http
POST /challenges
Content-Type: application/json

{
  "name": "Challenge de Ejemplo",
  "description": "Descripción del challenge",
  "max_limit": 100,
  "reward_id": "reward_123",
  "max_users": 50,
  "status": "active",
  "max_date": "2024-12-31T23:59:59"
}
```

#### Obtener todos los challenges
```http
GET /challenges
```

### 🏅 Recompensas

#### Crear una nueva recompensa
```http
POST /rewards
Content-Type: application/json

{
  "type": "points",
  "value": "100",
  "metadata": {
    "description": "Recompensa por completar challenge"
  }
}
```

#### Obtener todas las recompensas
```http
GET /rewards
```

### 📋 Instancias de Challenges

#### Asignar un challenge a un usuario
```http
POST /challenge-instances
Content-Type: application/json

{
  "user_id": "user_123",
  "challenge_id": "challenge_456"
}
```

#### Obtener challenges asignados a un usuario
```http
GET /users/{user_id}/assigned-challenges
```

### 🏆 Ranking

#### Obtener ranking global de un usuario
Devuelve la posición de un usuario en el ranking global basado en sus puntos.
```http
GET /ranking/{user_id}
```

#### Obtener ranking de un usuario por ciudad
Devuelve la posición de un usuario en el ranking, compitiendo solo contra usuarios de su misma ciudad.
```http
GET /ranking/ciudad/{user_id}
```

#### Obtener ranking de un usuario por departamento
Devuelve la posición de un usuario en el ranking, compitiendo solo contra usuarios de su mismo departamento (`state`).
```http
GET /ranking/departamento/{user_id}
```

## 🔧 Modelos de Datos

### User
```python
{
  "user_id": "string",
  "email": "string",
  "name": "string"
}
```

### Challenge
```python
{
  "challenge_id": "string",
  "name": "string",
  "description": "string",
  "max_limit": "integer",
  "reward_id": "string",
  "max_users": "integer",
  "status": "active|inactive|completed",
  "max_date": "datetime",
  "date_creation": "datetime"
}
```

### Reward
```python
{
  "reward_id": "string",
  "type": "string",
  "value": "string",
  "metadata": "object",
  "created_at": "datetime"
}
```

### ChallengeInstance
```python
{
  "instance_id": "string",
  "user_id": "string",
  "challenge_id": "string",
  "progress": "integer",
  "completed": "boolean",
  "date_started": "datetime"
}
```

### UserRankingResponse
```python
{
  "success": "boolean",
  "rank": "integer",
  "user_id": "string",
  "message": "string"
}
```

## 🌐 Documentación de la API

Una vez que la aplicación esté ejecutándose, puedes acceder a:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🚀 Ejecución

```bash
# Activar entorno virtual
.\entorno\Scripts\Activate.ps1

# Ejecutar la aplicación
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
La aplicación estará disponible en `http://localhost:8000`

## 🔒 Configuración de Seguridad

- Asegúrate de que `firebase-key.json` esté incluido en `.gitignore`
- Nunca subas credenciales de Firebase al repositorio
- Configura las reglas de seguridad apropiadas en Firebase Firestore

## 📝 Notas de Desarrollo

- La aplicación utiliza Firebase Firestore como base de datos
- Todos los endpoints incluyen manejo de errores robusto
- Los datos se validan usando Pydantic models
- La API incluye documentación automática con Swagger

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

Desarrollado como parte de una prueba técnica para un sistema de recompensas y gamificación.

---

**¡Disfruta usando la API de Sistema de Recompensas! 🎉**


