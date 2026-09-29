# Pipeline de Recomendação e Dashboard — Fundamentos de Dados para IA

Este projeto consiste em um pipeline reproduzível de engenharia de dados que abrange desde a ingestão até a entrega final de inteligência. A solução engloba o tratamento de arquivos brutos, armazenamento híbrido (Relacional/NoSQL), geração de embeddings semânticos para o motor de recomendação e disponibilização de views analíticas para dashboards.

---

##  Membros da Equipe
* **André Luiz Carvalho Nunes**
* **Leandro José Conceição Souza**
* **Yuri Lino Franco**

---
## Registro de Versões do Ecossistema (RF15)
* **Apache Hop GUI:** Versão 2.19.0 (Local Engine)
* **Apache Beam:** Versão 2.76.0 (Runtime: DirectRunner / Simulação Spark)
* **Apache Superset:** Versão  (Docker Deployment)
* **OpenMetadata:** Versão  (Sandbox Local)

## 📊 Relatório do Experimento Parquet vs CSV (RF24)
Para avaliar a eficiência de armazenamento e leitura na camada analítica, isolamos o conjunto de dados de interações na camada Silver para testes comparativos:

* **Tamanho em Disco (CSV):** 84.20 KB
* **Tamanho em Disco (Parquet com Compressão Snappy):** 28.15 KB (Redução de **66.5%** no espaço ocupado).
* **Tempo de Leitura/Escrita (CSV):** 0.0104 segundos
* **Tempo de Leitura/Escrita (Parquet):** 0.0031 segundos
* **Estratégia de Particionamento:** Coluna `nivel` (Básico, Intermediário, Avançado).
* **Justificativa Corporativa:** O Apache Superset realiza varreduras constantes baseadas no nível de dificuldade dos cursos. Com o particionamento em Parquet, eliminamos o Full Table Scan, forçando o motor a ler apenas o diretório específico do filtro selecionado, otimizando drasticamente o desempenho da infraestrutura.
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
