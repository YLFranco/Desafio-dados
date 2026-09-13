# src/ia.py
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer


class MotorIA:
    def __init__(self):
        self.nome_modelo = 'sentence-transformers/all-MiniLM-L6-v2' # (anotar para ver se esse modelo impacta em algo)
        print(f"[IA] Carregando modelo de embeddings {self.nome_modelo}...")
        self.model = SentenceTransformer(self.nome_modelo)
        
    def gerar_embeddings_catalogo(self, conexao_func):
        """RF08 - Gera embeddings para cada conteúdo que ainda não possui vetor armazenado"""
        print("[IA] Iniciando geração de embeddings para o catálogo de conteúdos...")
        
        conn = conexao_func()
        register_vector(conn) # Habilita o suporte a vetores no driver do psycopg
        
        try:
            with conn.cursor() as cur:
                # Busca conteúdos que ainda estão com o campo embedding nulo
                cur.execute("SELECT conteudo_id, titulo, descricao FROM conteudo WHERE embedding IS NULL")
                registros = cur.fetchall()
                
                if not registros:
                    print("[IA] Todos os conteúdos já possuem embeddings gerados. Pulando etapa.")
                    return
                
                print(f"[IA] Encontrados {len(registros)} conteúdos para vetorizar.")
                
                for conteudo_id, titulo, descricao in registros:
                    # Preparação do texto combinando Título + Descrição (conforme exigido pelo RF08)
                    texto_completo = f"{titulo}. {descricao if descricao else ''}"
                    
                    # Gerando o vetor numérico usando a rede neural
                    embedding = self.model.encode(texto_completo).tolist()
                    
                    # Atualizando o registro diretamente no PostgreSQL usando pgvector
                    cur.execute(
                        "UPDATE conteudo SET embedding = %s WHERE conteudo_id = %s",
                        (embedding, conteudo_id)
                    )
            conn.commit()
            print("[IA] Geração e armazenamento de embeddings finalizados com sucesso!")
        except Exception as e:
            conn.rollback()
            print(f"[ERRO - IA] Erro ao salvar embeddings no banco: {e}")
            raise e
        finally:
            conn.close()

    def buscar_por_similaridade(self, conexao_func, consulta_texto, limite=3):
        """RF09 - Realiza busca por similaridade semântica usando distância cosseno (<=>)"""
        # Converte a frase digitada pelo usuário em linguagem natural para um vetor
        vetor_consulta = self.model.encode(consulta_texto).tolist()
        
        conn = conexao_func()
        register_vector(conn)
        
        resultados = []
        try:
            with conn.cursor() as cur:
                # O cast %s::vector resolve o erro informando ao PostgreSQL o formato correto
                cur.execute(
                    """SELECT c.conteudo_id, c.titulo, cat.nome, c.tipo, (c.embedding <=> %s::vector) AS distancia
                       FROM conteudo c
                       JOIN categoria cat ON c.categoria_id = cat.categoria_id
                       ORDER BY distancia ASC
                       LIMIT %s""",
                    (vetor_consulta, limite)
                )
                
                for idx, row in enumerate(cur.fetchall(), start=1):
                    resultados.append({
                        "posicao": idx,
                        "conteudo_id": row[0],
                        "titulo": row[1],
                        "categoria": row[2],
                        "tipo": row[3],
                        "distancia_cosseno": round(float(row[4]), 4)
                    })
        finally:
            conn.close()
            
        return resultados
