
-- -------------------------------------------------------------------------
-- METRICAS OPERACIONAIS
-- -------------------------------------------------------------------------

-- 1. Totalização Básica do Ecossistema
CREATE OR REPLACE VIEW v_metrica_totalizacao AS
SELECT 
    (SELECT COUNT(*) FROM usuario) AS total_usuarios,
    (SELECT COUNT(*) FROM conteudo) AS total_conteudos,
    (SELECT COUNT(*) FROM interacao) AS total_interacoes;

-- 2. Volume de Visualizações por Mês/Ano
CREATE OR REPLACE VIEW v_metrica_visualizacoes_periodo AS
SELECT 
    TO_CHAR(data_hora, 'YYYY-MM') AS periodo,
    COUNT(*) AS total_visualizacoes
FROM interacao
WHERE tipo_interacao = 'visualização'
GROUP BY periodo
ORDER BY periodo;

-- -------------------------------------------------------------------------
-- KPIS ORIENTADOS À TOMADA DE DECISÃO
-- -------------------------------------------------------------------------

-- 1. Taxa de Conclusão por Curso (Mede a qualidade e retenção do conteúdo)
CREATE OR REPLACE VIEW v_kpi_taxa_conclusao AS
SELECT 
    c.conteudo_id,
    c.titulo,
    COUNT(CASE WHEN i.tipo_interacao = 'início' THEN 1 END) AS total_iniciados,
    COUNT(CASE WHEN i.tipo_interacao = 'conclusão' THEN 1 END) AS total_concluidos,
    CASE 
        WHEN COUNT(CASE WHEN i.tipo_interacao = 'início' THEN 1 END) > 0 
        THEN ROUND((COUNT(CASE WHEN i.tipo_interacao = 'conclusão' THEN 1 END)::NUMERIC / COUNT(CASE WHEN i.tipo_interacao = 'início' THEN 1 END)) * 100, 2)
        ELSE 0.00
    END AS taxa_conclusao_percentual
FROM conteudo c
LEFT JOIN interacao i ON c.conteudo_id = i.conteudo_id
GROUP BY c.conteudo_id, c.titulo;

-- 2. Avaliação Média por Categoria Temática (Apoia na decisão de novos investimentos)
CREATE OR REPLACE VIEW v_kpi_avaliacao_categoria AS
SELECT 
    cat.nome AS nome_categoria,
    COUNT(i.avaliacao_atribuida) AS total_avaliacoes,
    ROUND(AVG(i.avaliacao_atribuida)::NUMERIC, 2) AS avaliacao_media
FROM categoria cat
JOIN conteudo c ON cat.categoria_id = c.categoria_id
JOIN interacao i ON c.conteudo_id = i.conteudo_id
WHERE i.avaliacao_atribuida IS NOT NULL
GROUP BY cat.nome
ORDER BY avaliacao_media DESC;
