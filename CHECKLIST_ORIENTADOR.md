# ✅ Checklist — Pontos de Melhoria do Orientador
> Devolutiva de Resultados Preliminares — Prof. Daniel Valotto (ESALQ/USP)  
> Gerado em: 06/Set/2026 | Prazo: 7 dias

---

## 🔬 FRENTE 1 — Experimento e Análise (Código / Dados)

### Design Experimental
- [ ] **[#15]** Deixar explícito no texto o que foi **manipulado** (tipo de prompt/persona), o que foi **observado** (probabilidade, veredito, rigor das críticas, identificação de problemas reais) e contra o que foi **comparado** (grupo controle)
- [ ] **[#16]** Incluir **tabela metodológica formal** com: Unidade experimental, Grupos (Controle + 3 Tratamentos), Variáveis observadas (prob. sucesso, veredito final, rigor crítico, correspondência com problemas reais) e Referência externa (desfecho real)
- [ ] **[#17]** Adaptar a tabela metodológica com os detalhes reais do experimento (não deixar como placeholder)

### Classificação e Gabarito
- [ ] **[#19]** **Justificar n=20** (por que 20 startups) e apresentar **critérios de inclusão** (ex: ser de base tecnológica, ter modelo de negócio digital, ter informações públicas suficientes para reconstrução do Lean Canvas)
- [ ] **[#20]** Criar **critérios objetivos de classificação** do desfecho real:
  - Startup ativa: evidência documental de operação em data de corte específica
  - Startup encerrada: evidência documental de encerramento/inatividade
  - Motivo da falha: fonte primária/secundária confiável + classificação na taxonomia adotada

### Métricas e Acurácia
- [ ] **[#21]** Definir **matematicamente o que é um acerto**:
  - `startup encerrou + IA rejeitou = acerto`
  - `startup ativa + IA aprovou = acerto`
  - Calcular: Acurácia, Falsos Positivos, Falsos Negativos, Precisão e Recall por persona
- [ ] **[#22]** Explicar operacionalmente como medir **rigor crítico** e **correspondência com problemas reais**

### Profundidade de Análise
- [ ] **[#23]** Ir além das médias — realizar análise aprofundada:
  - Verificar **consistência** do comportamento entre startups diferentes
  - **Correspondência com desfechos reais** (acertos, erros, FP, FN por startup)
  - Explorar **conjuntamente**: probabilidades + vereditos + qualidade das justificativas
  - Identificar **em quais dimensões do Lean Canvas** o Advogado do Diabo detectou problemas que o Controle não viu
  - Categorizar: persona adversarial apenas **reduziu probabilidade** ou **aumentou capacidade de identificar fragilidades**?
- [ ] **[#25]** Decidir e documentar **quais dados serão apresentados** (seleção criteriosa dos resultados mais relevantes)

---

## 📝 FRENTE 2 — Texto Acadêmico (Introdução + M&M + Resultados)

### Introdução
- [ ] **[#2]** Especificar **"incerteza em relação a quê"** no trecho que menciona incerteza sem complemento
- [ ] **[#3]** Trazer **dados concretos que evidenciem as falhas** das startups mencionadas
- [ ] **[#4]** Trazer **dados concretos que evidenciem as falhas** (segundo trecho — verificar qual parágrafo)
- [ ] **[#5]** Explicar o que são **Lean Canvas e Design Thinking** e como ajudam o processo inicial das startups. Incluir Design Thinking na introdução (está na metodologia mas ausente aqui)
- [ ] **[#6]** Incluir **caracterização formal dos LLMs**: o que são, características principais, vantagens de utilização
- [ ] **[#7]** Fazer a **ligação explícita entre uso de LLMs e ideação/validação** de startups
- [ ] **[#8]** Verificar se o termo correto é **"previsibilidade"** no trecho indicado

### Material e Métodos
- [ ] **[#9]** Substituir "web-scraping" por **"uso de ferramenta assistiva (Perplexity)"** para busca, localização e síntese de informações públicas. Explicar que a validação final foi realizada pelo pesquisador
- [ ] **[#10]** Detalhar se foi utilizada alguma **indicação de fonte ou delimitação de busca** no Perplexity
- [ ] **[#13]** Detalhar **quais colunas** continham o arquivo/dataset utilizado
- [ ] **[#24]** Reescrever a justificativa da temperatura: *"A temperatura foi mantida constante em 0,2 em todas as condições experimentais, **buscando reduzir** a variabilidade decorrente da amostragem estocástica e **manter constante** esse parâmetro entre as diferentes personas..."*  
  ⚠️ Remover afirmação de que a temperatura isolou **exclusivamente** o efeito da persona

### Resultados e Discussão
- [ ] Substituir análise apenas descritiva por análise de **acurácia formal** (tabelas com acertos/erros/FP/FN)
- [ ] Incluir **novos gráficos** gerados na análise aprofundada
- [ ] Discutir o **paradoxo do hipercriticismo** do Advogado do Diabo (rejeitou Airbnb, Uber, Nubank — falsos negativos)
- [ ] Comparar diagnósticos da IA com **motivos reais de sucesso/insucesso** das empresas

---

## 🛠️ FRENTE 3 — Repositório e Documentação Técnica

- [ ] Corrigir temperatura no **README.md** (0,2 → valor correto com justificativa)
- [ ] Atualizar README com descrição das **colunas do dataset** (atende #13)
- [ ] Documentar **critérios de inclusão** das startups no README (atende #19)
- [ ] Documentar a **definição de desfecho/gabarito** utilizada (atende #20)

---

## ⏳ DEIXAR PARA O FINAL (últimos a trabalhar)
> Removidos desta lista conforme solicitado — serão tratados separadamente

- [ ] Resumo / Abstract / Palavras-chave
- [ ] Considerações Finais (roteiro detalhado do orientador disponível)

---

## 📊 Status Geral

| Frente | Total de itens | Concluídos | Pendentes |
|---|---|---|---|
| Experimento e Análise | 8 | 0 | 8 |
| Texto Acadêmico | 13 | 0 | 13 |
| Repositório | 4 | 0 | 4 |
| **TOTAL** | **25** | **0** | **25** |

> 💡 **Dica:** À medida que for concluindo, troque `[ ]` por `[x]` para acompanhar o progresso.
