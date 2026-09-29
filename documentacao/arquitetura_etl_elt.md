# Arquitetura ETL/ELT — Desafio Prático 2

## Visão geral

A solução utiliza uma arquitetura em camadas Medallion:

**Fontes → Apache Hop → Bronze → Silver / Quarentena → Qualidade → Gold → Superset**

A governança será complementada pelo OpenMetadata, com catálogo, glossário, classificação e linhagem.

## Pontos de ETL e ELT

### ETL
O Apache Hop executa a extração dos arquivos CSV/JSON, adiciona campos de auditoria e grava a camada Bronze. Na passagem Bronze → Silver são feitas padronização, tipagem, deduplicação, validação e direcionamento de registros inválidos para quarentena.

### ELT
Na camada Gold são utilizadas consultas SQL e views no PostgreSQL para produzir estruturas orientadas a consumo analítico e KPIs.

### Classificação
A arquitetura é **híbrida ETL/ELT**.

- ETL: ingestão e tratamento Bronze → Silver.
- ELT: modelagem e agregações Silver → Gold dentro do PostgreSQL.

## Justificativa

A Bronze preserva os dados de origem sem destruição e permite reprocessamento. A Silver centraliza regras de qualidade e padronização. A Gold reduz custo de consulta e simplifica o consumo analítico. O modelo híbrido permite combinar governança, rastreabilidade e facilidade de reprocessamento.

## Reprocessamento

Cada execução da Bronze recebe um `execucao_id`, além de `origem` e `data_hora_ingestao`. Isso permite manter histórico de cargas e rastrear uma execução específica.

## Limitações de scripts isolados

Scripts independentes dificultam:
- controle de dependências entre etapas;
- interrupção em falha crítica;
- rastreabilidade da execução;
- tratamento uniforme de erros;
- reprocessamento;
- observabilidade.

O workflow principal do Apache Hop reduz essas limitações ao orquestrar Bronze, Silver, qualidade e Gold.
