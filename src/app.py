from fastapi import FastAPI
from db.database import DatabasePool
from src.llm.api.dialogue_endpoint import router as dialogue_router
from src.auth.api.auth_endpoint import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from src.db.api.db_endpoint import router as db_router
from src.healthz import router as healthz_router
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv(override=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация пула при запуске
    DatabasePool.init_pool()
    print("Pool connected")

    yield
    # Закрытие пула при остановке
    DatabasePool.close_all()
    
app = FastAPI(title="Screenwriter Dialogue API", lifespan=lifespan)

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


    
