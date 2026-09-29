CREATE SCHEMA IF NOT EXISTS gold;

CREATE OR REPLACE VIEW gold.vw_engajamento_conteudo AS
SELECT
    c.conteudo_id,
    c.titulo,
    c.tipo,
    c.categoria,
    c.nivel,
    c.carga_horaria_min,
    COUNT(i.conteudo_id) AS total_interacoes,
    COUNT(DISTINCT i.usuario_id) AS usuarios_ativos,
    ROUND(AVG(i.percentual_conclusao)::numeric, 2) AS media_percentual_conclusao,
    COUNT(*) FILTER (WHERE i.tipo_interacao = 'conclusão') AS total_conclusoes,
    COUNT(*) FILTER (WHERE i.tipo_interacao = 'curtida') AS total_curtidas,
    ROUND(
        AVG(i.avaliacao_atribuida)
        FILTER (WHERE i.avaliacao_atribuida IS NOT NULL)::numeric,
        2
    ) AS avaliacao_media
FROM silver.catalogo c
LEFT JOIN silver.interacoes i
       ON i.conteudo_id = c.conteudo_id
GROUP BY
    c.conteudo_id,
    c.titulo,
    c.tipo,
    c.categoria,
    c.nivel,
    c.carga_horaria_min;

CREATE OR REPLACE VIEW gold.vw_engajamento_categoria AS
SELECT
    categoria,
    COUNT(*) AS total_conteudos,
    SUM(total_interacoes) AS total_interacoes,
    SUM(usuarios_ativos) AS soma_usuarios_por_conteudo,
    ROUND(AVG(media_percentual_conclusao)::numeric, 2) AS media_percentual_conclusao,
    SUM(total_conclusoes) AS total_conclusoes,
    SUM(total_curtidas) AS total_curtidas,
    ROUND(AVG(avaliacao_media)::numeric, 2) AS avaliacao_media
FROM gold.vw_engajamento_conteudo
GROUP BY categoria;

CREATE OR REPLACE VIEW gold.vw_kpis_gerais AS
SELECT
    (SELECT COUNT(*) FROM silver.catalogo) AS total_conteudos,
    (SELECT COUNT(*) FROM silver.interacoes) AS total_interacoes,
    (SELECT COUNT(DISTINCT usuario_id) FROM silver.interacoes) AS usuarios_ativos,
    (
        SELECT ROUND(AVG(percentual_conclusao)::numeric, 2)
        FROM silver.interacoes
    ) AS media_percentual_conclusao,
    (
        SELECT ROUND(
            100.0 * COUNT(*) FILTER (WHERE tipo_interacao = 'conclusão')
            / NULLIF(COUNT(*), 0),
            2
        )
        FROM silver.interacoes
    ) AS taxa_conclusao_interacoes;

CREATE OR REPLACE VIEW gold.vw_recomendacoes_conversao AS
SELECT
    r.recomendacao_id,
    r.usuario_id,
    r.conteudo_id,
    c.titulo,
    c.categoria,
    r.pontuation_final,
    r.posicao_resultado,
    r.data_hora_geracao,
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM silver.interacoes i
            WHERE i.usuario_id = r.usuario_id
              AND i.conteudo_id = r.conteudo_id
              AND i.data_hora >= r.data_hora_geracao
        ) THEN 1
        ELSE 0
    END AS convertida
FROM public.recomendacao r
LEFT JOIN silver.catalogo c
       ON c.conteudo_id = r.conteudo_id;

CREATE OR REPLACE VIEW gold.vw_kpi_recomendacao AS
SELECT
    COUNT(*) AS total_recomendacoes,
    SUM(convertida) AS recomendacoes_convertidas,
    ROUND(
        100.0 * SUM(convertida) / NULLIF(COUNT(*), 0),
        2
    ) AS taxa_conversao_recomendacao
FROM gold.vw_recomendacoes_conversao;
