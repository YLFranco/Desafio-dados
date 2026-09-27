# RF19 — Arquitetura ETL/ELT

## 1. Objetivo

A arquitetura do Desafio Prático 2 evolui a solução implementada no
Desafio Prático 1 para um fluxo automatizado, auditável, reprocessável
e organizado nas camadas Bronze, Silver e Gold.

A solução adota uma arquitetura híbrida ETL/ELT.

---

## 2. Arquitetura geral

```text
FONTES DO DESAFIO 1

catalogo.csv
interacoes.json
comentarios.json
PostgreSQL
MongoDB
        |
        | Extração
        v
+-----------------------------+
| APACHE HOP                  |
|                             |
| BRONZE                      |
| dados preservados           |
| + campos de auditoria       |
+-------------+---------------+
              |
              | Transformação
              v
+-----------------------------+
| APACHE HOP                  |
|                             |
| SILVER                      |
| padronização                |
| validação                   |
| deduplicação                |
| tratamento de ausentes      |
| validação de referências    |
+-------------+---------------+
              |
        +-----+------+
        |            |
        |            v
        |      QUARENTENA
        |      registros inválidos
        |
        v
+-----------------------------+
| PARQUET                     |
| dados Silver selecionados   |
+-------------+---------------+
              |
              v
+-----------------------------+
| APACHE BEAM                 |
| DirectRunner                |
| Spark                       |
+-------------+---------------+
              |
              v
+-----------------------------+
| POSTGRESQL                  |
| GOLD                        |
| dimensões                   |
| fatos                       |
| agregações                  |
| KPIs                        |
+-------------+---------------+
              |
        +-----+------+
        |            |
        v            v
     SQL Lab      OpenMetadata
        |         catálogo
        |         glossário
        |         linhagem
        |         qualidade
        |         classificação
        v
 Apache Superset
 dashboard
 filtros
 alertas
 storytelling