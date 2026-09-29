# Glossário de Negócio

## Usuário ativo

**Definição:** usuário que possui pelo menos uma interação registrada no período analisado.

**Cálculo:** `COUNT(DISTINCT usuario_id)` sobre as interações dentro do período.

**Granularidade:** período selecionado.

**Owner proposto:** Área de Dados / Produto Educacional.

## Taxa de conclusão

**Definição:** percentual de interações consideradas concluídas em relação ao total de interações.

**Cálculo:** quantidade de interações com conclusão total dividida pela quantidade total de interações, multiplicada por 100.

**Exclusões:** registros inválidos ou direcionados à quarentena não participam da camada Gold.

**Owner proposto:** Área de Dados / Produto Educacional.

## Conversão de recomendação

**Definição:** proporção das recomendações geradas que resultaram em interação do usuário com o conteúdo recomendado.

**Cálculo:** recomendações convertidas / total de recomendações * 100.

**Owner proposto:** Produto / Recomendação.

## Engajamento por categoria

**Definição:** conjunto de métricas de interação dos usuários agrupadas pela categoria do conteúdo.

**Indicadores utilizados:** total de interações, usuários distintos e média do percentual de conclusão.

**Owner proposto:** Produto Educacional.
