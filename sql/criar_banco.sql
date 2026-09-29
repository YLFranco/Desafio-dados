
psql -U yuri -d postgres -c "CREATE DATABASE plataforma_edu;"

-- Habilita a extensão de vetores (necessária para o pgvector no RF08)
CREATE EXTENSION IF NOT EXISTS vector;

-- Remoção de tabelas caso já existam (Garante a reprodutibilidade)
DROP TABLE IF EXISTS recomendacao CASCADE;
DROP TABLE IF EXISTS interacao CASCADE;
DROP TABLE IF EXISTS conteudo CASCADE;
DROP TABLE IF EXISTS categoria CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;

-- Criando a tabela de Categorias
CREATE TABLE categoria (
    categoria_id SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL
);

-- Criando a tabela de Usuários
CREATE TABLE usuario (
    usuario_id INT PRIMARY KEY,
    nome VARCHAR(100) DEFAULT 'Usuário Fictício'
);

-- Criando a tabela de Conteúdos (Catálogo)
CREATE TABLE conteudo (
    conteudo_id INT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    categoria_id INT NOT NULL,
    nivel VARCHAR(50) NOT NULL,
    carga_horaria_min INT NOT NULL,
    data_publicacao DATE NOT NULL,
    descricao TEXT,
    autor VARCHAR(100),
    embedding vector(384), -- Vetor de 384 dimensões (padrão de modelos leves como all-MiniLM-L6-v2)
    FOREIGN KEY (categoria_id) REFERENCES categoria(categoria_id)
);

-- Criando a tabela de Interações
CREATE TABLE interacao (
    interacao_id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    conteudo_id INT NOT NULL,
    tipo_interacao VARCHAR(50) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    tempo_consumido INT NOT NULL,
    percentual_conclusao NUMERIC(5,2) NOT NULL,
    avaliacao_atribuida INT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(usuario_id),
    FOREIGN KEY (conteudo_id) REFERENCES conteudo(conteudo_id)
);

-- Criando a tabela de Recomendações (RF11)
CREATE TABLE recomendacao (
    recomendacao_id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    conteudo_id INT NOT NULL,
    pontuation_final NUMERIC(5,2) NOT NULL,
    posicao_resultado INT NOT NULL,
    data_hora_geracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(usuario_id),
    FOREIGN KEY (conteudo_id) REFERENCES conteudo(conteudo_id)
);

-- sql/camada_bronze_auditoria.sql
-- =========================================================================
-- REQUISITO RF20 - DESTINO DE BANCO DE DADOS NA CAMADA BRONZE
-- Finalidade: Armazenar cópias brutas com logs de auditoria do sistema
-- =========================================================================

-- 1. Tabela de Auditoria Bruta do Catálogo
CREATE TABLE IF NOT EXISTS bronze_catalogo_auditoria (
    conteudo_id VARCHAR(50),
    titulo TEXT,
    tipo VARCHAR(100),
    categoria VARCHAR(150),
    nivel VARCHAR(100),
    carga_horaria_min VARCHAR(50),
    data_publicacao VARCHAR(100),
    descricao TEXT,
    autor VARCHAR(150),
    -- Campos obrigatórios de Auditoria (RF20)
    origem_dado VARCHAR(100) DEFAULT 'catalogo_csv',
    data_hora_ingestao VARCHAR(100),
    execucao_id VARCHAR(100)
);

-- 2. Tabela de Auditoria Bruta de Interações
CREATE TABLE IF NOT EXISTS bronze_interacoes_auditoria (
    usuario_id VARCHAR(50),
    conteudo_id VARCHAR(50),
    tipo_interacao VARCHAR(100),
    data_hora VARCHAR(100),
    tempo_consumido VARCHAR(50),
    percentual_conclusao VARCHAR(50),
    avaliacao_atribuida VARCHAR(50),
    -- Campos obrigatórios de Auditoria (RF20)
    origem_dado VARCHAR(100) DEFAULT 'interacoes_json',
    data_hora_ingestao VARCHAR(100),
    execucao_id VARCHAR(100)
);
