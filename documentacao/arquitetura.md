# Relatório de Definição e Justificativa de Arquitetura de Dados

Este documento atende às exigências do requisito **RF19**, mapeando o fluxo ponta a ponta da solução, identificando os momentos de manipulação dos dados (Extração, Transformação e Carga) e justificando a abordagem tecnológica adotada pelo time de engenharia de dados.

---

## 1. Mapeamento do Fluxo de Dados e Camadas (Medallion Architecture)

O nosso ecossistema de dados foi estruturado seguindo o padrão de arquitetura de camadas (Lakehouse), garantindo que os dados evoluam em níveis de maturidade, governança e segurança:

1. **Fontes de Origem:** Arquivos estruturados (CSV do Catálogo), semiestruturados (JSONs de Interações e Comentários) e tabelas transacionais do PostgreSQL/MongoDB legados.
2. **Camada Bronze (Raw/Bruta):** Cópia idêntica e auditável das fontes. A extração ocorre sem nenhuma transformação destrutiva, apenas anexando metadados chaves do sistema (`data_hora_ingestao` e o processo `PID`).
3. **Camada Silver (Trusted/Tratada):** Camada de dados padronizados. Os dados passam por higienização de strings, tipagem estrita e filtros condicionais de qualidade via Apache Hop. Registros inconsistentes são isolados na Quarentena de forma síncrona.
4. **Camada Gold (Analytics/Negócio):** Tabelas agregadas e consolidadas orientadas a responder aos KPIs e perguntas estratégicas de negócio. Os dados nesta fase estão pseudonimizados em conformidade com a LGPD e armazenados em alta performance.
5. **Consumo:** Disponibilização da Camada Gold para o Apache Superset e modelagens via SQL Lab.

---

## 2. Classificação da Abordagem: Arquitetura Híbrida (ETL + ELT)

O projeto adota uma **Arquitetura Híbrida**, combinando os benefícios do modelo tradicional **ETL** com a flexibilidade moderna do **ELT**:

* **ETL (Extract, Transform, Load) entre as camadas Bronze e Silver:** As transformações, limpezas e desvios para quarentena são processados em memória pelo motor do **Apache Hop** antes de gravar os arquivos finais em formato definitivo. Isso impede a entrada de dados sujos ou inválidos na camada de confiança (Silver).
* **ELT (Extract, Load, Transform) na camada Gold:** O motor do **Apache Beam** (DirectRunner) extrai os dados limpos da Silver, carrega-os na esteira distribuída de alta performance para realizar agregações pesadas de tempo de consumo e volumetria por curso, salvando os resultados finais na Gold.

### Justificativa de Escolha (Vantagens Corporativas):
* **Custo e Desempenho:** A limpeza inicial remove o desperdício de processar linhas corrompidas. O uso de processamento distribuído (Beam/Spark) para as agregações da Gold garante escalabilidade à medida que o volume de acessos aumenta.
* **Reprocessamento e Governança:** Caso uma regra de negócio mude na Gold, os dados limpos já estão estruturados na Silver, permitindo reexecutar o pipeline analítico instantaneamente sem a necessidade de reingerir as fontes originais brutas.

---

## 3. Limitações da Abordagem Anterior (Desafio 1) vs Ganhos Atuais

A solução desenvolvida no Desafio Prático 1 baseava-se puramente em scripts isolados executados sequencialmente em Python. Essa abordagem apresentava severas restrições técnicas superadas no estágio atual:

* **Falta de Linhagem e Auditoria:** Scripts isolados gravavam arquivos sem rastreamento de ID de execução ou hora, dificultando saber quando ou qual processo gerou um erro no banco. Hoje, a auditoria é nativa no Apache Hop.
* **Riscos de Carga Parcial (Inconsistência):** Se um script do Desafio 1 falhasse na metade, o banco de dados corria o risco de reter cargas parciais duplicadas ou corrompidas. No modelo atual, o workflow do Hop (`.hwf`) atua como orquestrador atômico, interrompendo as fases seguintes se um erro crítico for detectado.
* **Falta de Escalabilidade Horizontual:** Pandas carrega todo o conjunto de dados na memória RAM de uma única máquina. Ao migrarmos as agregações pesadas para o **Apache Beam**, preparamos a plataforma para processar petabytes de dados de interações distribuídos de forma paralela.
