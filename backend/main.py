from backend.routers.envios import router as envios_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.importacao import router as importacao_router

app = FastAPI(
    title="Sistema de Rastreamento Logístico",
    description="API para acompanhamento de envios",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(importacao_router)

app.include_router(envios_router)
@app.get("/")
def home():
    return {
        "sistema": "Rastreamento Logístico",
        "status": "online",
        "versao": "1.0.0"
    }