import pandas as pd
import os

def processar_arquivo(caminho_arquivo: str):
    extensao = os.path.splitext(caminho_arquivo)[1].lower()
    
    try:
        if extensao == '.csv':
            # Espia a primeira linha do arquivo para descobrir como ler
            with open(caminho_arquivo, 'r', encoding='latin1') as f:
                primeira_linha = f.readline()
            
            # Se for Correios, pula as 5 linhas iniciais do relatório deles
            if "Correios" in primeira_linha:
                df = pd.read_csv(caminho_arquivo, sep=';', encoding='latin1', skiprows=5)
            else:
                # Se for a Aviat, lê normalmente a partir da primeira linha
                df = pd.read_csv(caminho_arquivo, sep=';', encoding='latin1')
        else:
            df = pd.read_excel(caminho_arquivo)
            
        colunas = df.columns.tolist()
        colunas_norm = " ".join([str(c).lower() for c in colunas])
        
        tipo_arquivo = "Desconhecido"
        
        # Identificação pelas colunas
        if "ultimo evento" in colunas_norm or "numero do objeto" in colunas_norm:
            tipo_arquivo = "Correios"
        elif "n° ct-e" in colunas_norm or "ct-e" in colunas_norm:
            tipo_arquivo = "Aviat"
        elif "ordem de serviço" in colunas_norm or "natureza da operação" in colunas_norm:
            tipo_arquivo = "Expedição"
            
        return {
            "tipo_identificado": tipo_arquivo,
            "total_linhas_lidas": len(df),
            "colunas_encontradas": colunas[:5],
            "dataframe": df
        }
    except Exception as e:
        return {"erro": str(e)}