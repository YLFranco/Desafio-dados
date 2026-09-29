# Proposta de Master Data Management

## Entidade mestre escolhida

**Conteúdo educacional**

## Chave de negócio

`conteudo_id`

## Atributos essenciais

- título;
- tipo;
- categoria;
- nível;
- carga horária;
- data de publicação;
- autor.

## Fonte de referência

A camada Silver do catálogo é utilizada como fonte de referência após padronização, validação e deduplicação.

## Matching

A regra principal é determinística pelo `conteudo_id`.

## Deduplicação

Antes da persistência na Silver, os registros são ordenados pela chave e passam pela remoção de duplicados.

## Survivorship

Quando houver registros conflitantes para o mesmo `conteudo_id`, deve sobreviver o registro aceito pelas regras de qualidade e pertencente à execução considerada válida para reprocessamento. Registros rejeitados devem permanecer rastreáveis na quarentena.

## Identificador mestre

O próprio `conteudo_id` funciona como identificador mestre no escopo do desafio.

## Tratamento de conflito

Dois registros com a mesma chave e atributos conflitantes não devem ser mantidos simultaneamente na Silver. O conflito deve ser identificado, registrado e resolvido pela regra de fonte de referência/execução válida.
