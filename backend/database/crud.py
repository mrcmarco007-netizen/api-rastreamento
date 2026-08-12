from sqlalchemy.orm import Session
from backend.models.envio import Envio
from datetime import datetime

def salvar_envios_correios(db: Session, df):
    registros_salvos = 0
    
    # Percorre cada linha da planilha
    for index, row in df.iterrows():
        # Verifica se o rastreio já existe no banco
        rastreio_existente = db.query(Envio).filter(Envio.codigo_rastreio == row['NUMERO DO OBJETO']).first()
        
        # Converte as datas
        try:
            previsao = datetime.strptime(str(row['DATA PREVISTA']), '%d/%m/%Y %H:%M:%S')
        except:
            previsao = None
            
        if not rastreio_existente:
            novo_envio = Envio(
                transportadora="Correios",
                codigo_rastreio=row['NUMERO DO OBJETO'],
                status_atual=row['ULTIMO STATUS'],
                previsao_entrega=previsao
            )
            db.add(novo_envio)
            registros_salvos += 1
            
    db.commit()
    return registros_salvos

def salvar_envios_aviat(db: Session, df):
    registros_salvos = 0
    for index, row in df.iterrows():
        rastreio = str(row.get('N° CT-e', ''))
        
        if rastreio and rastreio != 'nan':
            rastreio_existente = db.query(Envio).filter(Envio.codigo_rastreio == rastreio).first()
            
            try:
                previsao = datetime.strptime(str(row.get('Prazo Entrega', '')), '%d/%m/%Y %H:%M')
            except:
                previsao = None
                
            if not rastreio_existente:
                novo_envio = Envio(
                    transportadora="Aviat",
                    pedido=str(row.get('N° Referência', '')),
                    nota_fiscal=str(row.get('Notas Fiscais', '')).replace('=', '').replace('"', ''),
                    codigo_rastreio=rastreio,
                    status_atual=str(row.get('Última ocorrência', '')),
                    previsao_entrega=previsao
                )
                db.add(novo_envio)
                registros_salvos += 1
                
    db.commit()
    return registros_salvos

def salvar_envios_expedicao(db: Session, df):
    registros_salvos = 0
    for index, row in df.iterrows():
        rastreio = str(row.get('RASTREIO', ''))
        
        if rastreio and rastreio != 'nan':
            rastreio_existente = db.query(Envio).filter(Envio.codigo_rastreio == rastreio).first()
            
            try:
                data_envio = datetime.strptime(str(row.get('DATA DA COLETA', '')), '%Y-%m-%d %H:%M:%S')
            except:
                data_envio = None
                
            if rastreio_existente:
                rastreio_existente.pedido = str(row.get('PEDIDO', ''))
                rastreio_existente.nota_fiscal = str(row.get('NOTA FISCAL', ''))
                if data_envio:
                    rastreio_existente.data_envio = data_envio
                registros_salvos += 1
            else:
                novo_envio = Envio(
                    transportadora="Correios",
                    pedido=str(row.get('PEDIDO', '')),
                    nota_fiscal=str(row.get('NOTA FISCAL', '')),
                    codigo_rastreio=rastreio,
                    status_atual=str(row.get('STATUS', '')),
                    data_envio=data_envio
                )
                db.add(novo_envio)
                registros_salvos += 1
                
    db.commit()
    return registros_salvos