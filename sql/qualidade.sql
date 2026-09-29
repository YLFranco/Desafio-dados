CREATE SCHEMA IF NOT EXISTS qualidade;

CREATE TABLE IF NOT EXISTS qualidade.resultado_execucao (
    id BIGSERIAL PRIMARY KEY,
    execucao_id TEXT NOT NULL,
    fonte TEXT NOT NULL,
    teste TEXT NOT NULL,
    dimensao TEXT NOT NULL,
    severidade TEXT NOT NULL,
    resultado TEXT NOT NULL,
    valor_observado NUMERIC,
    limite_esperado TEXT,
    data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DELETE FROM qualidade.resultado_execucao
WHERE execucao_id = '${EXECUCAO_ID}';

INSERT INTO qualidade.resultado_execucao
(execucao_id, fonte, teste, dimensao, severidade, resultado, valor_observado, limite_esperado)
SELECT
    '${EXECUCAO_ID}',
    'silver.catalogo',
    'Campos obrigatorios nulos',
    'completude',
    'CRITICA',
    CASE WHEN COUNT(*) = 0 THEN 'SUCESSO' ELSE 'FALHA' END,
    COUNT(*),
    '= 0'
FROM silver.catalogo
WHERE conteudo_id IS NULL
   OR titulo IS NULL
   OR tipo IS NULL
   OR categoria IS NULL
   OR nivel IS NULL
   OR carga_horaria_min IS NULL
   OR data_publicacao IS NULL;

INSERT INTO qualidade.resultado_execucao
(execucao_id, fonte, teste, dimensao, severidade, resultado, valor_observado, limite_esperado)
SELECT
    '${EXECUCAO_ID}',
    'silver.catalogo',
    'Duplicidade de conteudo_id',
    'unicidade',
    'CRITICA',
    CASE WHEN COUNT(*) = 0 THEN 'SUCESSO' ELSE 'FALHA' END,
    COUNT(*),
    '= 0'
FROM (
    SELECT conteudo_id
    FROM silver.catalogo
    GROUP BY conteudo_id
    HAVING COUNT(*) > 1
) d;

INSERT INTO qualidade.resultado_execucao
(execucao_id, fonte, teste, dimensao, severidade, resultado, valor_observado, limite_esperado)
SELECT
    '${EXECUCAO_ID}',
    'silver.interacoes',
    'Percentual de conclusao fora do intervalo',
    'validade',
    'CRITICA',
    CASE WHEN COUNT(*) = 0 THEN 'SUCESSO' ELSE 'FALHA' END,
    COUNT(*),
    '0 a 100'
FROM silver.interacoes
WHERE percentual_conclusao < 0
   OR percentual_conclusao > 100;

INSERT INTO qualidade.resultado_execucao
(execucao_id, fonte, teste, dimensao, severidade, resultado, valor_observado, limite_esperado)
SELECT
    '${EXECUCAO_ID}',
    'silver.interacoes',
    'Referencias de usuario ou conteudo inexistentes',
    'integridade_referencial',
    'CRITICA',
    CASE WHEN COUNT(*) = 0 THEN 'SUCESSO' ELSE 'FALHA' END,
    COUNT(*),
    '= 0'
FROM silver.interacoes i
LEFT JOIN public.usuario u
       ON u.usuario_id = i.usuario_id
LEFT JOIN public.conteudo c
       ON c.conteudo_id = i.conteudo_id
WHERE u.usuario_id IS NULL
   OR c.conteudo_id IS NULL;

INSERT INTO qualidade.resultado_execucao
(execucao_id, fonte, teste, dimensao, severidade, resultado, valor_observado, limite_esperado)
SELECT
    '${EXECUCAO_ID}',
    'silver.interacoes',
    'Auditoria inconsistente com a execucao',
    'consistencia',
    'CRITICA',
    CASE WHEN COUNT(*) = 0 THEN 'SUCESSO' ELSE 'FALHA' END,
    COUNT(*),
    'origem=interacoes.json e execucao_id atual'
FROM silver.interacoes
WHERE origem <> 'interacoes.json'
   OR execucao_id <> '${EXECUCAO_ID}';
