# Arquitetura V6: Validação de Modelos de Negócio em Gênese via Lean Canvas e Auditoria Multi-Agente (LLM)

**Trabalho de Conclusão de Curso (TCC) — ESALQ/USP**  
**Programa:** MBA em Gestão de Negócios Digitais e Inteligência Artificial  
**Autor:** Murilo Ferrarezi Chiari  
**Orientador:** Prof. Dr. Daniel Valotto  
**Repositório:** `devils-advocate` | **Branch:** `experiment/v6-lean-canvas`

---

## 1. Fundamentação Teórica e Motivação Metodológica

### 1.1. O Conflito Epistemológico entre IA Preditiva e Metodologia Lean
Estudos tradicionais que aplicam modelos de linguagem (LLMs) ou algoritmos de Machine Learning à avaliação de startups costumam tratar o problema como uma **classificação preditiva atuarial**, exigindo que a IA atribua uma *"probabilidade de sobrevivência (0 a 100%)"*.

Nossos experimentos preliminares (V1 a V3) demonstraram que exigir uma estimativa probabilística de sobrevivência para uma startup em estágio de gênese (ano de fundação) incorre em um **erro de categoria epistemológico**:
1. **Incerteza de Knight (*Knightian Uncertainty*):** Em estágio embrionário, as distribuições de probabilidade de mercado são desconhecidas e não mensuráveis a priori (Knight, 1921). 
2. **Viés de Omissão e Hipercriticismo:** Diante da ausência natural de dados de tração, faturamento ou métricas consolidadas no ano de fundação, o LLM ancora na taxa histórica de mortalidade do ecossistema (~90% de falhas) e passa a penalizar a falta de dados como se fosse evidência de inviabilidade, rejeitando sistematicamente inovações radicais legítimas (ex.: Airbnb em 2008 e Uber em 2009 foram sumariamente reprovados na V3).

### 1.2. O Resgate da Ontologia do Lean Startup e Lean Canvas
A **Arquitetura V6** substitui o paradigma de previsão probabilística atuarial pela **auditoria lógica de hipóteses** preconizada pelo *Lean Startup* (Ries, 2011) e pelo *Lean Canvas* (Maurya, 2012):
* Um modelo de negócios no papel **não possui uma taxa estática de sobrevivência no dia zero**. A sobrevivência depende da velocidade e qualidade do ciclo *Construir-Medir-Aprender*.
* O papel do LLM e das personas adversariais (em especial o **Advogado do Diabo**) não é funcionar como um oráculo preditivo de sucesso futuro, mas sim como um **auditor de estresse de premissas**, identificando a **Hipótese de Salto de Fé (*Leap of Faith Assumption* - LOFA)** e avaliando a coerência interna entre as 9 caixas do Canvas.

---

## 2. Especificação Exata dos Prompts da V6

Os prompts abaixo são reproduzidos **ipsis litteris** como estão implementados no código executável oficial (`experimento_tcc.py`):

### 2.1. Prompt de Sistema Base (`SYSTEM_TEMPLATE`)

```text
{instrucao_persona}

Sua tarefa no comitê de avaliação é auditar a proposta de negócio estruturada no "Lean Canvas" em seu ano de fundação (estágio de gênese), sob a ótica estrita da metodologia Lean Startup (Eric Ries) e Lean Canvas (Ash Maurya).

No framework Lean, um modelo de negócios embrionário é um conjunto articulado de hipóteses que devem ser auditadas quanto à sua coerência lógica interna e testabilidade empírica no ciclo Construir-Medir-Aprender.

DIRETRIZES DE DECISÃO LEAN:
- "Avançar para MVP": As hipóteses do Canvas são logicamente coerentes e a proposta de valor é plausível, justificando a construção de um Produto Viável Mínimo (MVP) para teste empírico em campo.
- "Necessita Pivotagem": O problema é real, mas existe um desalinhamento crítico entre as premissas do Canvas (ex.: canal incompatível, modelo de receita que repele o público-alvo ou atrito de adoção insustentável), exigindo redesenho de hipóteses antes de alocar recursos.
- "Descarte por Inviabilidade Estrutural": O modelo possui um bloqueio fatal insanável (premissa central que contraria leis científicas/físicas sem validação prévia, ilegalidade manifesta insuperável, ou estratégia anti-Lean que exige queima massiva de centenas de milhões de dólares antes de validar qualquer demanda).

Você deve responder EXCLUSIVAMENTE em formato JSON válido, com concisão analítica (máximo de 3 a 4 frases por campo de justificativa):

{{
  "analise_coerencia_problema_solucao": "Análise da amarração lógica entre o problema do cliente, a proposta de valor e a solução",
  "analise_viabilidade_economica_canais": "Análise da coerência entre modelo de monetização, custos previstos e canais de acesso ao cliente",
  "premissa_salto_de_fe_lofa": "A premissa crítica mais arriscada de sustentação do Canvas (Leap of Faith Assumption) cuja falha desmorona o modelo",
  "experimento_mvp_prioritario": "Desenho do experimento prático ou MVP enxuto para validar a LOFA a baixo custo",
  "decisao_lean": "Avançar para MVP | Necessita Pivotagem | Descarte por Inviabilidade Estrutural"
}}
```

---

### 2.2. Prompt de Entrada da Startup (`USER_TEMPLATE`)

Garante um isolamento temporal estrito (*clean timeline*), sem vazamento de informações de futuro (*data leakage*):

```text
DADOS DA STARTUP:
Setor: {setor}
Ano da Análise (Gênese): {ano_analise}
Proposta do Negócio: {nome_anonimizado}
Premissas do Modelo de Negócios (Lean Canvas): {modelo_negocios}
Contexto Operacional e de Mercado: {contexto_mercado}
```

---

## 3. O Comitê de 7 Personas Avaliadoras

Cada persona é avaliada de forma **independente e isolada** (sem deliberação mútua), permitindo analisar a modulação de ceticismo e o foco diagnóstico de cada papel institucional:

| Prefixo | Persona | Instrução Textual Injetada no Prompt (`{instrucao_persona}`) | Papel Epistêmico no Framework Lean |
| :--- | :--- | :--- | :--- |
| **Con** | **Analista Neutro** | *"Atue no comitê de avaliação sob a perspectiva de um 'Analista Neutro de Modelos de Negócios'. Sua função é auditar a coerência intrínseca entre as 9 caixas do 'Lean Canvas', avaliando se as hipóteses de problema, solução e receita formam um sistema equilibrado e não contraditório."* | **Linha de Base (Controle):** Avaliação de consistência interna das 9 caixas sem viés indutivo. |
| **Gen** | **Consultor Geral** | *"Atue no comitê de avaliação sob a perspectiva de um 'Consultor Geral de Negócios'. Sua função é avaliar a atratividade da proposta e a viabilidade de execução do 'Lean Canvas' frente às dinâmicas competitivas e alternativas existentes de mercado."* | **Pragmatismo Comercial:** Foco em alternativas existentes e atratividade frente aos concorrentes. |
| **Diabo** | **Auditor de Estresse (Advogado do Diabo)** | *"Atue no comitê de avaliação sob a perspectiva de um 'Auditor de Teste de Estresse de Premissas'. Sua função é realizar o teste de estresse do 'Lean Canvas', caçando a premissa de salto de fé (LOFA) mais frágil do modelo. Avalie com rigor implacável se essa fraqueza exige pivotagem, descarte imediato ou se pode ser validada em um MVP estrito."* | **Teste Dialético Adversarial:** Caçador implacável de pontos de ruptura estruturais e fragilidades de execução. |
| **Anali** | **Analista Financeiro** | *"Atue no comitê de avaliação sob a perspectiva de um 'Analista Financeiro de Inovação'. Sua função é auditar a sustentabilidade dos unit economics do 'Lean Canvas'. Avalie se a estrutura de custos é proporcional aos estágios de validação ou se impõe uma queima destrutiva de capital pré-validação."* | **Unit Economics & Queima de Caixa:** Prevenção de modelos anti-Lean de alto custo de capital sem validação. |
| **Anjo** | **Avaliador de Tração** | *"Atue no comitê de avaliação sob a perspectiva de um 'Avaliador de Tração e Validação Inicial de Mercado'. Sua função é auditar a urgência da dor do cliente e a eficácia dos canais propostos para capturar e testar os primeiros adotantes (early adopters) com agilidade."* | **Early Adopters & Tração:** Foco na urgência da dor e nos canais de contato inicial com clientes reais. |
| **Epist** | **Auditor de Lógica** | *"Atue no comitê de avaliação sob a perspectiva de um 'Auditor de Lógica e Falseabilidade de Hipóteses'. Sua função é auditar a falseabilidade das premissas do 'Lean Canvas'. Verifique se as hipóteses centrais são passíveis de teste empírico ou se dependem de premissas místicas, cientificamente impossíveis ou auto-imunes."* | **Falseabilidade Popperiana:** Garante que as hipóteses sejam empiricamente testáveis e científicas. |
| **Reg** | **Avaliador de Risco Legal** | *"Atue no comitê de avaliação sob a perspectiva de um 'Avaliador de Risco Regulatório e Institucional'. Sua função é examinar o 'Lean Canvas' sob a ótica de barreiras legais. Diferencie fricções regulatórias normais de inovações de impedimentos legais intransponíveis que inviabilizam o avanço."* | **Risco Institucional e Regulatório:** Auditoria de barreiras legais, conformidade e fricções setoriais. |

---

## 4. Detalhamento dos Campos do Schema JSON de Saída

O formato de saída foi concebido para operacionalizar o ciclo Lean de forma direta e estruturada:

1. **`analise_coerencia_problema_solucao`:** Avalia o *Problem-Solution Fit* teórico. Verifica se a proposta de valor ataca diretamente a dor prioritária declarada.
2. **`analise_viabilidade_economica_canais`:** Avalia o alinhamento de monetização e canais. Analisa se a estrutura de custos proposta não inviabiliza o modelo antes dos primeiros ciclos de aprendizado.
3. **`premissa_salto_de_fe_lofa` (*Leap of Faith Assumption*):** Campo de maior valor qualitativo da pesquisa. Isola a premissa vital mais vulnerável que sustenta o Lean Canvas. Serve para confrontação semântica com o gabarito real de fechamento das startups fracassadas.
4. **`experimento_mvp_prioritario`:** Proposta de experimento prático para testar a LOFA a baixo custo no ciclo Construir-Medir-Aprender, impedindo investimentos cegos.
5. **`decisao_lean`:** A categoria decisória operacional:
   * **Avançar para MVP:** Hipóteses equilibradas e testáveis (Aprovação de validação);
   * **Necessita Pivotagem:** Desalinhamento entre blocos do Canvas que exige reformulação conceitual antes de gastar recursos;
   * **Descarte por Inviabilidade Estrutural:** Falha fatal (científica, legal ou econômica absurda).

---

## 5. Hiperparâmetros e Configuração de Execução

* **Modelo Base:** `qwen2.5:14b` (executado localmente via Ollama para total reprodutibilidade, auditabilidade e ausência de custos por token).
* **Temperatura de Amostragem:** `0.25` (temperatura controlada para garantir respeito estrito à sintaxe JSON, mantendo a consistência lógica analítica).
* **Limite de Tokens (`num_predict`):** `1500` (garante respostas densas, evitando divagações e eliminando gargalos de tempo de processamento).
* **Ambiente de Execução:** Python 3.9+ com biblioteca `requests` e `pandas` em ambiente virtual (`.venv`), salvando saídas incrementais a cada startup processada.

---

## 6. Validação Inicial dos Resultados (Piloto de Controle)

No teste piloto com 4 startups emblemáticas (28 chamadas com `qwen2.5:14b`):
* **S01 - Airbnb (Sucesso Real):** **85,7% das personas (6 de 7)** aprovaram o modelo para **"Avançar para MVP"** (incluindo o Advogado do Diabo).
* **S02 - Uber (Sucesso Real):** **71,4% das personas (5 de 7)** aprovaram o modelo para **"Avançar para MVP"**.
* **F02 - Theranos (Fraude/Falha Científica):** **85,7% das personas (6 de 7)** bloquearam o avanço, carimbando **"Necessita Pivotagem"** devido à falta de comprovação de microfluídica.
* **F01 - Quibi (Falha de Modelo/Mercado):** **43% das personas** exigiram pivotagem e todas as personas orientaram a testar pequenos catálogos em redes sociais em vez de despender US$ 1,75 bilhão.

---

## 7. Questões para Validação na Literatura Acadêmica

Este documento serve de base para consultas à literatura internacional especializada (ex.: *Journal of Business Venturing*, *Entrepreneurship Theory and Practice*, *IEEE Transactions on Engineering Management*):

1. *Em termos de governança decisória em estágio inicial, a taxonomia tripartite de Lean Startup (Avançar para MVP vs. Pivotagem vs. Descarte) é considerada mais aderente e robusta para avaliar Lean Canvas sob incerteza de Knight do que métricas de classificação probabilística binária (Go/No-Go com corte em 50%)?*
2. *De que maneira o emprego de personas analíticas com papéis institucionais definidos (como o Advogado do Diabo) contribui para mitigar a sicofância em LLMs na identificação de premissas de salto de fé (LOFA) sem cair no viés de omissão / hipercriticismo?*
3. *Existe respaldo teórico para classificar a avaliação de hipóteses em gênese como um processo estritamente não-atuarial, no qual a tomada de decisão legítima privilegia a testabilidade empírica a baixo custo em vez da probabilidade prévia de sobrevivência?*
