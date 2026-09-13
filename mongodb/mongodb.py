import os
import json
import pandas as pd
import psycopg
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()




def obter_client_mongo():
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(uri)
    db = client[os.getenv("MONGO_DB", "plataforma_edu_nosql")]
    return client, db



def carregar_dados_mongodb(diretorio_processados):
    print("[MONGO] Iniciando a persistência NoSQL...")
    with open(os.path.join(diretorio_processados, 'comentarios_avaliacoes_limpo.json'), 'r') as f:
        documentos = json.load(f)
        
    client, db = obter_client_mongo()
    colecao = db['comentarios_avaliacoes']
    
    try:
        # Limpar coleção antiga para garantir reprodutibilidade do script
        colecao.delete_many({})
        if documentos:
            resultado = colecao.insert_many(documentos)
            print(f"[MONGO] Sucesso! {len(resultado.inserted_ids)} documentos inseridos na coleção 'comentarios_avaliacoes'.")
    except Exception as e:
        print(f"[ERRO - MONGO] Falha na persistência NoSQL: {e}")
        raise e
    finally:
        client.close()