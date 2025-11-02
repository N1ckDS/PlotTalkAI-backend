from fastapi import FastAPI
from db.database import DatabasePool
from src.llm.api.dialogue_endpoint import router as dialogue_router
from src.auth.api.auth_endpoint import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from src.db.api.db_endpoint import router as db_router
from src.healthz import router as healthz_router
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
# from contextlib import asynccontextmanager

load_dotenv(override=True)

# Настройка схемы безопасности для JWT
security_scheme = HTTPBearer()

app = FastAPI(
    title="Screenwriter Dialogue API",
    description="API для генерации диалогов с JWT аутентификацией",
    version="1.0.0",
    openapi_tags=[
        {"name": "Auth", "description": "Операции аутентификации"},
        {"name": "Dialogue", "description": "Генерация диалогов"},
        {"name": "Database", "description": "Операции с базой данных"},
        {"name": "Health", "description": "Проверка состояния сервиса"}
    ]
)

# Добавляем схему безопасности в OpenAPI
app.openapi_schema = None  # Сбрасываем кэш схемы

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Добавляем схему безопасности
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Введите ваш JWT токен"
        }
    }
    
    # Применяем схему безопасности к защищенным эндпоинтам
    for path in openapi_schema["paths"]:
        if path.startswith("/api/generate") or path.startswith("/api/users") or path.startswith("/api/get"):
            for method in openapi_schema["paths"][path]:
                if method in ["get", "post", "put", "delete"]:
                    openapi_schema["paths"][path][method]["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.on_event("startup")
async def startup_event():
    DatabasePool.init_pool()
    print("Pool connected")

@app.on_event("shutdown")
def shutdown_event():
    DatabasePool.close_all()
    print("Pool closed")
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://26.15.136.181:5173", "http://10.82.161.66:5173", "https://galeevarslandev.github.io/PlotTalkAI/",
                   "https://galeevarslandev.github.io/PlotTalkAI", "https://galeevarslandev.github.io/", "https://galeevarslandev.github.io"],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.include_router(dialogue_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(db_router, prefix="/api")
app.include_router(healthz_router, prefix="/api")

# @app.on_event("startup")
# async def startup():
#     # Инициализация пула при запуске
#     DatabasePool.init_pool()

# @app.on_event("shutdown")
# async def shutdown():
#     # Закрытие пула при остановке
#     DatabasePool.close_all()


    
