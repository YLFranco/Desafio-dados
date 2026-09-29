-- sql/sql_lab.sql
-- =========================================================================
-- REQUISITO RF17 - CONSULTAS ANALÍTICAS E CONJUNTOS DE DADOS VIRTUAIS
-- Finalidade: Modelar visões analíticas complexas a partir da Gold/Silver
-- para servir de fonte de dados limpa ao Apache Superset.
-- =========================================================================

-- -------------------------------------------------------------------------
-- CONSULTA 1: Funil de Conversão e Retenção por Nível do Curso
-- Objetivo: Agregar o volume de inícios vs conclusões e calcular a taxa
-- de eficiência utilizando expressões condicionais e agrupamentos.
-- -------------------------------------------------------------------------
-- FINALIDADE DO DATASET VIRTUAL: Fornecer ao dashboard a métrica de abandono
-- por nível de dificuldade, permitindo auditoria pedagógica.

SELECT 
    c.nivel AS nivel_curso,
    COUNT(CASE WHEN i.tipo_interacao = 'início' THEN 1 END) AS total_iniciados,
    COUNT(CASE WHEN i.tipo_interacao = 'conclusão' THEN 1 END) AS total_concluidos,
    CASE 
        WHEN COUNT(CASE WHEN i.tipo_interacao = 'início' THEN 1 END) > 0 
        THEN ROUND((COUNT(CASE WHEN i.tipo_interacao = 'conclusão' THEN 1 END)::NUMERIC / COUNT(CASE WHEN i.tipo_interacao = 'início' THEN 1 END)) * 100, 2)
        ELSE 0.00
    END AS taxa_conversao_percentual
FROM conteudo c
LEFT JOIN interacao i ON c.conteudo_id = i.conteudo_id
GROUP BY c.nivel
ORDER BY taxa_conversao_percentual DESC;


-- -------------------------------------------------------------------------
-- CONSULTA 2: Análise Temporal de Engajamento e Consumo Mensal
-- Objetivo: Utilizar funções de tratamento de data (TO_CHAR/DATE_TRUNC)
-- para consolidar o tempo gasto e o volume de interações passivas e ativas.
-- -------------------------------------------------------------------------
-- FINALIDADE DO DATASET VIRTUAL: Alimentar gráficos de linhas temporais,
-- identificando picos sazonais de acesso de usuários.

SELECT 
    TO_CHAR(i.data_hora, 'YYYY-MM') AS periodo_mensal,
    COUNT(i.interacao_id) AS volume_total_interacoes,
    ROUND(SUM(i.tempo_consumido) / 60.0, 2) AS tempo_total_consumido_horas,
    COUNT(DISTINCT i.usuario_id) AS estudantes_ativos_no_mes
FROM interacao i
WHERE i.data_hora >= '2026-01-01'::TIMESTAMP
GROUP BY TO_CHAR(i.data_hora, 'YYYY-MM')
ORDER BY periodo_mensal ASC;


-- -------------------------------------------------------------------------
-- CONSULTA 3: Auditoria de Qualidade e Desempenho dos Instrutores
-- Objetivo: Realizar junções triplas (Tabelas Conteúdo, Categoria e Interação)
-- para cruzar o score médio de avaliação com o percentual de entrega por autor.
-- -------------------------------------------------------------------------

SELECT 
    c.autor AS nome_professor,
    cat.nome AS especialidade_categoria,
    COUNT(DISTINCT c.conteudo_id) AS total_cursos_publicados,
    ROUND(AVG(i.avaliacao_atribuida)::NUMERIC, 2) AS score_medio_satisfacao,
    ROUND(AVG(i.percentual_conclusao)::NUMERIC, 2) AS media_progresso_alunos
FROM conteudo c
JOIN categoria cat ON c.categoria_id = cat.categoria_id
JOIN interacao i ON c.conteudo_id = i.conteudo_id
WHERE c.autor IS NOT NULL
GROUP BY c.autor, cat.nome
HAVING COUNT(i.interacao_id) > 5
ORDER BY score_medio_satisfacao DESC;
