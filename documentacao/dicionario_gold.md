# Especificação Técnica e Dicionário de Dados: Camada Gold (RF26)

Este documento descreve a estrutura, chaves, granularidade e lógica matemática aplicadas na consolidação das visões analíticas destinadas ao Apache Superset.

---

## 1. Definição do Dataset Analítico
* **Nome da Tabela:** `gold_metricas_conteudo`
* **Granularidade:** Um registro por `conteudo_id` (Nível Curso).
* **Frequência de Atualização:** Carga incremental/substituição síncrona a cada execução completa do Workflow.

---

## 2. Estrutura de Campos e Regras de Negócio

### 🔑 Chave Primária: `conteudo_id`
* **Tipo:** `VARCHAR(50)`
* **Descrição:** Identificador único do curso ou material didático.
* **Regra:** Chave de negócio mantida desde a origem (Catálogo) para servir de pivô nas junções do SQL Lab.

### 📐 Medida: `total_interacoes`
* **Tipo:** `INT`
* **Regra de Cálculo:** Contagem linear volumétrica (`COUNT`) de todas as linhas de ações limpas associadas ao curso na camada Silver.

### 📐 Medida: `tempo_total_minutos`
* **Tipo:** `NUMERIC(10,2)`
* **Regra de Cálculo:** Somatório acumulado (`SUM`) da coluna `tempo_consumido` dividido pelo motor distribuído do Apache Beam.

### 📐 Medida: `usuarios_unicos_impactados`
* **Tipo:** `INT`
* **Regra de Cálculo:** Contagem distinta (`COUNT DISTINCT`) baseada no campo `usuario_hash` (pseudonimizado via Hashing com Salt em conformidade com a LGPD). Garante a métrica real de alcance sem duplicações de acessos do mesmo aluno.
