# Acordo de Nível de Serviço (SLA) e Regras de Qualidade de Dados

Este documento estabelece as regras de qualidade, filtros de validação e políticas de desvio para a quarentena implementados na camada **Silver**, conforme as exigências dos requisitos **RF21** e **RF23** do Desafio Prático 2.

## 1. Mapeamento de Regras por Origem

### 1.1. Catálogo de Conteúdos (CSV ➡️ Camada Bronze)
* **Regra Q01 (Campos Obrigatórios):** O registro deve conter obrigatoriamente os campos `conteudo_id`, `titulo`, `tipo`, `categoria` e `nivel` preenchidos.
  * *Ação de Falha:* Desvio imediato para `dados/quarentena/catalogo_rejeitado.csv`.
* **Regra Q02 (Sanidade Numérica):** O campo `carga_horaria_min` não pode conter valores nulos ou negativos (`< 0`).
  * *Ação de Falha:* Isolamento na quarentena com a flag de erro correspondente.

### 1.2. Interações de Usuários (JSON ➡️ Camada Bronze)
* **Regra Q03 (Validação Lógica de Conclusão):** Registros com `tipo_interacao = 'conclusão'` devem, obrigatoriamente, apresentar `percentual_conclusao = 100.0`.
  * *Ação de Falha:* Encaminhamento automático para a esteira de rejeitados.
* **Regra Q04 (Validação de Avaliação precoce):** Se o usuário realizou uma ação do tipo `avaliação`, o campo `percentual_conclusao` deve ser igual a `100.0` (o aluno não pode avaliar um curso que não concluiu).
  * *Ação de Falha:* Desvio para o arquivo `dados/quarentena/interacoes_rejeitadas.json` através do bloco *Filter Rows* do Apache Hop.

---

## 2. Fluxo de Tratamento e Quarentena (RF23)

O pipeline visual orquestrado no **Apache Hop** atua como o motor de governança ativa do Lakehouse:
1. **Bifurcação Condicional:** O bloco *Filter Rows* avalia a expressão lógica descrita na Regra Q04 (`percentual_conclusao < 100 AND tipo_interacao = 'avaliação'`).
2. **Result is TRUE (Dado Corrompido):** O registro é isolado e gravado no diretório de quarentena, preservando o estado original para auditoria do time de governança de dados, evitando a poluição dos KPIs corporativos.
3. **Result is FALSE (Dado Higienizado):** O registro segue para o arquivo definitivo da camada Silver, recebendo codificação universal **UTF-8** para preservação da acentuação ortográfica.

---

## 3. Monitoramento de Métricas de Qualidade

A taxa de rejeição da quarentena é acompanhada através de volumetrias automatizadas. No último ciclo de processamento, a volumetria consolidou:
* **Registros Processados com Sucesso (Silver):** 895 linhas higienizadas.
* **Registros Desviados (Quarentena):** 105 linhas isoladas.
* **Índice de Qualidade da Base Bruta:** 89.5% de conformidade.
