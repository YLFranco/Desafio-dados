# Produção de Métricas e KPIs — Pipeline Educacional

Este documento detalha os indicadores e KPIs implementados no projeto para apoiar a tomada de decisão da plataforma educacional, conforme o requisito RF12.

## 1. Métricas Operacionais

### Métrica 1: Totalização Básica do Ecossistema
* **Nome:** Volumetria Geral de Registros Sanitizados
* **Objetivo:** Monitorar o volume total de entidades carregadas após o processo de DataOps.
* **Fórmula:** 
  * `Total Usuários = COUNT(usuario_id)`
  * `Total Conteúdos = COUNT(conteudo_id)`
  * `Total Interações = COUNT(interacao_id)`
* **Fonte dos dados:** Tabelas `usuario`, `conteudo` e `interacao` no PostgreSQL.
* **Periodicidade:** Atualização em tempo real a cada execução do pipeline.
* **Interpretação:** Fornece a escala atual da base de dados ativa da plataforma.

### Métrica 2: Volume de Visualizações por Período
* **Nome:** Histórico Mensal de Engajamento Passivo
* **Objetivo:** Identificar tendências sazonais de acessos na plataforma.
* **Fórmula:** `COUNT(interacao_id) WHERE tipo_interacao = 'visualização' GROUP BY TO_CHAR(data_hora, 'YYYY-MM')`
* **Fonte dos dados:** Tabela `interacao` no PostgreSQL.
* **Periodicidade:** Mensal.
* **Interpretação:** Picos de visualização indicam períodos de maior interesse ou campanhas de engajamento bem-sucedidas.

---

## 2. KPIs Orientados à Tomada de Decisão

### KPI 1: Taxa de Conclusão por Curso
* **Nome:** Índice de Retenção e Conclusão de Conteúdo (Nível de Engajamento Eficiente)
* **Objetivo:** Avaliar a qualidade e a capacidade de retenção de cada material didático.
* **Fórmula:** `Taxa = (Total de Interações de Conclusão / Total de Interações de Início) * 100`
* **Fonte dos dados:** View `v_kpi_taxa_conclusao` (PostgreSQL).
* **Periodicidade:** Semanal / Mensal.
* **Interpretação:** Cursos com baixa taxa de conclusão (mesmo com alto número de inícios) indicam problemas de didática, fadiga do material ou desalinhamento de expectativas. Serve para decidir quais cursos precisam ser reformulados.

### KPI 2: Avaliação Média por Categoria Temática
* **Nome:** Score de Satisfação por Área do Conhecimento
* **Objetivo:** Apoiar o direcionamento de novos investimentos e contratação de professores para produzir conteúdos das áreas mais bem avaliadas.
* **Fórmula:** `Média = AVG(avaliacao_atribuida) GROUP BY categoria`
* **Fonte dos dados:** View `v_kpi_avaliacao_categoria` (PostgreSQL).
* **Periodicidade:** Mensal.
* **Interpretação:** Categorias com médias próximas a 5.0 possuem alta maturidade e satisfação. Áreas com médias inferiores a 3.5 exigem auditoria imediata sobre a qualidade dos materiais e autores.
