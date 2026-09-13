# src/main.py
import yaml
import json
import psycopg
from ingestao.ingestao import processar_pipeline
from src.bancos import carregar_dados_postgres, obter_conexao_postgres
from src.ia import MotorIA
from recomendacao.recomendacao import gerar_recomendacoes_usuario
from mongodb.mongodb import carregar_dados_mongodb

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
    print("[INFO] ====================================================")
    print("[INFO] Iniciando Pipeline Completo de DataOps + IA...")
    print("[INFO] ====================================================")
    
    config = carregar_configuracao()
    dir_proc = config['arquivos']['diretorio_processados']
    
    # 1. Ingestão
    resumo = processar_pipeline(config)
    
    # 2. Carga nos Bancos
    try:
        carregar_dados_postgres(dir_proc)
        carregar_dados_mongodb(dir_proc)
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha na persistência: {e}")
        return

    # 3. Geração de Embeddings
    try:
        motor_ia = MotorIA()
        motor_ia.gerar_embeddings_catalogo(obter_conexao_postgres)
        
        frase_teste = "Quero aprender os fundamentos de banco de dados para inteligência artificial."
        resultados_busca = motor_ia.buscar_por_similaridade(obter_conexao_postgres, frase_teste, limite=1)
        print(f"\n[OK] Busca Semântica testada para: '{frase_teste}'")
        print(json.dumps(resultados_busca, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"[ERRO] Falha na etapa de IA: {e}")

        
        
    
    # 4. Geração de Recomendações
    try:
        id_usuario_teste = 53
        recs =gerar_recomendacoes_usuario(id_usuario_teste)
        print(f"\nTop conteúdos recomendados para o Usuário {id_usuario_teste}:")
        print(json.dumps(recs, indent=4, ensure_ascii=False))
        print("\n[OK] Recomendações salvas com sucesso no PostgreSQL!")
    except Exception as e:
        print(f"[ERRO] Falha ao gerar recomendações: {e}")

    # 5. Criação Analítica das tabelas do Apache Superset (RF12)
    aplicar_views_analiticas()
    print("\n[SUCESSO] Todo o ecossistema backend está pronto e operacional!")

if __name__ == '__main__':
    main()
