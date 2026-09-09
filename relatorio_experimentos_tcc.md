# Relatório de Experimentos: Calibração de Prompts e Julgamento de LLMs na Validação de Startups

## 1. Contexto e Objetivo
- **Pesquisa:** TCC ESALQ/USP (Gestão de Negócios e IA).
- **Objetivo:** Avaliar modelos de negócios em fase de gênese (*Lean Canvas* no ano de fundação) usando LLM local (*qwen2.5:14b* via Ollama) sob comitê de 7 personas, com ênfase no papel do **Advogado do Diabo**.
- **Dataset:** 20 startups históricas anonimizadas (10 sucessos reais como Airbnb/Uber; 10 fracassos/fraudes reais como Quibi/Theranos).
- **Comitê de Personas:** Con (Neutro), Gen (Consultor), Diabo (Estresse dialético), Anali (Financeiro), Anjo (Tração), Epist (Lógica dedutiva), Reg (Risco legal).

---

## 2. As Quatro Arquiteturas Testadas e Resultados Empíricos

### V2: Baseline Agnóstica (3 categorias textuais)
- **Veredito:** Aprovado | Necessita Pivotagem | Reprovado.
- **Resultado:** **Colapso Central de 95% em "Necessita Pivotagem"** (hedging por aversão ao conflito decorrente do RLHF).

### V3: Binária Estrita + Ancoragem Conservadora (20 startups completas, 140 chamadas)
- **Veredito:** Go ou No-Go forçado (instrução de base-rate conservador).
- **Resultado:**
  - **Especificidade de 100%:** Todas as 10 falhas/fraudes rejeitadas como No-Go ($P \approx 30\% - 36\%$).
  - **Ordenação das Personas Perfeita:** Diabo mais severo (30.0%), seguido por Epist/Reg (36.1%), Con (36.9%), Anali (40.3%), Anjo (41.1%) e Gen (42.8%).
  - **Patologia (Hipercriticismo / Viés de Omissão):** Airbnb e Uber também foram reprovados como No-Go ($P \approx 38\% - 42\%$), pois a ausência natural de métricas em gênese foi tratada como falha fatal.

### V4: Meio-Termo com Hard-Stops e Incerteza Legítima (Piloto 4 startups: Quibi, Theranos, Airbnb, Uber)
- **Veredito:** Go | Go Condicional / Pivotar | No-Go (meta-norma: incerteza vai para validação; No-Go só para inviabilidade científica/econômica manifesta).
- **Resultado:**
  - **Colapso Textual de 100%:** 28 de 28 chamadas deram "Go Condicional / Pivotar". Para Theranos, a IA escreveu que a falha de engenharia era "bloqueio fatal" e deu probabilidade de 30%, mas o filtro de RLHF impediu de escrever a palavra "No-Go".
  - **Probabilidade Contínua:** Theranos 36.4%, Quibi 50.0%, Airbnb 45.7%, Uber 47.1%.

### V5: Rubricas Ortogonais Decompostas (5 notas 1 a 5 + Motor Python)
- **Método:** LLM pontua 5 rubricas (Dor, Técnica, Capital, Legal, Lean MVP). Probabilidade e veredito calculados externamente via Python.
- **Resultado:** **Armadilha Compensatória Aditiva**. Quibi recebeu nota 5 em viabilidade técnica de software e 5 em lean MVP, gerando score de 76% (Go). Critérios técnicos triviais mascararam a ausência fatal de demanda.

---

## 3. As Três Patologias Mapeadas
1. **V3 (Binária):** Hipercriticismo e Viés de Omissão (elimina fraudes, mas mata inovações legítimas).
2. **V4 (Graduada Textual):** Hesitação de RLHF e Aversão ao Conflito (mesmo com risco fatal, recusa-se a emitir No-Go em texto).
3. **V5 (Rubricas Aditivas):** Compensação Aditiva (notas fáceis em tecnologia mascaram inviabilidade de negócio).

---

## 4. Questões Estratégicas para Discussão
1. Faz mais sentido para a dissertação adotar a V3 (já 100% finalizada com as 20 startups) como o resultado principal da tese e usar os achados da V4 e V5 como um capítulo rico de discussão metodológica sobre as patologias de LLMs?
2. Ou vale a pena refinar a V4 (usando apenas a probabilidade contínua com limiar numérico externo em Python, sem pedir veredito textual) ou a V5 (com modelo não-linear/multiplicativo)?
3. Qual abordagem confere maior valor científico perante uma banca de TCC/Mestrado da USP?
