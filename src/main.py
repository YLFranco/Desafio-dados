# src/main.py
import json

import yaml

from ingestao.ingestao import processar_pipeline
from mongodb.mongodb import carregar_dados_mongodb, obter_client_mongo, consultar_mongodb
from recomendacao.recomendacao import gerar_recomendacoes_usuario
from src.postgres import carregar_dados_postgres, obter_conexao_postgres
from src.busca import MotorIA


def carregar_configuracao():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def aplicar_views_analiticas():
    print("[POSTGRES] Aplicando Views de Métricas e KPIs...")
    conn = obter_conexao_postgres()
    try:
        with open('sql/consultas.sql', 'r') as f:
            sql_script = f.read()
        with conn.cursor() as cur:
            cur.execute(sql_script)
        conn.commit()
        print("[POSTGRES] Views e KPIs estruturados com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"[ERRO] Falha ao injetar script de consultas: {e}")
    finally:
        conn.close()

def main():
    print(" ====================================================")
    print("[INFO] Iniciando Pipeline")
    print("====================================================")
    
    config = carregar_configuracao()
    dir_proc = config['arquivos']['diretorio_processados']
    
    
    resumo = processar_pipeline(config)
    
    
    print("\n=================== RESUMO DA INGESTÃO ===================")
    print(json.dumps(resumo, indent=4, ensure_ascii=False))
    print("==========================================================\n")
    
   
    try:
        carregar_dados_postgres(dir_proc)
        carregar_dados_mongodb(dir_proc)
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha na persistência: {e}")
        return

    consultar_mongodb()
    
    try:
        motor_ia = MotorIA()
        motor_ia.gerar_embeddings_catalogo(obter_conexao_postgres)
        
        frase_teste = "Quero aprender os fundamentos de banco de dados para inteligência artificial."
        resultados_busca = motor_ia.buscar_por_similaridade(obter_conexao_postgres, frase_teste, limite=1)
        print(f"\n[INFO] Busca Semântica testada para: '{frase_teste}'")
        print(json.dumps(resultados_busca, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"[ERRO] Falha na etapa de IA: {e}")
    
    try:
        id_usuario_teste = 53
        recs =gerar_recomendacoes_usuario(id_usuario_teste)
        print(f"\nTop conteúdos recomendados para o Usuário {id_usuario_teste}:")
        print(json.dumps(recs, indent=4, ensure_ascii=False))
        print("\n[INFO] Recomendações salvas com sucesso no PostgreSQL!")
    except Exception as e:
        print(f"[ERRO] Falha ao gerar recomendações: {e}")

    
    aplicar_views_analiticas()
    print("\n Todo o ecossistema backend está pronto e operacional!")

if __name__ == '__main__':
    main()
