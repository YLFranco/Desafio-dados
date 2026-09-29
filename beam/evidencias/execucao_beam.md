# Evidência de execução Apache Beam

## Pipeline

Arquivo:

`hop/pipelines/beam_agregacao_catalogo_2024.hpl`

Fluxo:

Silver Parquet 2024
→ leitura do Parquet
→ agregação por categoria
→ contagem de conteúdos
→ média da carga horária
→ gravação em Parquet + Snappy

O mesmo pipeline foi utilizado nos dois runtimes.

## Volume

Partição utilizada: ano 2024.

Quantidade de registros de entrada: 408.

## Beam DirectRunner

Run configuration:

`Beam Direct`

Saída:

`dados/gold/beam/direct/`

A execução gerou arquivos `catalogo_categoria_*.parquet.snappy`.

Tempo observado entre início do hop-run e geração da saída: aproximadamente 10 segundos.

## Beam Spark

Run configuration:

`Beam Spark`

Spark master:

`local[4]`

Saída:

`dados/gold/beam/spark/`

A execução apresentou a mensagem:

`Beam pipeline execution has finished.`

e gerou arquivos `catalogo_categoria_*.parquet.snappy`.

Tempo observado do processo completo: aproximadamente 12 segundos.

Tempo entre criação/início efetivo do pipeline Beam e finalização: aproximadamente 4 segundos.

## Conclusão

A mesma regra de transformação foi executada com sucesso utilizando:

- Apache Beam DirectRunner;
- Apache Beam Spark.

Os dois runtimes produziram saída Parquet comprimida com Snappy.
