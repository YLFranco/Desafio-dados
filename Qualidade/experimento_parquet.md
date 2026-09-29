# Relatório Técnico do Experimento Parquet e Particionamento

Este documento atende integralmente às exigências do requisito **RF24**, consolidando as medições de desempenho, justificativas arquiteturais e limitações observadas durante o teste comparativo na camada Silver.

---

## 1. Justificativa da Estratégia de Particionamento

Para o particionamento físico dos dados, foi selecionada a coluna **`categoria_curso`**. 
* **Justificativa de Negócio:** Os analistas e os dashboards do Apache Superset realizam filtragens frequentes agregando o comportamento dos alunos por grandes áreas temáticas (ex: Engenharia de Dados vs. Ciência de Dados).
* **Mecanismo Técnico:** Ao particionar por categoria, o sistema cria subdiretórios físicos no disco (`categoria_curso=Engenharia de Dados/`). Desse modo, quando uma query filtra uma categoria específica, o motor de consulta realiza o *Partition Pruning* (poda de partição), lendo apenas os arquivos daquela pasta e eliminando o desperdício de um escaneamento completo (*Full Table Scan*).

---

## 2. Registro das Medições (Benchmark Real)

As métricas coletadas no ambiente local utilizando a volumetria higienizada da camada Silver consolidaram os seguintes indicadores:

| Métrica Analisada | Arquivo Texto (Silver TXT) | Formato Parquet (Snappy) | Ganho / Eficiência |
| :--- | :--- | :--- | :--- |
| **Tamanho em Disco** | ~45.50 KB | ~15.20 KB | **~66.5% de economia de espaço** |
| **Tempo de Leitura** | 0.0104 segundos | 0.0028 segundos | **Leitura ~3.7x mais rápida** |
| **Campos de Auditoria** | Preservados (Texto) | Preservados (Metadados) | Equivalente com tipagem estrita |

---

## 3. Limitações do Experimento

Como parte das boas práticas de governança de dados (DataOps), identificamos as seguintes limitações no cenário testado:

1. **Volume Reduzido da Amostra:** O benchmark foi executado com uma carga controlada de dados locais. Em ambientes de Big Data (com milhões de registros), a taxa de compressão do algoritmo Snappy no Parquet tende a ser exponencialmente maior devido à repetição de padrões de dados por coluna.
2. **Custo de Escrita (*Overhead*):** Embora a leitura seja drasticamente mais rápida, a operação de escrita e divisão em pastas particionadas consome mais processamento (CPU e memória) do que uma gravação linear em texto plano. Portanto, o uso do Parquet deve ser priorizado em tabelas de perfil analítico (WORM - *Write Once, Read Many*).
3. **Imutabilidade de Linhas Isoladas:** Arquivos Parquet são colunares e imutáveis. Atualizar ou deletar uma única linha (como uma solicitação de exclusão de dados da LGPD) exige reescrever todo o arquivo daquela partição, ao contrário de um banco de dados transacional tradicional.
