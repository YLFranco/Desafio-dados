# Ambiente do Desafio Prático 2

## Ambiente de desenvolvimento

- Sistema operacional: Ubuntu
- Python: 3.12.3
- Docker: 29.1.3
- Docker Compose: 2.40.3
- PostgreSQL: 17.11
- pgvector: 0.8.6
- MongoDB: 7.0.43

## Serviços containerizados

### PostgreSQL

- Container: `desafio_postgres`
- Banco: `plataforma_edu`
- Porta externa: `5432`
- Imagem: `pgvector/pgvector:pg17`

### MongoDB

- Container: `desafio_mongo`
- Banco: `plataforma_edu_nosql`
- Porta externa: `27017`
- Imagem: `mongo:7.0`

## Componentes ainda não instalados

As versões serão registradas quando os componentes forem configurados:

- Apache Hop
- Apache Beam
- Spark
- Apache Superset
- OpenMetadata

## Segurança de configuração

As credenciais locais são mantidas no arquivo `.env`.

O arquivo `.env` não deve ser versionado.

O repositório mantém apenas `.env.example`, sem credenciais reais.