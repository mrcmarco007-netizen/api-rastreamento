from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.database.database import Base

class Envio(Base):
    __tablename__ = "envios"

    id = Column(Integer, primary_key=True, index=True)
    transportadora = Column(String, index=True)
    pedido = Column(String, index=True)
    nota_fiscal = Column(String, index=True)
    codigo_rastreio = Column(String, index=True)
    status_atual = Column(String)
    data_envio = Column(DateTime)
    previsao_entrega = Column(DateTime)
    criado_em = Column(DateTime, default=datetime.now)