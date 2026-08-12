from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal
from backend.models.envio import Envio

router = APIRouter(prefix="/envios", tags=["Envios"])

# Função para conectar ao banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def listar_envios(db: Session = Depends(get_db)):
    # Busca todos os envios no banco de dados
    envios = db.query(Envio).all()
    
    # Vamos contar os totais para o nosso futuro painel
    total = len(envios)
    entregues = sum(1 for e in envios if e.status_atual and "entregue" in e.status_atual.lower())
    
    return {
        "indicadores": {
            "total_envios": total,
            "entregues": entregues,
            "em_andamento": total - entregues
        },
        "lista_pedidos": envios
    }