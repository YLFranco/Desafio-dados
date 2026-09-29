# Testes de Qualidade

Os resultados são registrados por execução em `qualidade.resultado_execucao`.

| Dimensão | Teste | Severidade | Limite | Ação |
|---|---|---|---|---|
| Completude | Campos obrigatórios nulos no catálogo | CRÍTICA | 0 | Bloquear Gold |
| Unicidade | Duplicidade de `conteudo_id` | CRÍTICA | 0 | Bloquear Gold |
| Validade | `percentual_conclusao` fora de 0 a 100 | CRÍTICA | 0 | Bloquear Gold |
| Integridade referencial | usuário ou conteúdo inexistente | CRÍTICA | 0 | Bloquear Gold |
| Consistência | auditoria incompatível com execução/origem | CRÍTICA | 0 | Bloquear Gold |

## Resultado da execução 20260929_01

Os cinco testes retornaram `SUCESSO`, com valor observado igual a zero.

## Evolução recomendada

Acompanhar por execução:
1. percentual de registros enviados para quarentena;
2. quantidade de violações críticas.

Essas métricas permitem observar tendência de qualidade entre execuções.
