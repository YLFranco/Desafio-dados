# Registro de Uso de Inteligência Artificial (AI)

## 1. Ferramentas Utilizadas
* **Modelo:** Google Gemini / Assistente de IA Generativa.

## 2. Exemplos de Solicitações e Prompts Realizados
* **Prompt 1 (Modelagem):** *"Como criar uma tabela no PostgreSQL para armazenar embeddings textuais usando a extensão pgvector?"*
* **Prompt 2 (Depuração):** *"Estou tendo um erro 'operator does not exist: vector <=> double precision[]' ao tentar fazer uma busca por similaridade usando o psycopg e pgvector. Como corrigir?"*

## 3. Decisões Apoiadas pela IA
* **Uso do pgvector:** A decisão arquitetural de acoplar a extensão `vector` diretamente no PostgreSQL (`sql/criar_banco.sql`) em vez de subir um banco vetorial isolado (como Pinecone), otimizando a infraestrutura mínima em um único banco relacional.
* **Fórmula de Recomendação:** Estruturação da consulta lógica em SQL para computar os índices binários e de afinidade temática (`Ivis` e `Icur`) exigidos na regra de negócio.

## 4. Erros Encontrados nas Respostas da IA e Alterações da Equipe
* **Tipagem no Driver do Python:** A IA inicialmente gerou uma query de busca por similaridade semântica passando a lista pura do Python para o operador `<=>`. O PostgreSQL rejeitou com um erro de tipo (`double precision[]`).
* **Correção feita pela equipe:** Foi aplicada a correção manual adicionando o cast de tipo explícito `%s::vector` no script `src/ia.py` para forçar o driver do banco a compreender as dimensões do embedding gerado pelo modelo `SentenceTransformer`.
