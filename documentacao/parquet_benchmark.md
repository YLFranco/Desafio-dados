# Comparação CSV x Parquet

## Recorte utilizado

Foi utilizada a partição de catálogo referente ao ano de 2024, contendo **408 registros**.

## Tamanho dos arquivos

### CSV
- 2024: 221.334 bytes
- 2025: 219.583 bytes
- 2026: 102.391 bytes
- Total: **543.308 bytes**

### Parquet + Snappy
- 2024: 65.124 bytes
- 2025: 63.999 bytes
- 2026: 28.590 bytes
- Total: **157.713 bytes**

O Parquet ocupou aproximadamente **70,97% menos espaço** que o CSV no conjunto completo.

## Tempo de leitura — partição 2024

- CSV: **0,056 s**
- Parquet execução 1: **0,042 s**
- Parquet execução 2: **0,034 s**
- Média Parquet: **0,038 s**

No recorte medido, o Parquet apresentou leitura aproximadamente **32,1% mais rápida** em relação à execução medida do CSV.

## Estratégia de particionamento

Os dados foram particionados por `ano_publicacao`:

- `ano=2024`
- `ano=2025`
- `ano=2026`

A estratégia permite evitar leitura de anos não necessários em consultas que filtram período.

## Limitação da medição

O conjunto possui apenas 1.000 registros. Em volumes pequenos, custos fixos de inicialização, cache do sistema operacional e aquecimento da JVM podem influenciar os tempos. Portanto, a comparação de tamanho é mais representativa que a diferença absoluta de tempo neste volume.
