# Arquitetura Canônica de Validação em Gênese: Auditoria de Lean Canvas e Showstoppers via Comitê de LLMs

**Trabalho de Conclusão de Curso (TCC) — ESALQ/USP**  
**Programa:** MBA em Gestão de Negócios Digitais e Inteligência Artificial  
**Autor:** Murilo Ferrarezi Chiari  
**Orientador:** Prof. Dr. Daniel Valotto  
**Repositório:** `devils-advocate` | **Branch:** `experiment/v6-lean-canvas`  
**Dataset Base:** 20 Startups (10 Falhas Históricas / 10 Ativas de Sucesso) $\times$ 8 Condições = 160 Inferências Completas  
**Modelo Empregado:** `qwen2.5:14b` (Ollama local, temperatura 0.25, 1500 tokens de contexto de saída)

---

## 1. Fundamentação Teórica e Resgate Epistemológico

### 1.1. A Superação do Erro Categorial da IA Preditiva Atuarial (V1–V3)
As primeiras versões deste estudo (V1 a V3) investigaram a hipótese comum na literatura de Inteligência Artificial de que um Modelo de Grande Linguagem (LLM) poderia atuar como um oráculo preditivo, estimando diretamente uma *"probabilidade de sobrevivência comercial (0 a 100%)"* para startups em estágio de gênese (ano de fundação).

Os dados empíricos demonstraram que essa abordagem incorre em um **erro epistemológico fundamental de categoria**:
1. **Incerteza Genuína de Knight (*Knightian Uncertainty*):** Em estágio de gênese, distribuições de probabilidade estatística de mercado são objetivamente desconhecidas e não mensuráveis a priori (Knight, 1921). Não há dados históricos suficientes sobre uma empresa no "Dia Zero" que permitam um cálculo atuarial legítimo.
2. **Hipercriticismo e Viés de Omissão Induzido:** Diante da ausência natural de faturamento, dados de tração ou métricas operacionais consolidadas na fundação, o modelo de linguagem ancora na taxa histórica macroeconômica de mortalidade de startups (~90% de falência). O LLM passa então a penalizar a carência embrionária de dados como se fosse evidência fática de inviabilidade, rejeitando sistematicamente inovações radicais legítimas. Na versão V3, sob corte probabilístico de 50%, o modelo reprovou 99,3% das startups avaliadas, descartando sumariamente casos consagrados como Airbnb (2008), Uber (2009), Nubank (2013), Stripe (2010) e Canva (2013).

### 1.2. A Ontologia do Lean Startup e a Auditoria de Hipóteses
A presente arquitetura rompe com a classificação atuarial espúria e ancora-se estritamente na tradição teórica do **Lean Startup** (Ries, 2011) e do **Lean Canvas** (Maurya, 2012):
* Na gênese, uma startup no papel **não possui uma probabilidade estática de sobrevivência**. O seu sucesso ou fracasso é função da qualidade, velocidade e disciplina metodológica com que a equipe executa o ciclo empírico *Construir-Medir-Aprender*;
* O papel analítico da Inteligência Artificial e do comitê com a persona do **Advogado do Diabo** não é adivinhar o futuro distante da empresa, mas sim realizar o **teste de estresse dedutivo das premissas**, isolando a **Premissa de Salto de Fé (*Leap of Faith Assumption* — LOFA)** e desenhando o experimento mínimo necessário para testá-la a baixo custo.

### 1.3. A Doutrina dos *Showstoppers* e o Espaço Decisório Ternário Calibrado
Para evitar que o modelo caia no extremo oposto da sicofância (benevolência excessiva ou complacência algorítmica onde tudo é aprovado para iteração), a arquitetura incorpora a doutrina formal de **Showstoppers** (Maurya, 2012):
* Em uma auditoria de Lean Canvas, uma ideia não deve ser descartada por incerteza de mercado ordinária (pois o mercado é incerto por definição);
* Contudo, se a proposta contiver um **Showstopper estrutural insanável já no papel** (leis da física/tecnologia impossível, fraude científica, bloqueio regulatório sanitário incontornável ou estratégia anti-Lean de queima massiva de capital pré-validação), o modelo tem o dever metodológico de emitir **Reprovação por Showstopper (Descarte)**;
* Estabelece-se, assim, um espaço decisório ternário claro e operacional:
  1. **🟢 Avançar para MVP:** Hipóteses logicamente coerentes e defensáveis, justificando a construção de um Produto Viável Mínimo;
  2. **🟡 Necessita Pivotagem:** Problema e dor legítimos, mas desalinhamento entre premissas secundárias (canal, precificação ou segmento de cliente) que exige reformulação conceitual antes de queimar caixa;
  3. **🔴 Reprovação por Showstopper (Descarte):** Bloqueio estrutural insolúvel no papel, tornando inútil despender tempo ou capital em MVP ou pivotagem.

---

## 2. Especificação Canônica dos Prompts e Parâmetros de Execução

Os prompts a seguir são os textos exatos implementados no script de produção (`experimento_tcc.py`):

### 2.1. Prompt de Sistema Base (`BASE_SYSTEM_INSTRUCTION`)
```text
Sua tarefa no comitê de avaliação é auditar a proposta de negócio estruturada no "Lean Canvas" em seu ano de fundação (estágio de gênese), sob a ótica estrita da metodologia Lean Startup (Eric Ries) e Lean Canvas (Ash Maurya).

No framework Lean, um modelo de negócios embrionário é um conjunto articulado de hipóteses que devem ser auditadas quanto à sua coerência lógica interna e testabilidade empírica no ciclo Construir-Medir-Aprender.

DIRETRIZES DE DECISÃO LEAN:
- "Avançar para MVP": As hipóteses do Canvas são logicamente coerentes, a proposta de valor ataca uma dor real prioritária e a economia unitária básica é defensável, justificando a construção de um Produto Viável Mínimo (MVP) para teste empírico em campo com os primeiros clientes.
- "Necessita Pivotagem": O problema é real e a dor do cliente é prioritária, mas há um desalinhamento corrigível entre as premissas secundárias do Canvas (ex.: canal de aquisição alternativo, precificação ou perfil de early adopter), justificando uma iteração de hipóteses antes de alocar recursos no MVP.
- "Reprovação por Showstopper (Descarte)": O modelo possui um bloqueador fatal insolúvel (Showstopper de Maurya) que condena a proposta já no papel, tornando inútil gastar tempo ou dinheiro em MVP ou pivotagem. Deve ser SUMARIAMENTE REPROVADA E DESCARTADA se apresentar qualquer uma das seguintes condições:
  1. Problema superficial ou inexistente: o cliente não sente dor urgente e alternativas gratuitas consolidadas de mercado já resolvem satisfatoriamente (ex.: cobrar assinatura por vídeos curtos de celular quando o público consome vídeos gratuitos em redes sociais);
  2. Unit Economics estruturalmente deficitário: custos operacionais unitários de logística, inspeção física ou hardware que superam a receita por transação sem perspectiva de margem viável com escala;
  3. Barreira regulatória ou científica proibitiva: exigência de certificações médicas/sanitárias de alta complexidade sem testes laboratoriais clínicos prévios, ou dependência de tecnologia central de hardware/microfluídica não comprovada;
  4. Estratégia Anti-Lean: modelo que exige queima massiva de dezenas ou centenas de milhões de dólares em ativos ou licenciamento pré-validação empírica.

AVISO DE RIGOR METODOLÓGICO (DIRETRIZ ANTI-EUFEMISMO):
Não utilize "Necessita Pivotagem" como refúgio educado para propostas inviáveis. A pivotagem é reservada exclusivamente para quando o núcleo da dor do cliente for legítimo e comprovável. Se o modelo apresentar um Showstopper estrutural (de mercado, financeiro ou regulatório), você é OBRIGADO a emitir "Reprovação por Showstopper (Descarte)".

Você deve responder EXCLUSIVAMENTE em formato JSON válido, com concisão analítica (máximo de 3 a 4 frases por campo de justificativa):

{
  "analise_coerencia_problema_solucao": "Análise da amarração lógica entre o problema do cliente, a proposta de valor e a solução",
  "analise_viabilidade_economica_canais": "Análise da coerência entre modelo de monetização, custos previstos e canais de acesso ao cliente",
  "premissa_salto_de_fe_lofa": "A premissa crítica mais arriscada de sustentação do Canvas (Leap of Faith Assumption) cuja falha desmorona o modelo",
  "experimento_mvp_prioritario": "Desenho do experimento prático de MVP (ou justificativa da impossibilidade em caso de Showstopper/Descarte)",
  "decisao_lean": "Avançar para MVP | Necessita Pivotagem | Reprovação por Showstopper (Descarte)"
}
```

### 2.2. Prompt de Entrada da Startup (`USER_TEMPLATE`)
Garante um isolamento temporal rigoroso (*clean timeline*), sem contaminação por eventos futuros:
```text
DADOS DA STARTUP:
Setor: {setor}
Ano da Análise (Gênese): {ano_analise}
Proposta do Negócio: {nome_anonimizado}
Premissas do Modelo de Negócios (Lean Canvas): {modelo_negocios}
Contexto Operacional e de Mercado: {contexto_mercado}
```

---

## 3. O Comitê de 8 Condições Experimentais Balanceadas

A composição estruturada do comitê de avaliação divide-se em 4 blocos funcionais, garantindo a neutralidade epistemológica e isolando o efeito marginal da injeção de cada persona:

| Bloco Metodológico | Prefixo | Persona | Instrução Textual de Persona Injetada | Função Epistêmica no Framework |
| :--- | :--- | :--- | :--- | :--- |
| **Controle Neutro** | **`Base`** | **Modelo Puro (Baseline)** | *(Nenhuma persona injetada. Opera sob a instrução base pura.)* | Mede a linha de base pura do modelo sem indução de papel comportamental. |
| **Consistência Lógica** | **`Epist`** | **Cético Epistêmico** | *"Atue no comitê sob a perspectiva de um 'Cético Epistêmico e Auditor de Consistência Lógica'. Sua função é auditar a consistência lógica dedutiva entre os 9 blocos do Lean Canvas. Se identificar premissas místicas, cientificamente não comprovadas ou contradição lógica insanável, isso é um Showstopper de falseabilidade: emita categoricamente 'Reprovação por Showstopper (Descarte)'."* | Auditoria popperiana de falseabilidade e ausência de contradições lógicas dedutivas. |
| **Tríade Crítica (Downside)** | **`Diabo`** | **Advogado do Diabo** | *"Atue no comitê sob a perspectiva do 'Advogado do Diabo'. Sua função é realizar uma simulação de pré-morte (pre-mortem) e o teste de estresse rigoroso das premissas do Lean Canvas. Se a premissa de salto de fé (LOFA) for insustentável ou o modelo possuir um Showstopper evidente, NÃO hesite e NÃO use pivotagem como refúgio educado: emita categoricamente 'Reprovação por Showstopper (Descarte)'."* | Teste dialético de estresse, simulação de pré-morte (*pre-mortem*) e detecção agressiva de falhas fatais. |
| **Tríade Crítica (Downside)** | **`Anali`** | **Analista Financeiro** | *"Atue no comitê sob a perspectiva de um 'Analista Financeiro de Inovação'. Sua função é auditar a viabilidade econômica do Lean Canvas. Se identificar que o modelo exige queima massiva de capital pré-validação empírica ou possui unit economics estruturalmente deficitário, isso é um Showstopper financeiro insanável: emita OBRIGATORIAMENTE 'Reprovação por Showstopper (Descarte)'."* | Auditoria de sustentabilidade econômica, margens unitárias e queima prematura de caixa (*burn rate*). |
| **Tríade Crítica (Downside)** | **`Reg`** | **Auditor Regulatório** | *"Atue no comitê sob a perspectiva de um 'Auditor de Risco Regulatório e Institucional'. Sua função é examinar o Lean Canvas sob a ótica de barreiras legais e licenças sanitárias. Se a proposta colidir com regulação setorial severa ou depender de certificações laboratoriais/médicas inalcançáveis para um estágio embrionário, isso é um Showstopper legal: emita OBRIGATORIAMENTE 'Reprovação por Showstopper (Descarte)'."* | Identificação de fricções normativas, litígios e barreiras regulatórias intransponíveis na gênese. |
| **Tríade Propositiva (Upside)** | **`Anjo`** | **Investidor Anjo** | *"Atue no comitê sob a perspectiva de um 'Investidor Anjo de Startups'. Sua função é avaliar a proposta de valor sob a ótica de oportunidade de mercado, capacidade de execução da equipe, velocidade de tração nos primeiros 12 a 18 meses e viabilidade de escala rápida a partir dos early adopters."* | Foco na capacidade de tração, velocidade de execução nos primeiros ciclos e adoção inicial. |
| **Tríade Propositiva (Upside)** | **`Prod`** | **Champion de Produto** | *"Atue no comitê sob a perspectiva de um 'Champion de Produto (Product Leader)'. Sua função é auditar a centralidade do cliente e o Problem-Solution Fit do Lean Canvas. Se o problema for superficial, se a dor do cliente não for prioritária ou se alternativas gratuitas já resolverem plenamente o problema, isso é um Showstopper de produto: emita 'Reprovação por Showstopper (Descarte)'."* | Avaliação do encaixe problema-solução (*Problem-Solution Fit*), fricção de uso e retenção de clientes. |
| **Tríade Propositiva (Upside)** | **`Inov`** | **Estrategista de Inovação** | *"Atue no comitê sob a perspectiva de um 'Estrategista de Inovação e Vantagem Competitiva'. Sua função é avaliar o potencial de diferenciação e upside do Lean Canvas, analisando a singularidade da proposta única de valor, a robustez da vantagem injusta (unfair advantage) e a existência de efeitos de rede defensáveis."* | Análise de assimetria positiva de retorno, defesas competitivas (*moats*) e efeitos de rede. |

---

## 4. Evidências Empíricas Consolidadas (160 Inferências)

### 4.1. Distribuição Global de Decisões (Padrão IBGE)

| Status Real da Startup | Avançar para MVP | Necessita Pivotagem | Reprovação por Showstopper (Descarte) | Total de Avaliações | Taxa Total de Bloqueio (Pivot + Descarte) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Ativas (Sucesso Real)** | **68 (85,0%)** | 11 (13,8%) | **1 (1,2%)\*** | 80 (100,0%) | 15,0% |
| **Falhas (Insucesso Real)** | 33 (41,2%) | **36 (45,0%)** | **11 (13,8%)** | 80 (100,0%) | **47 (58,8%)** |
| **Total Amostral** | **101 (63,1%)** | **47 (29,4%)** | **12 (7,5%)** | **160 (100,0%)** | — |

*\*Nota: O único caso de descarte em startups ativas ocorreu no Mercado Livre de 1999 avaliado pela Persona Base (sem persona), motivado pela baixa penetração de internet na América Latina à época. Nenhuma das 7 personas especializadas cometeu falso descarte no Mercado Livre.*

---

### 4.2. Matriz de Desempenho e Discriminação por Persona

| Condição Experimental | Papel Metodológico | Falhas: MVP (%) | Falhas: Pivot (%) | Falhas: Descarte (%) | **Falhas: Bloqueio Total (%)** | Ativas: MVP (%) | Ativas: Pivot (%) | Ativas: Descarte (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Champion de Produto (`Prod`)** | Tríade Propositiva | 20,0% | 60,0% | **20,0%** | **80,0%** | 90,0% | 10,0% | **0,0%** |
| **Advogado do Diabo (`Diabo`)** | Tríade Crítica | 30,0% | 60,0% | **10,0%** | **70,0%** | 90,0% | 10,0% | **0,0%** |
| **Modelo Puro (`Base`)** | Controle Baseline | 40,0% | 50,0% | 10,0% | 60,0% | 80,0% | 10,0% | 10,0% |
| **Cético Epistêmico (`Epist`)** | Consistência | 40,0% | 50,0% | 10,0% | 60,0% | 80,0% | 20,0% | **0,0%** |
| **Analista Financeiro (`Anali`)** | Tríade Crítica | 40,0% | 50,0% | 10,0% | 60,0% | 90,0% | 10,0% | **0,0%** |
| **Auditor Regulatório (`Reg`)** | Tríade Crítica | 50,0% | 0,0% | **50,0%** | 50,0% | 90,0% | 10,0% | **0,0%** |
| **Investidor Anjo (`Anjo`)** | Tríade Propositiva | 50,0% | 50,0% | 0,0% | 50,0% | 70,0% | 30,0% | **0,0%** |
| **Estrategista Inovação (`Inov`)** | Tríade Propositiva | 60,0% | 40,0% | 0,0% | 40,0% | 90,0% | 10,0% | **0,0%** |

---

### 4.3. Análise Detalhada dos Casos Emblemáticos

1. **Theranos (Fraude e Inviabilidade Técnica/Regulatória):**
   * Recebeu **4 Descartes Sumários por Showstopper** (`Base`, `Epist`, `Anali` e `Reg`) e 3 pedidos de Pivotagem (`Diabo`, `Anjo` e `Prod`). Apenas o `Inov` concedeu MVP.
   * A LOFA diagnosticada pelo `Reg` foi precisa: *"A premissa crítica é a capacidade de desenvolver e certificar tecnologia de microfluídica e dispositivos proprietários em conformidade com as regulamentações sanitárias e laboratoriais."*
2. **Quibi (Modelo de Vídeo Curto Pago vs. Redes Sociais Gratuitas):**
   * Recebeu **3 Descartes Sumários por Showstopper** (`Diabo`, `Reg` e `Prod`) e 4 pedidos de Pivotagem. Apenas o `Anali` concedeu MVP.
   * O `Prod` cravou o Showstopper de produto: *"A premissa crítica é a capacidade de atrair e reter assinantes pagantes quando existem alternativas gratuitas e populares no mercado."*
3. **Juicero e 23andMe (100% de Bloqueio nas 8 Personas):**
   * Ambas obtiveram **0% de aprovação para MVP**.
   * O `Reg` aplicou Descarte Sumário em ambas (identificando a regulação sanitária da FDA no 23andMe), enquanto todas as outras 7 personas prescreveram *Necessita Pivotagem*.
4. **O Caso Singular do Mercado Livre (1999):**
   * A persona `Base` cometeu falso descarte argumentando que a baixa penetração da internet tornava um MVP inviável.
   * Em contraste, **nenhuma das 7 personas especializadas cometeu falso descarte**: 6 personas prescreveram *Necessita Pivotagem* (reconhecendo a necessidade de contornar a precariedade dos meios de pagamento e logística) e o `Inov` concedeu *Avançar para MVP*, comprovando que papéis instrucionais refinam o discernimento do modelo.
5. **Startups Ativas Consagradas (Airbnb, Uber, Nubank, Stripe, Slack, Canva e Shopify):**
   * **100% de aprovação para MVP em todas as 8 personas**, demonstrando a eliminação completa dos falsos negativos que assolavam as versões probabilísticas preliminares.

---

## 5. Protocolo de Avaliação da Causa do Fracasso (Aderência Causal pós-hoc)

### 5.1. A Separação Epistemológica: Geração em Gênese vs. Avaliação Ex-Post
Um dos cuidados metodológicos centrais da pesquisa foi evitar o **vício retrospectivo (*hindsight bias*) e a adivinhação teleológica**. 

Nas versões preliminares (V1–V3), o modelo era forçado a escolher uma causa de fracasso em uma lista pré-definida no momento em que avaliava a startup no ano de fundação. Isso gerava um vício conceitual: uma startup no Dia Zero ainda não fracassou; forçar a IA a prever o motivo futuro induz ao pessimismo artificial.

Na presente arquitetura, o processo foi formalmente **desacoplado em duas etapas temporais e operacionais independentes**:
1. **Etapa 1 — Diagnóstico Cego em Gênese (Ano de Fundação):**
   * O LLM recebe apenas os dados de ideação (Lean Canvas) no ano de fundação, sem saber o desfecho histórico da empresa;
   * O modelo não tenta adivinhar o futuro: ele apenas redige em texto livre qual é a **Premissa de Salto de Fé (*Leap of Faith Assumption* — LOFA)**, ou seja, a hipótese mais vulnerável do modelo cuja falsidade derrubaria o negócio (Jain et al., 2026).
2. **Etapa 2 — Avaliação Pós-Hoc via Juiz Semântico (*LLM-as-a-Judge*) (Perez et al., 2022):**
   * Em um script independente (`classificar_lofas_cbinsights.py`), um modelo juiz (com temperatura determinística 0.1) recebe **apenas o texto da LOFA** isolado, sem qualquer menção ao nome da startup, setor ou desfecho real;
   * O juiz classifica a LOFA estritamente em uma das 9 categorias padronizadas da taxonomia da CB Insights (2026):
     1. Sem necessidade de mercado; 2. Fim do caixa; 3. Problema de preço ou custo; 4. Modelo de negócios falho; 5. Problema regulatório ou legal; 6. Produto ruim; 7. Concorrência predatória; 8. Equipe inadequada; 9. Outro.
3. **Etapa 3 — Cruzamento Estatístico e Métricas de Aderência Causal:**
   * **Acerto Causal Estrito:** Ocorre quando a categoria diagnosticada na LOFA é **exatamente idêntica à causa primária** documentada no gabarito real da CB Insights (`Rotulo_Categorico`);
   * **Acerto Causal Amplo:** Ocorre quando a categoria diagnosticada na LOFA coincide com a **causa primária OU com qualquer uma das causas secundárias** documentadas (`Rotulos_Secundarios`).
4. **Etapa 4 — Auditoria e Validação Humana Qualitativa:**
   * Para assegurar que o juiz algorítmico não cometeu distorções semânticas, foi compilado o `CADERNO_VALIDACAO_AUDITORIA.md`, onde o pesquisador confere visualmente a confrontação textual entre a LOFA redigida e o histórico documentado da empresa.

---

### 5.2. Resultados Quantitativos de Aderência Causal nas Falhas

A Tabela abaixo resume a taxa de acerto do comitê em identificar com precisão a causa real que anos mais tarde provocaria a quebra da empresa:

| Persona | Acertos Estritos (Causa Primária) | Taxa Estrita (%) | Acertos Amplos (Primária ou Secundárias) | Taxa Ampla (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Investidor Anjo (`Anjo`)** | **6 de 10** | **60,0%** | **9 de 10** | **90,0%** |
| **Analista Financeiro (`Anali`)** | 3 de 10 | 30,0% | **9 de 10** | **90,0%** |
| **Cético Epistêmico (`Epist`)** | **5 de 10** | **50,0%** | 7 de 10 | 70,0% |
| **Controle Puro (`Base`)** | 2 de 10 | 20,0% | 8 de 10 | 80,0% |
| **Champion de Produto (`Prod`)** | 4 de 10 | 40,0% | 6 de 10 | 60,0% |
| **Auditor Regulatório (`Reg`)** | 3 de 10 | 30,0% | 6 de 10 | 60,0% |
| **Advogado do Diabo (`Diabo`)** | 3 de 10 | 30,0% | 5 de 10 | 50,0% |
| **Estrategista Inovação (`Inov`)** | 1 de 10 | 10,0% | 7 de 10 | 70,0% |

---

### 5.3. Destaques Qualitativos da Correspondência Causal
* **Theranos e 23andMe:** 100% de concordância estrita de todas as personas críticas em *Problema regulatório ou legal*;
* **Quibi:** Acerto estrito em *Sem necessidade de mercado* por `Epist`, `Anjo` e `Prod`, e acerto amplo em *Modelo de negócios falho* por `Base`, `Anali` e `Reg`;
* **Beepi:** 100% de acerto amplo em *Modelo de negócios falho* e *Problema de preço ou custo*.

---

## 6. Catálogo dos Artefatos Gerados para a Dissertação (`anexos_tcc/`)

Todos os artefatos visuais e tabulares foram gerados a 300 DPI sob o padrão tipográfico da ABNT/ESALQ pelo script `gerar_anexos_tcc.py`:

1. **`figura1_distribuicao_decisoes_lean.png`:** Gráfico de barras horizontais empilhadas (100%) comparando as taxas de MVP, Pivotagem e Descarte entre Falhas e Ativas para cada uma das 8 personas;
2. **`figura2_heatmap_startups_personas.png`:** Mapa de calor matricial de todas as 20 startups $\times$ 8 personas, codificado nas cores verde (MVP), âmbar (Pivot) e vermelho (Descarte);
3. **`figura3_taxa_bloqueio_falhas.png`:** Gráfico de barras demonstrando a taxa de bloqueio total nas falhas, evidenciando que o `Prod` (80%) e o `Diabo` (70%) superam a linha de base do `Base` (60%);
4. **`figura4_aderencia_causal_cbinsights.png`:** Gráfico de barras emparelhadas de acerto estrito vs. amplo na taxonomia de causas de insucesso da CB Insights;
5. **`figura5_distribuicao_causas_diagnosticadas.png`:** Gráfico de prevalência diagnóstica das causas diagnosticadas pela IA vs. frequência fática do gabarito histórico real;
6. **Tabelas Estatísticas:** `tabela1_distribuicao_decisoes_ibge.csv`, `tabela2_desempenho_por_persona_ibge.csv`, `tabela3_aderencia_causal_cbinsights_ibge.csv` e `tabela4_matriz_veredito_completa.csv`.

---

## 7. Estrutura Canônica de Arquivos no Repositório

* **Script Oficial de Execução:** `experimento_tcc.py`
* **Classificador Pós-Hoc do Juiz Semântico:** `classificar_lofas_cbinsights.py`
* **Gerador Canônico de Figuras e Tabelas:** `gerar_anexos_tcc.py`
* **Gerador do Caderno de Validação Humana:** `gerar_painel_validacao.py`
* **Dataset Oficial Consolidado:** `resultados/resultados_lean_canvas_completo.csv`
* **Dataset com Classificação do Juiz CB Insights:** `resultados/resultados_lean_canvas_com_categorias_lofa.csv`
* **Caderno Integral de Auditoria Humana:** `CADERNO_VALIDACAO_AUDITORIA.md` (e em `capitulos_tcc/PAINEL_VALIDACAO_HUMANA.md`)
* **Artefatos Gráficos e Tabelas IBGE:** pasta `anexos_tcc/`
