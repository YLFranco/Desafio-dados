-- sql/dados_mestres.sql

-- RF30: Criação da Tabela Mestre de Conteúdos (MDM)
CREATE TABLE IF NOT EXISTS conteudo_master (
    master_id SERIAL PRIMARY KEY,
    conteudo_id INT UNIQUE NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    nivel VARCHAR(50) NOT NULL,
    carga_horaria_min INT NOT NULL,
    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regra de Sobrevivência e Resolução de Conflitos:
-- Se o mesmo conteudo_id for reinserido com dados conflitantes, 
-- o sistema adota o critério de sobrevivência do registro mais recente (UPDATE)
-- e mantém a maior carga horária informada (Garante integridade).
INSERT INTO conteudo_master (conteudo_id, titulo, categoria, nivel, carga_horaria_min, ultima_atualizacao)
VALUES (1, 'Introdução ao SQL para IA', 'Ciência De Dados', 'Básico', 120, CURRENT_TIMESTAMP)
ON CONFLICT (conteudo_id) 
DO UPDATE SET 
    titulo = EXCLUDED.titulo,
    categoria = EXCLUDED.categoria,
    nivel = EXCLUDED.nivel,
    carga_horaria_min = GREATEST(conteudo_id.carga_horaria_min, EXCLUDED.carga_horaria_min),
    ultima_atualizacao = CURRENT_TIMESTAMP;
