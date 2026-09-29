-- =========================================================
-- DESAFIO PRATICO 2 - CONSULTAS PARA SQL LAB / SUPERSET
-- =========================================================

-- QUERY 1
-- Engajamento por categoria.
-- Usa JOIN + agregacao.
SELECT
    c.categoria,
    COUNT(*) AS total_interacoes,
    COUNT(DISTINCT i.usuario_id) AS usuarios,
    ROUND(AVG(i.percentual_conclusao), 2) AS media_conclusao
FROM silver.interacoes i
JOIN silver.catalogo c
    ON c.conteudo_id = i.conteudo_id
GROUP BY c.categoria
ORDER BY total_interacoes DESC;


-- QUERY 2
-- Evolucao mensal das interacoes por categoria.
-- Usa JOIN + DATE_TRUNC + agregacao.
SELECT
    DATE_TRUNC('month', i.data_hora) AS mes,
    c.categoria,
    COUNT(*) AS total_interacoes,
    ROUND(AVG(i.percentual_conclusao), 2) AS media_conclusao
FROM silver.interacoes i
JOIN silver.catalogo c
    ON c.conteudo_id = i.conteudo_id
GROUP BY
    DATE_TRUNC('month', i.data_hora),
    c.categoria
ORDER BY mes, c.categoria;


-- QUERY 3
-- Classificacao do engajamento dos conteudos.
-- Usa CASE + JOIN + agregacao.
SELECT
    c.conteudo_id,
    c.titulo,
    c.categoria,
    COUNT(i.usuario_id) AS total_interacoes,
    ROUND(AVG(i.percentual_conclusao), 2) AS media_conclusao,
    CASE
        WHEN AVG(i.percentual_conclusao) >= 80 THEN 'ALTO'
        WHEN AVG(i.percentual_conclusao) >= 50 THEN 'MEDIO'
        ELSE 'BAIXO'
    END AS faixa_engajamento
FROM silver.catalogo c
LEFT JOIN silver.interacoes i
    ON i.conteudo_id = c.conteudo_id
GROUP BY
    c.conteudo_id,
    c.titulo,
    c.categoria
ORDER BY total_interacoes DESC;
