# Pipeline de Recomendação e Dashboard — Fundamentos de Dados para IA

Este projeto consiste em um pipeline reproduzível de engenharia de dados que abrange desde a ingestão até a entrega final de inteligência. A solução engloba o tratamento de arquivos brutos, armazenamento híbrido (Relacional/NoSQL), geração de embeddings semânticos para o motor de recomendação e disponibilização de views analíticas para dashboards.

---

##  Membros da Equipe
* **André Luiz Carvalho Nunes**
* **Leandro José Conceição Souza**
* **Yuri Lino Franco**

---

##  Como Executar o Projeto

Siga os passos abaixo sequencialmente para configurar o ambiente e rodar toda a aplicação:

### 1. Instalar as Dependências
Certifique-se de estar com seu ambiente virtual ativo e instale as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### 2. Configurar as Variáveis de Ambiente
Crie um arquivo chamado `.env` na raiz do seu projeto e preencha com as credenciais de acesso aos seus servidores locais:
```text
DB_HOST=localhost
DB_PORT=5432
DB_USER=seu_usuario
DB_PASSWORD=sua_senha_aqui
DB_NAME=plataforma_edu
```

### 3. Criar a Estrutura do Banco de Dados (PostgreSQL)
Execute os comandos abaixo no seu terminal para criar o banco de dados, habilitar as extensões necessárias (como `pgvector`), estruturar as tabelas e gerar as views analíticas:
```bash
psql -U postgres -d postgres -c "CREATE DATABASE plataforma_edu;"
psql -U postgres -d plataforma_edu -f sql/criar_banco.sql
psql -U postgres -d plataforma_edu -f sql/consultas.sql
```

### 4. Executar o Pipeline Integrado
Rode o script principal para iniciar a extração, tratamento, carga dos dados e cálculo das recomendações via IA:
```bash
python -m src.main
```

### 5. Acessar as Métricas e Dashboards
1. Abra a interface do **Apache Superset**.
2. Conecte uma nova fonte de dados apontando para o banco `plataforma_edu`.
3. Explore e visualize os dados a partir das views analíticas geradas na etapa 3.
