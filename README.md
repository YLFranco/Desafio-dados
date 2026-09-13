[README.md](https://github.com/user-attachments/files/32157561/README.md)
# Pipeline de Recomendação e Dashboard — Fundamentos de Dados para IA

Este repositório contém a solução completa para o Desafio Prático 1. O projeto consiste em um pipeline reproduzível que abrange a ingestão de dados, armazenamento híbrido (Relacional/NoSQL), geração de embeddings semânticos e motor de recomendação.

##  Como Executar o Projeto

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure suas credenciais locais:**
   Crie e preencha as variáveis de acesso aos servidores locais no arquivo `.env` na raiz.

3. **Crie a estrutura de tabelas e views no PostgreSQL:**
   ```bash
   psql -U postgres -d postgres -c "CREATE DATABASE plataforma_edu;"
   psql -U postgres -d plataforma_edu -f sql/criar_banco.sql
   psql -U postgres -d plataforma_edu -f sql/consultas.sql
   ```

4. **Execute o pipeline integrado (Requisito RF01):**
   ```bash
   python -m src.main
   ```

5. **Acesse as métricas:**
   Conecte o Apache Superset ao banco `plataforma_edu` e explore as views analíticas configuradas.
