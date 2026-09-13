
import os

import pandas as pd
import psycopg
from dotenv import load_dotenv

load_dotenv()

def obter_conexao_postgres():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "plataforma_edu"),
        user=os.getenv("POSTGRES_USER", "yuri"),
        password=os.getenv("POSTGRES_PASSWORD")
    )



def carregar_dados_postgres(diretorio_processados):
    print("[POSTGRES] Iniciando a persistência relacional em lote...")
    
    # Carregando os datasets processados no Pandas
    df_cat = pd.read_csv(os.path.join(diretorio_processados, 'catalogo_conteudos_limpo.csv'))
    df_int = pd.read_json(os.path.join(diretorio_processados, 'interacoes_usuarios_limpo.json'))
    
    # Extrair os IDs de usuários únicos presentes nas fontes para preencher a tabela de usuários
    usuarios_unicos = set(df_int['usuario_id'].unique())
    if os.path.exists(os.path.join(diretorio_processados, 'comentarios_avaliacoes_limpo.json')):
        df_com_temp = pd.read_json(os.path.join(diretorio_processados, 'comentarios_avaliacoes_limpo.json'))
        usuarios_unicos.update(df_com_temp['usuario_id'].unique())

    conn = obter_conexao_postgres()
    try:
        with conn.cursor() as cur:
            # 1. Carga de Usuários
            for user_id in usuarios_unicos:
                cur.execute(
                    "INSERT INTO usuario (usuario_id) VALUES (%s) ON CONFLICT (usuario_id) DO NOTHING",
                    (int(user_id),)
                )
            
            # 2. Carga e mapeamento de Categorias dinamicamente
            categorias_unicas = df_cat['categoria'].unique()
            mapa_categorias = {}
            for cat_nome in categorias_unicas:
                cur.execute(
                    "INSERT INTO categoria (nome) VALUES (%s) ON CONFLICT (nome) DO UPDATE SET nome=EXCLUDED.nome RETURNING categoria_id",
                    (str(cat_nome),)
                )
                mapa_categorias[cat_nome] = cur.fetchone()[0]

            # 3. Carga de Conteúdos
            for _, row in df_cat.iterrows():
                cur.execute(
                    """INSERT INTO conteudo (conteudo_id, titulo, tipo, categoria_id, nivel, carga_horaria_min, data_publicacao, descricao, autor)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (conteudo_id) DO NOTHING""",
                    (
                        int(row['conteudo_id']),
                        str(row['titulo']),
                        str(row['tipo']),
                        mapa_categorias[row['categoria']],
                        str(row['nivel']),
                        int(row['carga_horaria_min']),
                        str(row['data_publicacao']),
                        str(row['descricao']) if pd.notna(row['descricao']) else None,
                        str(row['autor']) if pd.notna(row['autor']) else None
                    )
                )
            
            # 4. Carga de Interações utilizando transação em bloco
            for _, row in df_int.iterrows():
                # Converter avaliacao_atribuida para None caso seja NaN
                val_avaliacao = int(row['avaliacao_atribuida']) if pd.notna(row['avaliacao_atribuida']) else None
                cur.execute(
                    """INSERT INTO interacao (usuario_id, conteudo_id, tipo_interacao, data_hora, tempo_consumido, percentual_conclusao, avaliacao_atribuida)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        int(row['usuario_id']),
                        int(row['conteudo_id']),
                        str(row['tipo_interacao']),
                        str(row['data_hora']),
                        int(row['tempo_consumido']),
                        float(row['percentual_conclusao']),
                        val_avaliacao
                    )
                )
        # Finaliza e consolida a transação da carga
        conn.commit()
        print(f"[POSTGRES] Sucesso! Carga efetuada. {len(df_cat)} conteúdos e {len(df_int)} interações salvas.")
    except Exception as e:
        conn.rollback()
        print(f"[ERRO - POSTGRES] Falha na carga. Transação revertida: {e}")
        raise e
    finally:
        conn.close()


