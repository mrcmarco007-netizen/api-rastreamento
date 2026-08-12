from backend.database.crud import salvar_envios_correios, salvar_envios_aviat, salvar_envios_expedicao
from fastapi import APIRouter, UploadFile, File, Depends
from pathlib import Path
import shutil
from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.services.identificador import processar_arquivo
from backend.database.crud import salvar_envios_correios

router = APIRouter(prefix="/importacao", tags=["Importação"])
UPLOAD_DIR = Path("data/uploads")

# Função para conectar ao banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload")
async def upload_arquivo(arquivo: UploadFile = File(...), db: Session = Depends(get_db)):
    caminho_destino = UPLOAD_DIR / arquivo.filename
    with open(caminho_destino, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)
        
    resultado_analise = processar_arquivo(str(caminho_destino))
    
    # Se for Correios, vamos salvar no banco!
    resultado_analise = processar_arquivo(str(caminho_destino))
    
    registros_inseridos = 0
    if "dataframe" in resultado_analise:
        df = resultado_analise.pop("dataframe") 
        
        if resultado_analise.get("tipo_identificado") == "Correios":
            registros_inseridos = salvar_envios_correios(db, df)
        elif resultado_analise.get("tipo_identificado") == "Aviat":
            registros_inseridos = salvar_envios_aviat(db, df)
        elif resultado_analise.get("tipo_identificado") == "Expedição":
            registros_inseridos = salvar_envios_expedicao(db, df)
            
        resultado_analise["registros_salvos_no_banco"] = registros_inseridos
    
    return {
        "status": "sucesso", 
        "analise": resultado_analise
    }