# Relatório Executivo: Storytelling Analítico e Estratégia de Engajamento

**Pergunta Decisória Central:** *Como a distribuição e o nível dos conteúdos do catálogo impactam diretamente o engajamento eficiente e a taxa de conclusão dos usuários na plataforma?*

---

## 1. Contexto (O Cenário Atual)
A nossa plataforma educacional expandiu aceleradamente o seu catálogo, disponibilizando múltiplos formatos de mídias (cursos, vídeos, artigos e podcasts) para uma base diversificada de alunos. No entanto, a equipe de gestão operava às cegas devido à fragmentação dos dados brutos em arquivos CSV e JSON isolados. 

O objetivo deste projeto foi centralizar essas informações em uma arquitetura de Data Lakehouse governada e extrair inteligência analítica a partir da camada **Gold**, permitindo correlacionar os perfis dos cursos com o comportamento de consumo real dos estudantes para otimizar os investimentos em novos conteúdos.

---

## 2. Evidência (Os Dados Observados)
Com base nas visões analíticas geradas e conectadas ao nosso dashboard no Apache Superset, isolamos três métricas-chave sequenciais para análise:

1. **Volume por Categoria Temática:** O catálogo possui uma forte concentração em conteúdos de *Engenharia de Dados* e *Ciência de Dados*.
2. **Avaliação Média dos Usuários:** O score geral de satisfação da plataforma está consolidado em **4.53 estrelas**. As categorias de *Machine Learning* e *Infraestrutura de IA* apresentam as maiores notas médias (4.82), enquanto *Fundamentos de Banco de Dados* apresenta a menor média (3.62).
3. **Métrica de Retenção (Fato Técnico):** Ao analisarmos o funil de progresso, descobrimos um volume de **105 registros em quarentena** onde usuários tentaram atribuir avaliações pontuais a cursos que apresentavam `percentual_conclusao` inferior a 100%.

---

## 3. Descoberta (A Análise e as Hipóteses)
Cruzando as evidências estatísticas obtidas nas tabelas consolidadas, chegamos às seguintes conclusões:

* **Hipótese de Fadiga do Material:** A baixa nota média em *Fundamentos de Banco de Dados* (3.62) correlaciona-se com um tempo de consumo excessivamente alto nas primeiras interações. Isso levanta a hipótese de que o material didático atual está denso, cansativo ou desalinhado com o nível técnico inicial esperado pelos estudantes, provocando frustração precoce.
* **Comportamento de Engajamento Precoce:** Os 105 registros isolados na quarentena provam que existe uma tendência clara de o usuário tentar avaliar ou interagir de forma definitiva com o conteúdo antes mesmo de consumi-lo integralmente. Isso valida a necessidade de manter a trava de quarentena ativa no Apache Hop para impedir que o viés de avaliações parciais polua as métricas reais de qualidade da plataforma.

---

## 4. Ação Recomendada (Direcionamento Estratégico)
Com o suporte da narrativa baseada em dados, recomendamos as seguintes decisões de negócio para a diretoria executiva:

1. **Reformulação Prioritária:** Auditar e segmentar a trilha de *Fundamentos de Banco de Dados*. Sugere-se quebrar a carga horária em módulos menores e dinâmicos para reduzir a taxa de abandono identificada.
2. **Direcionamento de Orçamento:** Alocar 60% do orçamento do próximo trimestre para a produção de conteúdos avançados nas verticais de *Machine Learning* e *Infraestrutura de IA*, aproveitando a alta tração e satisfação explícita medida na camada Gold.
3. **Gamificação do Progresso:** Implementar uma trava de interface na plataforma (front-end), replicando a nossa regra de qualidade do backend, impedindo que o aluno clique na caixa de avaliação antes de atingir 100% da barra de progresso do curso.
