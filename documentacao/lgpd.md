# Inventário técnico de dados e proteção

> Documento técnico de engenharia de dados. Não substitui avaliação jurídica.

## Inventário

### usuario_id
- Tipo: identificador indireto/pseudônimo no conjunto analítico.
- Finalidade: relacionar interações e calcular métricas de uso.
- Necessidade: necessária para contagens distintas, jornada e recomendação.
- Gold: evitar exposição do identificador original quando não necessário.

### Dados de conteúdo
Título, categoria, nível, autor e demais atributos de conteúdo não representam, por si só, dados pessoais do usuário da plataforma.

## Princípios aplicados

- finalidade;
- necessidade;
- minimização;
- segurança.

## Estratégias

### Mascaramento
Quando um campo identificável for necessário apenas para exibição parcial, utilizar mascaramento.

### Pseudonimização
Criar identificador substituto quando for necessário relacionar registros sem expor o identificador original. O mapeamento deve ficar fora do repositório e possuir acesso controlado.

### Hash com segredo/salt protegido
Para comparação determinística sem exposição do valor original, utilizar segredo ou salt protegido fora do código e fora do repositório.

## Camadas

- Bronze: acesso mais restrito e preservação do dado recebido.
- Silver: aplicação das regras de proteção.
- Gold: apenas dados necessários para análise e dashboard.

## Segredos

Senhas, salts, chaves e arquivos de associação não devem ser versionados no Git.
