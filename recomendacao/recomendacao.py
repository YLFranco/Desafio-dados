# src/recomendacao.py
from datetime import datetime

from src.postgres import obter_conexao_postgres


def gerar_recomendacoes_usuario(usuario_id):
    """Calcula scores e gera recomendações baseadas no comportamento do usuário"""
    conn = obter_conexao_postgres()
    recomendacoes_geradas = []
    
    try:
        with conn.cursor() as cur:
            # 1. Obter o total de tempo consumido pelo usuário por categoria (para Ivis)
            cur.execute("""
                SELECT c.categoria_id, SUM(i.tempo_consumido) 
                FROM interacao i
                JOIN conteudo c ON i.conteudo_id = c.conteudo_id
                WHERE i.usuario_id = %s
                GROUP BY c.categoria_id
            """, (usuario_id,))
            tempo_por_categoria = dict(cur.fetchall())
            tempo_total = sum(tempo_por_categoria.values()) if tempo_por_categoria else 0

            # 2. Obter categorias onde o usuário deu curtidas ou notas >= 4 (para Icur)
            cur.execute("""
                SELECT DISTINCT c.categoria_id
                FROM interacao i
                JOIN conteudo c ON i.conteudo_id = c.conteudo_id
                WHERE i.usuario_id = %s AND (i.tipo_interacao = 'curtida' OR i.avaliacao_atribuida >= 4)
            """, (usuario_id,))
            categorias_curtidas = {row[0] for row in cur.fetchall()}

            # 3. Obter conteúdos que o usuário já CONCLUIU (para Iconc = 0)
            cur.execute("""
                SELECT conteudo_id FROM interacao 
                WHERE usuario_id = %s AND tipo_interacao = 'conclusão'
            """, (usuario_id,))
            conteudos_concluidos = {row[0] for row in cur.fetchall()}

            # 4. Buscar todos os conteúdos do catálogo para avaliar a pontuação
            cur.execute("SELECT conteudo_id, titulo, categoria_id FROM conteudo")
            todos_conteudos = cur.fetchall()

            for conteudo_id, titulo, categoria_id in todos_conteudos:
                # Iconc: Se já concluiu, score é 0 (eliminado)
                if conteudo_id in conteudos_concluidos:
                    continue
                
                # Calcular Ivis (Proporção de tempo na categoria)
                if tempo_total > 0 and categoria_id in tempo_por_categoria:
                    ivis = tempo_por_categoria[categoria_id] / tempo_total
                else:
                    ivis = 0.0

                # Calcular Icur (1.0 se já interagiu positivamente na categoria, senão 0.0)
                icur = 1.0 if categoria_id in categorias_curtidas else 0.0

                # Aplicação da fórmula oficial do desafio
                pontuacaofinal = ((ivis + icur) / 2.0) * 100

                # Guardar candidatos elegíveis (com afinidade estável ou positiva)
                if pontuacaofinal > 0:
                    recomendacoes_geradas.append({
                        "usuario_id": usuario_id,
                        "conteudo_id": conteudo_id,
                        "titulo": titulo,
                        "score": round(pontuacaofinal, 2)
                    })

            # Ordenar pelo maior score
            recomendacoes_geradas = sorted(recomendacoes_geradas, key=lambda x: x['score'], reverse=True)

            # Persistência das Recomendações no PostgreSQL
            # Limpar recomendações anteriores do usuário para não duplicar
            cur.execute("DELETE FROM recomendacao WHERE usuario_id = %s", (usuario_id,))
            
            # Salva o Top 5 recomendações
            for posicao, rec in enumerate(recomendacoes_geradas[:5], start=1):
                cur.execute("""
                    INSERT INTO recomendacao (usuario_id, conteudo_id, pontuation_final, posicao_resultado, data_hora_geracao)
                    VALUES (%s, %s, %s, %s, %s)
                """, (rec['usuario_id'], rec['conteudo_id'], rec['score'], posicao, datetime.now()))
                
        conn.commit()
    finally:
        conn.close()
        
    return recomendacoes_geradas[:5]
