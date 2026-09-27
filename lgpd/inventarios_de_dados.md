# Inventário de Dados e Relatório de Impacto à Privacidade (RIPD)

Este documento atende às exigências normativas da Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018), mapeando o ciclo de vida dos dados pessoais tratados na plataforma educacional e detalhando as técnicas de proteção implementadas nas camadas **Silver** e **Gold** (conforme os requisitos **RF32** e **RF33**).

---

## 1. Inventário de Atividades de Tratamento (Data Mapping)

| Campo Original | Categoria do Dado | Finalidade do Tratamento | Fase de Mitigação de Risco | Status na Camada Gold |
| :--- | :--- | :--- | :--- | :--- |
| `usuario_id` | Dado Pessoal Direto (Identificador) | Rastrear o progresso do aluno e computar as métricas de recomendação. | Pseudonimização via Hash Criptográfico. | **Totalmente Mascarado** |
| `comentario` | Dado Pessoal Indireto (Opinião) | Avaliação qualitativa da percepção e satisfação dos cursos. | Armazenamento isolado e controlado no NoSQL MongoDB. | **Isolado / Não exposto** |

---

## 2. Técnicas de Proteção de Dados Aplicadas (RF32 & RF33)

### 2.1. Mascaramento e Pseudonimização (RF32)
Para garantir que analistas de negócios e ferramentas de BI (como o Apache Superset) consigam calcular métricas volumétricas sem expor a identidade dos estudantes, o identificador original `usuario_id` é removido e substituído por uma chave alfanumérica irreversível antes de tocar a camada analítica **Gold**.

### 2.2. Mecanismo de Criptografia Unidirecional com Salt (RF33)
Gerações simples de Hashing (como aplicar apenas `MD5` ou `SHA-256` diretamente no ID) são vulneráveis a ataques de engenharia reversa por tabelas de arco-íris (*Rainbow Tables*), visto que IDs sequenciais (1, 2, 3...) geram assinaturas facilmente previsíveis.

Para mitigar este risco, o nosso motor distribuidor em **Apache Beam** injeta uma técnica de **Salt Dinâmico**:
1. O sistema intercepta o `usuario_id` vindo da camada Silver.
2. Combina o ID a uma chave secreta alfa-numérica complexa de bastidores (`FicDevIA_Secret_Salt_2026!`).
3. Aplica o algoritmo de espelhamento matemático **SHA-256** sobre a string combinada.
4. Reduz a assinatura final para os 16 caracteres iniciais mais significativos.

**Fórmula Lógica:**
```text
Hash_Final = SHA-256(usuario_id + SALT_KEY)[:16]
```

---

## 3. Justificativa de Segurança e Governança

* **Irreversibilidade:** Mesmo que um ator mal-intencionado tenha acesso aos arquivos analíticos JSON da camada Gold, ele jamais conseguirá descobrir qual estudante realizou aquela ação, pois o Hash gerado com a nossa chave Salt é matematicamente irreversível.
* **Minimização de Dados:** Apenas as métricas estritamente necessárias para o cálculo de eficiência dos cursos (como total de interações e tempo gasto) foram mantidas na camada Gold, eliminando qualquer risco de vazamento de dados de identificação pessoal.
