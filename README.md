# Mitigação de Vieses Otimistas de Inteligência Artificial na Validação de Modelos de Negócios Digitais

Este repositório contém o código-fonte, metodologia, base de dados e scripts analíticos do experimento científico conduzido para o Trabalho de Conclusão de Curso na **Especialização em Gestão de Negócios Digitais e Inteligência Artificial – ESALQ/USP**.

Alinhado com os preceitos de **Ciência Aberta (Open Science)**, este projeto foi concebido para ser integralmente **auditável**, **transparente** e **reprodutível localmente**, sem qualquer dependência de APIs proprietárias pagas ou serviços em nuvem fechados.

---

## 🔬 Delineamento Metodológico do Experimento

O estudo investiga como Grandes Modelos de Linguagem (*Large Language Models* - LLMs) avaliam premissas em estágio inicial (*early-stage*) de startups reais quando submetidos a diferentes condições de condicionamento de papel (*Role-Conditioned Instruction Sets*).

O experimento submete uma amostra controlada e balanceada de startups a **7 personas avaliadoras distintas**, construídas sobre literaturas de tomada de decisão em Venture Capital, Lean Startup e governança epistêmica:

1. **Persona Controle (Baseline Neutro):** Avalia as premissas estritamente pelo framework do *Lean Canvas* (Maurya, 2012), sem indução de viés positivo ou negativo.
2. **Persona Genérica (Consultor de Negócios):** Simula a postura típica de assistentes de IA comerciais, propensa a reforçar a tese do empreendedor (*viés de sicofância algorítmica*).
3. **Persona Advogado do Diabo (Auditor de VC - Calibrado):** Atua como provocador epistêmico implacável, estressando vulnerabilidades fatais, com regra explícita de calibração para não incorrer em hipercriticismo cego.
4. **Persona Analítica (Auditor Financeiro Estrito):** Julga exclusivamente pela mecânica unitária e inclui a cláusula *No Evidence Clause* (declara "Evidência insuficiente" em vez de inventar dados ausentes).
5. **Persona Investidor Anjo (Early-Stage Angel):** Foca na capacidade de execução da equipe fundadora, urgência da dor e viabilidade do horizonte de 12–18 meses (*pre-seed / seed*).
6. **Persona Cético Epistêmico (Governança de Premissas):** Avalia a coerência lógica interna e as relações de causa-efeito entre as hipóteses formuladas, caçando contradições implícitas.
7. **Persona Auditor Regulatório (Risco Legal e Incumbentes):** Mapeia riscos regulatórios, barreiras legais e capacidade de retaliação predatória por atores de mercado consolidados.

---

## 🎛️ Parâmetros de Inferência e Temperatura
*Atende aos Comentários #13 e #24 do orientador.*

Para assegurar o rigor acadêmico e a comparabilidade estatística:
* **Temperatura ($T = 0.2$):** A temperatura foi mantida constante em 0,2 em todas as condições experimentais, buscando reduzir a variabilidade decorrente da amostragem estocástica e manter constante esse parâmetro entre as diferentes personas avaliadoras. O valor baixo garante que o modelo mantenha estrita conformidade sintática com o schema JSON e a taxonomia taxonômica exigida, sem eliminar a capacidade reflexiva necessária para o tensionamento analítico.
* **Stateless:** Cada requisição HTTP efetuada para o motor de inferência é independente e isolada, sem histórico de contexto ou vazamento entre personas/startups.
* **Schema JSON Estrito:** Todas as respostas retornam exclusivamente em formato JSON com chaves padronizadas:
  * `analise_problema_mercado`
  * `analise_solucao_proposta`
  * `analise_receitas_custos`
  * `vantagem_injusta`
  * `risco_critico`
  * `analise_equipe`
  * `categoria_risco_principal` (escolha forçada em taxonomia de 10 categorias da CB Insights)
  * `probabilidade_sucesso_0_a_100` (escore numérico contínuo)
  * `veredito_final` (`Aprovada`, `Rejeitada`, `Necessita Pivotagem`)
  * `nivel_rigor_diagnostico` (autoavaliação em escala 1–10)

---

## 📁 Dataset Experimental (`dataset_experimento_agnostico.csv`)
*Atende aos Comentários #13, #19 e #20 do orientador.*

A base conta com $n=20$ startups selecionadas segundo critérios rigorosos de elegibilidade histórica:
* **Balanceamento Perfeito (50% / 50%):** 10 startups com desfecho de falência comprovada (`Falha`) e 10 com desfecho consolidado de sobrevivência (`Ativa`).
* **Critérios de Inclusão (#19):**
  1. Empresa nativa digital ou de base estritamente tecnológica;
  2. Disponibilidade documental auditável para reconstrução integral dos 9 blocos do Lean Canvas (CB Insights, Crunchbase, SEC, relatórios judiciais);
  3. Desfecho histórico incontroverso na data de corte (maio de 2026).
* **Definição de Gabarito / Ground Truth (#20):**
  - `Falha`: Dissolução formal, encerramento de atividades ou liquidação judicial comprovada. Motivo primário classificado na taxonomia de 10 categorias da CB Insights.
  - `Ativa`: Operação madura contínua e faturamento escalável comprovados. Documenta-se o obstáculo crítico superado na trajetória.
* **Anonimização Funcional:** Nomes de fundadores, marcas comerciais e identificadores diretos foram removidos das premissas para blindagem contra vazamento de memória histórica (*lookahead bias*).
* **Marco Temporal (*Time Window*):** Cada linha possui o campo `Ano_Evento_Critico`, instruindo a IA a balizar a análise estritamente pelo estado da arte tecnológico e competitivo da época.
* **Caso S06 (Mercado Livre):** Substituição formal da WeWork por caso de sobrevivência extrema incontroverso em mercados emergentes perante o estouro da bolha ponto-com (2000–2001).

### Dicionário de Colunas do Dataset (16 Atributos):
1. `ID_Startup`: Identificador único (`F01`–`F10` para Falhas; `S01`–`S10` para Ativas).
2. `Nome_Real`: Nome comercial histórico da empresa.
3. `Nome_Anonimizado`: Tese de negócio funcional utilizada na instrução do prompt.
4. `Ano_Fundacao`: Ano cronológico de criação da startup.
5. `Ano_Encerramento`: Ano de dissolução formal (nulo para empresas ativas).
6. `Setor_Industria`: Vertical de atuação (ex.: Fintech, MediaTech, HealthTech).
7. `Modelo_Negocios`: Descrição estruturada dos 9 blocos do Lean Canvas no ano de fundação.
8. `Status_Real`: Gabarito de desfecho (`Falha` vs `Ativa`).
9. `Motivo_Real_Gabarito`: Síntese textual da causa real do encerramento ou obstáculo superado.
10. `Rotulo_Categorico`: Causa primária de falência classificada na taxonomia de 10 categorias da CB Insights.
11. `Rotulos_Secundarios`: Causas secundárias reconhecidas do encerramento (separadas por ponto-e-vírgula).
12. `Evento_Critico`: Descrição da crise de quase-morte enfrentada pelas empresas ativas.
13. `Categoria_Evento_Critico`: Enquadramento taxonômico do evento crítico superado.
14. `Ano_Evento_Critico`: Ano do evento crítico, servindo como âncora temporal do prompt.
15. `Contexto_Mercado_Equipe`: Contexto competitivo e qualificação dos fundadores à época.
16. `URL_Fonte`: Link documental de auditoria da fonte de referência.

---

## 🛠️ Instalação e Configuração Local

### 1. Motor de IA Local (Ollama)
1. Instale o Ollama via [ollama.com](https://ollama.com) ou Homebrew (macOS):
   ```bash
   brew install ollama
   brew services start ollama
   ```
2. Baixe os modelos recomendados:
   ```bash
   # Modelo padrão do experimento (alta velocidade e excelente consistência JSON):
   ollama pull qwen2.5:14b

   # Modelo avançado para máxima profundidade diagnóstica:
   ollama pull qwen2.5:32b
   ```

### 2. Ambiente Virtual Python
```bash
cd devils-advocate
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # ou: pip install pandas requests tqdm matplotlib seaborn
```

---

## 🚀 Como Executar o Experimento

Com o ambiente virtual ativado e o Ollama em execução:

### Execução com o modelo padrão (`qwen2.5:14b`):
```bash
python3 experimento_tcc.py
```
*Tempo estimado: ~2h15min para as 20 startups $\times$ 7 personas (140 relatórios).*

### Execução com o modelo avançado (`qwen2.5:32b`):
```bash
python3 experimento_tcc.py --model qwen2.5:32b
```
*Tempo estimado: ~5h para execução sequencial completa (ideal para execução noturna).*

### Teste rápido de sanidade (apenas 2 primeiras startups):
```bash
python3 experimento_tcc.py --limit 2
```

### Execução Desacoplada em Background (Não fecha o terminal e não consome tokens de IA):
Se você deseja disparar o experimento no terminal e fechar a janela ou deixá-lo rodando sem monitoramento ativo:
```bash
# Executa em segundo plano com log redirecionado:
nohup .venv/bin/python3 experimento_tcc.py > experimento.log 2>&1 &

# Para acompanhar o progresso em tempo real quando quiser:
tail -f experimento.log
```

Os resultados são gravados automaticamente a cada startup concluída em:
`resultados/resultados_experimento_v2.csv`

---

## 📈 Geração de Gráficos e Análise Estatística

Após o encerramento da coleta, execute o script analítico formal:
```bash
python3 analise_acuracia.py
```
O script processará automaticamente as 140 inferências e exportará para a pasta `anexos_tcc/`:
* **Tabelas de Acurácia e Matriz de Confusão:** `tabela_metricas_desempenho_rejeicao.csv`, `tabela_metricas_desempenho_prob50.csv` e `tabela1_distribuicao_vereditos.csv`;
* **Acurácia Diagnóstica Causal:** `tabela_acuracia_diagnostica_causas.csv` e `tabela_matriz_riscos_diagnosticos_completa.csv`;
* **Bateria de Figuras Acadêmicas (300 DPI, ABNT/ESALQ):**
  - `figura2_heatmap_startups_personas.png` (Matriz de julgamento 20 startups $\times$ 7 personas);
  - `figura3_boxplot_probabilidades.png` (Boxplot bivariado de discriminação Falha vs Ativa);
  - `figura4_radar_lean_canvas.png` (Radar de profundidade analítica nas 6 dimensões do Lean Canvas);
  - `figura5_scatter_controle_vs_diabo.png` (Scatterplot com linha de identidade e casos emblemáticos).

---

## ✒️ Citação

```bibtex
@misc{chiari2026mitigacao,
  author       = {Chiari, Murilo Ferrarezi and Valotto, Daniel},
  title        = {Mitigação de vieses otimistas de inteligência artificial na validação de modelos de negócios digitais},
  howpublished = {Trabalho de Conclusão de Curso (Especialização em Gestão de Negócios Digitais e Inteligência Artificial) - ESALQ/USP},
  year         = {2026},
  note         = {Orientador: Prof. Dr. Daniel Valotto}
}
```

---

## 📄 Licença
Distribuído sob a licença **MIT**. Consulte o arquivo `LICENSE` para mais detalhes.