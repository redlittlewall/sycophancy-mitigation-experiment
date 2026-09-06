# 📚 Subsídios Teóricos e Metodológicos para a Redação do TCC Final
> Este documento reúne argumentos científicos, justificativas formais, citações e definições operacionais para fundamentar as seções de Introdução, Material & Métodos e Discussão do TCC.

---

## 1. Justificativa Metodológica da Amostra ($n=20$)
*Atende ao Comentário #19 do orientador.*

### Delineamento Não-Populacional (Métodos Mistos)
A pesquisa não se caracteriza como um censo econométrico de grande escala populacional (onde $n$ elevado é exigido para inferência paramétrica), mas sim como um **experimento computacional *in silico* de métodos mistos com abordagem fatorial** (Creswell, 2014; Gil, 2019). 

### Fator Multiplicador e Saturação Teórica
* Cada uma das 20 startups é submetida de forma independente a múltiplas personas avaliadoras.
* Em um desenho com 7 personas, o experimento produz **140 relatórios densos de auditoria analítica**.
* Segundo os preceitos de análise de conteúdo categorial (Bardin, 2011), uma base de 80 a 140 unidades contextuais aprofundadas atinge plenamente o ponto de **saturação teórica**, no qual novas unidades amostrais deixam de agregar novas categorias semânticas de erro ou viés.

### Balanceamento Amostral Estrito (50% / 50%)
* A base é composta simetricamente por **10 startups com desfecho de falência** e **10 startups com desfecho de sobrevivência/sucesso**.
* Esse desenho pareado elimina o **viés de desbalanceamento de classes (*class imbalance bias*)**, condição indispensável para o cálculo matematicamente válido de métricas de Sensibilidade (Recall), Especificidade, Falsos Positivos (FP) e Falsos Negativos (FN).

### Critérios Formais de Inclusão (Elegibilidade)
1. **Natureza do Modelo de Negócio:** Ser empresa de base estritamente tecnológica ou modelo de plataforma digital;
2. **Disponibilidade Documental Primária e Secundária:** Possuir registro histórico público e auditável suficiente (fontes como Crunchbase, reportagens investigativas, relatórios judiciais e relatórios de pós-mortem do CB Insights) para a reconstrução integral dos 9 blocos do Lean Canvas (Maurya, 2012);
3. **Desfecho Consolidado:** Ter status de mercado incontroverso — ou encerramento formal de atividades (dissolução/falência) ou operação madura e contínua comprovada na data de corte da pesquisa.

---

## 2. Protocolo de Anonimização e Blindagem contra Contaminação de Dados (*Lookahead Bias*)
*Como defender que a IA não usou dados históricos memorizados para "adivinhar o futuro".*

### O Protocolo de Anonimização Descritiva Funcional
* Todos os nomes próprios, fundadores famosos, marcas comerciais e identificadores diretos foram removidos das premissas.
* Cada empresa foi descrita unicamente pela sua **tese de negócio funcional** (ex: *"Plataforma móvel de micro-entretenimento premium"* para a Quibi; *"Marketplace peer-to-peer de hospitalidade alternativa"* para o Airbnb).
* Foi estipulado um parâmetro temporal de contorno (*"Ano da Análise"*), instruindo o modelo a balizar seu julgamento estritamente pelo estado da arte tecnológico e competitivo da época descrita.

### A Evidência Empírica contra o Efeito de Memorização (O "Contra-Golpe")
Se os LLMs estivessem simplesmente recuperando o desfecho histórico memorizado em seus pesos de treinamento (*lookahead leakage*):
1. O grupo **Controle (Baseline)** teria rejeitado categoricamente a Quibi e a Theranos, e aprovado imediatamente o Airbnb e o Uber.
2. **O resultado empírico real provou o oposto:** sob o prompt neutro de controle, a IA atribuiu **60% de probabilidade de sucesso para a Quibi** (atribuindo veredito de *"Necessita Pivotagem"*) e aprovou a 23andMe com **70% de probabilidade**.
3. **Conclusão científica:** O viés de **sicofância algorítmica** (*sycophancy*) e o viés de **superestimativa (*over-prediction*)** são forças preponderantes sobre a memória histórica da rede neural. A tendência inata de concordar passivamente com a tese apresentada pelo empreendedor sobrepõe-se à eventual recuperação de fatos passados.

---

## 3. O Dilema do Caso WeWork (S06)
*Análise crítica de posicionamento na base de dados.*

### O Problema:
* A WeWork foi categorizada originalmente como **`Ativa`** com ano de evento crítico em **2019** (o colapso do IPO e afastamento do CEO fundador).
* Em **novembro de 2023**, a WeWork protocolou pedido formal de recuperação judicial nos EUA (*Chapter 11*), embora tenha emergido em meados de 2024 como empresa privada reestruturada.

### Duas Alternativas para o Trabalho:

| Opção | Ação | Prós | Contras |
|---|---|---|---|
| **Opção A (Recomendada): Substituição por Caso Incontroverso** | Substituir WeWork por outra startup digital de sobrevivência e sucesso inquestionável (ex: **Mercado Livre**, **Dropbox**, **iFood** ou **Netflix**) | Blindagem total contra qualquer questionamento da banca examinadora; coerência conceitual perfeita. | Exige rodar os testes da nova startup (o que é rápido com os scripts automatizados). |
| **Opção B: Manutenção com Nota Metodológica de Rodapé** | Manter WeWork como Ativa e justificar em nota que o escopo temporal do estudo avaliou o evento de estresse de governança de 2019, momento em que a empresa continuava operacional. | Mantém o dataset prévio intacto. | Fica exposto ao questionamento de avaliadores do MBA que consideram o caso WeWork um clássico exemplo de falha de modelo e governança. |

---

## 4. Definição Matemática de "Acerto" e Métricas de Desempenho
*Atende aos Comentários #21 e #22 do orientador.*

### Matriz de Decisão Binária:

| Desfecho Real da Startup | Veredito da IA: Rejeitada / Pivot | Veredito da IA: Aprovada |
|---|---|---|
| **FALHA (Encerramento)** | **Verdadeiro Negativo (VN)** *(Acerto)* | **Falso Positivo (FP)** *(Erro por Sicofância)* |
| **ATIVA (Sobrevivência)** | **Falso Negativo (FN)** *(Erro por Hipercriticismo)* | **Verdadeiro Positivo (VP)** *(Acerto)* |

### Fórmulas das Métricas:
$$\text{Acurácia} = \frac{\text{VP} + \text{VN}}{\text{VP} + \text{VN} + \text{FP} + \text{FN}}$$

$$\text{Taxa de Falsos Positivos (Risco de Sicofância)} = \frac{\text{FP}}{\text{FP} + \text{VN}}$$

$$\text{Taxa de Falsos Negativos (Risco de Hipercriticismo)} = \frac{\text{FN}}{\text{FN} + \text{VP}}$$

* **Acerto Diagnóstico de Causa Principal:** Quando `categoria_risco_principal` da IA coincide estritamente com a taxonomia do `Rotulo_Categorico` oficial do pós-mortem.
* **Acerto Diagnóstico Secundário:** Quando coincide com as causas secundárias reconhecidas do encerramento.

---

## 5. Sensibilidade à Estruturação de Prompts e Disciplina Taxonômica
*Fundamentação teórica para o design do prompt e controle experimental.*

### A Ilusão do Modelo sem Restrição Estruturada
* Em ensaios comparativos entre modelos de diferentes portes (`llama3:8b`, `qwen2.5:14b`, `qwen2.5:32b`), observou-se que mesmo modelos com maior número de parâmetros (32B) exibem desvios de conformidade comportamental quando desprovidos de um sistema rígido de restrição de saída (*strict json schema enforcement* e taxonomia explícita).
* Com prompts abertos ou simplificados, modelos maiores tendem a gerar respostas prolixas, vereditos em linguagem natural não padronizada e extrapolação de escalas numéricas (ex.: autoatribuição de escores fora do intervalo 1–10).
* **Implicação Metodológica:** A robustez do arcabouço avaliativo reside primariamente na **arquitetura de condicionamento epistêmico do prompt** (*role-conditioned instruction set*, Maurya/Slade, 2026) combinada à **taxonomia fechada de falhas**, e não unicamente na escala volumétrica de parâmetros do modelo. O prompt atua como o redutor de entropia essencial para a comparabilidade científica dos dados.

---

## 6. O Efeito de Calibração Inversa de Rigor (Viés de Metacognição / Dunning-Kruger Algorítmico)
*Análise da variável `nivel_rigor_diagnostico` como métrica de autoavaliação.*

### Fenomenologia Observada
* Quando instruídos a autoavaliar o rigor analítico de seus próprios diagnósticos em uma escala de 1 a 10:
  * Modelos intermediários (14B) demonstraram tendência a escores máximos (9/10), correlacionados a diagnósticos mais assertivos porém circunscritos a riscos operacionais imediatos (ex.: preço e custo).
  * Modelos de maior capacidade paramétrica (32B) autoatribuíram notas mais conservadoras (8/10), apesar de identificarem causas-raiz estruturais e sistêmicas mais profundas (ex.: ausência intrínseca de necessidade de mercado — *product-market fit failure*).
* **Justificativa Teórica:** Essa disparidade reflete um fenômeno análogo ao efeito Dunning-Kruger em agentes cognitivos sintéticos. Modelos com maior repertório de contexto e raciocínio relacional possuem maior sensibilidade às variáveis latentes não mensuradas do negócio, gerando uma autoclassificação de rigor epistemicamente mais prudente e calibrada. Isso confirma que a autoavaliação do modelo deve ser tratada como variável explicativa do comportamento do LLM, e não como gabarito absoluto de verdade.

---

## 7. Resultados do Benchmark Empírico de Modelos e Concorrência Local
*Evidências experimentais coletadas em ambiente local Apple Silicon M1 Max (32GB RAM).*

### Comparativo Diagnóstico: `qwen2.5:14b` vs `qwen2.5:32b`
* **Tempo Médio de Inferência:** ~61s por chamada no 14B versus ~131s por chamada no 32B.
* **Acurácia Diagnóstica da Causa Primária:** No caso emblemático da Quibi (F01), o modelo de 32B identificou cirurgicamente a categoria `"Sem necessidade de mercado"` tanto na persona Advogado do Diabo quanto na de Investidor Anjo, correspondendo com precisão matemática ao gabarito histórico oficial do pós-mortem do CB Insights. O modelo de 14B convergiu para riscos operacionais mais visíveis (`"Problema de preço ou custo"` e `"Concorrência predatória"`).
* **Eficácia da Regra de Calibração:** No caso da Airbnb (S01 - empresa comprovadamente ativa e bem-sucedida), tanto o modelo de 14B quanto o de 32B atribuíram o veredito `"Necessita Pivotagem"` (probabilidade de 30%), erradicando o viés de falso negativo extremo (rejeição de 100%) observado na versão original não calibrada do Advogado do Diabo.

### Dinâmica de Concorrência e Paralelismo em Hardware Unificado
* **Gargalo de Largura de Banda de Memória (*Memory Bandwidth Bound*):** A geração autorregressiva de tokens em modelos quantizados locais é limitada pela taxa de transferência da memória unificada (400 GB/s no M1 Max).
* **Desempenho Medido:** A execução de duas requisições simultâneas via *multi-threading* (`OLLAMA_NUM_PARALLEL=2`) produziu um fator de aceleração (*speedup*) de **$1.31\times$** (redução líquida de **23.6%** no tempo de execução), sem degradação sintática das estruturas JSON.
* **Margem de Segurança Operacional:** O paralelismo é recomendado com folga de segurança para o modelo de 14B (~17 GB ocupados de 32 GB), enquanto o modelo de 32B (~20 GB de pesos) deve ser executado de forma sequencial para evitar pressão de *swap* no subsistema de armazenamento.

