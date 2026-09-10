#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Gerador do Painel Amplo de Validação e Auditoria Manual — Arquitetura V6
TCC ESALQ/USP — Autor: Murilo Ferrarezi Chiari | Orientador: Prof. Dr. Daniel Valotto
=============================================================================
Lê o dataset enriquecido com a classificação do juiz CB Insights e compila
um documento Markdown completo, exaustivo e intuitivo para auditoria humana,
conferência de acertos causais e geração de insumos para os gráficos do TCC.
=============================================================================
"""

import argparse
import os
import pandas as pd

DEFAULT_CSV_ENTRADA = "resultados/resultados_lean_canvas_com_categorias_lofa.csv"
DEFAULT_MD_SAIDA_DEVILS = "CADERNO_VALIDACAO_AUDITORIA.md"
DEFAULT_MD_SAIDA_CAPITULOS = "../capitulos_tcc/PAINEL_VALIDACAO_HUMANA.md"

PERSONAS = [
    ("Base", "Modelo Puro (Baseline)", "Controle"),
    ("Epist", "Cético Epistêmico", "Consistência Dedutiva"),
    ("Diabo", "Advogado do Diabo", "Tríade Crítica"),
    ("Anali", "Analista Financeiro", "Tríade Crítica"),
    ("Reg", "Auditor Regulatório", "Tríade Crítica"),
    ("Anjo", "Investidor Anjo", "Tríade Propositiva"),
    ("Prod", "Champion do Produto", "Tríade Propositiva"),
    ("Inov", "Estrategista de Inovação", "Tríade Propositiva"),
]


def formatar_decisao_tag(decisao: str) -> str:
    d = str(decisao)
    if "Avançar" in d or "MVP" in d:
        return "🟢 **MVP**"
    if "Pivot" in d:
        return "🟡 **PIVOT**"
    if "Descarte" in d or "Inviabilidade" in d:
        return "🔴 **DESCARTE**"
    return d


def gerar_painel(csv_entrada: str = DEFAULT_CSV_ENTRADA, md_saida_devils: str = DEFAULT_MD_SAIDA_DEVILS, md_saida_capitulos: str = DEFAULT_MD_SAIDA_CAPITULOS):
    if not os.path.exists(csv_entrada):
        print(f"[ERRO] Arquivo não encontrado: {csv_entrada}")
        return

    df = pd.read_csv(csv_entrada)
    falhas_df = df[df["Status_Real"] == "Falha"].copy()
    ativas_df = df[df["Status_Real"] == "Ativa"].copy()

    md = []
    
    # -------------------------------------------------------------------------
    # CABEÇALHO E INSTRUÇÕES
    # -------------------------------------------------------------------------
    md.append("# 📋 PAINEL INTEGRAL DE VALIDAÇÃO E AUDITORIA MANUAL — ARQUITETURA V6")
    md.append("## Auditoria Qualitativa de Decisões Lean e Aderência Causal das LOFAs (Taxonomia CB Insights)")
    md.append("**Trabalho de Conclusão de Curso (TCC) — ESALQ/USP**  ")
    md.append("**Autor:** Murilo Ferrarezi Chiari | **Orientador:** Prof. Dr. Daniel Valotto  ")
    md.append(f"**Fonte de Dados Auditada:** `{csv_entrada}`  ")
    md.append(f"**Total de Casos:** 20 startups (10 Falhas / 10 Ativas) $\\times$ 8 Condições = 160 inferências completas.\n")
    md.append("---\n")

    md.append("## 🎯 Objetivo Deste Documento e Roteiro de Auditoria Humana")
    md.append("Este documento reúne **a totalidade das evidências empíricas geradas pela Arquitetura V6** com o objetivo de subsidiar a sua auditoria e validação manual como pesquisador. Ele foi estruturado para resolver duas necessidades fundamentais da dissertação:\n")
    md.append("1. **Validação do Juiz LLM (*LLM-as-a-Judge*):** Permitir que você confira se o enquadramento categorial da LOFA feito pela IA na taxonomia da CB Insights é coerente e correto;")
    md.append("2. **Confrontação Causal Qualitativa:** Confrontar a premissa de maior fragilidade isolada no ano de gênese (`LOFA`) contra o desfecho histórico real de encerramento (`Motivo_Real_Gabarito`), alimentando as discussões do **Capítulo 4 (Resultados e Discussão)**.")
    md.append("\n> **Instruções para a Auditoria:** Utilize as caixas de seleção `[ ]` presentes em cada caso para anotar suas observações, confirmar acertos ou registrar discordâncias metodológicas com o juiz algorítmico.\n")
    md.append("---\n")

    # -------------------------------------------------------------------------
    # RESUMO EXECUTIVO QUANTITATIVO
    # -------------------------------------------------------------------------
    md.append("## 1. Resumo Executivo Quantitativo Consolidado\n")

    # Tabela 1: Resumo de Performance por Persona
    md.append("### Tabela 1.1 — Matriz de Discriminação e Aderência Causal por Persona\n")
    md.append("| Prefixo | Persona | Bloco | Aprov. Ativas (VP) | Aprov. Falhas (FP) | Delta Discriminação | Acerto Causal Estrito | Acerto Causal Amplo |")
    md.append("| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |")

    for pref, nome, bloco in PERSONAS:
        at_mvp = (ativas_df[f"{pref}_Decisao_Lean"].astype(str).str.contains("Avançar|MVP")).sum()
        fl_mvp = (falhas_df[f"{pref}_Decisao_Lean"].astype(str).str.contains("Avançar|MVP")).sum()
        taxa_at = (at_mvp / len(ativas_df)) * 100
        taxa_fl = (fl_mvp / len(falhas_df)) * 100
        delta = taxa_at - taxa_fl

        estritos = falhas_df[f"{pref}_Acerto_Causal_Estrito"].sum()
        amplos = falhas_df[f"{pref}_Acerto_Causal_Amplo"].sum()
        pct_est = (estritos / len(falhas_df)) * 100
        pct_amp = (amplos / len(falhas_df)) * 100

        md.append(f"| **`{pref}`** | {nome} | {bloco} | **{at_mvp}/10 ({taxa_at:.0f}%)** | {fl_mvp}/10 ({taxa_fl:.0f}%) | **{delta:+.0f} p.p.** | {int(estritos)}/10 ({pct_est:.0f}%) | **{int(amplos)}/10 ({pct_amp:.0f}%)** |")

    md.append("\n*Legenda: Delta Discriminação = Taxa de Aprovação em Ativas (Sensibilidade) menos Taxa de Aprovação em Falhas (1 - Especificidade).*")
    md.append("\n---\n")

    # Tabela 1.2: Visão Geral das 20 Startups
    md.append("### Tabela 1.2 — Matriz de Consenso Decisório (20 Startups $\\times$ 8 Personas)\n")
    md.append("| ID | Startup | Status Real | Setor | Base | Epist | Diabo | Anali | Reg | Anjo | Prod | Inov | Votos MVP | Diagnóstico de Consenso |")
    md.append("| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")

    for _, r in df.iterrows():
        mvps = sum(1 for pref, _, _ in PERSONAS if "Avançar" in str(r[f"{pref}_Decisao_Lean"]) or "MVP" in str(r[f"{pref}_Decisao_Lean"]))
        pct = (mvps / 8.0) * 100
        
        tags = [formatar_decisao_tag(r[f"{pref}_Decisao_Lean"]).replace("**", "") for pref, _, _ in PERSONAS]
        diag = "Validação Plena" if mvps >= 7 else ("Validação Majoritária" if mvps >= 5 else ("Divergência / Empate" if mvps == 4 else ("Bloqueio / Pivotagem" if mvps > 0 else "Bloqueio Unânime")))
        
        md.append(f"| **{r['ID_Startup']}** | {r['Nome_Real']} | **{r['Status_Real']}** | {r['Setor_Industria']} | {' | '.join(tags)} | **{mvps}/8 ({pct:.0f}%)** | {diag} |")

    md.append("\n---\n")

    # -------------------------------------------------------------------------
    # SEÇÃO 2: AUDITORIA DETALHADA DAS 10 STARTUPS DE FALHA REAL
    # -------------------------------------------------------------------------
    md.append("## 2. Auditoria Detalhada das Startups de Falha Real (F01 a F10)")
    md.append("Esta seção é o núcleo da **validação causal**: confronte a causa documental do colapso da empresa contra a premissa de salto de fé (LOFA) e o enquadramento atribuído pelo juiz algorítmico.\n")

    for _, r in falhas_df.iterrows():
        md.append(f"### 🔴 [{r['ID_Startup']}] {r['Nome_Real']} (Status: Falha)")
        md.append(f"**Tese Anonimizada Apresentada à IA:** *{r['Nome_Anonimizado']}*  ")
        md.append(f"**Setor:** {r['Setor_Industria']} | **Ano de Fundação:** {int(r['Ano_Fundacao'])} | **Ano de Encerramento:** {int(r['Ano_Encerramento'])}  ")
        md.append(f"**Causa Primária Documental (CB Insights):** `{r['Rotulo_Categorico']}`  ")
        md.append(f"**Causas Secundárias Registradas:** `{r['Rotulos_Secundarios']}`  ")
        md.append(f"**Gabarito Real Histórico:**  \n> *\"{r['Motivo_Real_Gabarito']}\"*\n")

        md.append("#### Auditoria das 8 Personas para " + r['Nome_Real'] + ":\n")
        md.append("| Persona | Decisão Lean | Categoria Juiz (CB Insights) | Acerto Causal | Premissa de Salto de Fé (LOFA) Formulada | Justificativa do Juiz LLM |")
        md.append("| :--- | :---: | :--- | :---: | :--- | :--- |")

        for pref, nome, _ in PERSONAS:
            dec = formatar_decisao_tag(r[f"{pref}_Decisao_Lean"])
            cat = r.get(f"{pref}_LOFA_Categoria", "N/A")
            lofa = r.get(f"{pref}_LOFA", "N/A")
            just = r.get(f"{pref}_LOFA_Justificativa_Juiz", "N/A")
            est = r.get(f"{pref}_Acerto_Causal_Estrito", False)
            amp = r.get(f"{pref}_Acerto_Causal_Amplo", False)

            tag_acerto = "🎯 **Estrito**" if est else ("🟢 **Amplo**" if amp else "❌ Não aderente")
            md.append(f"| **`{pref}`** ({nome}) | {dec} | `{cat}` | {tag_acerto} | {lofa} | {just} |")

        md.append("\n**Validação Manual do Pesquisador para " + r['Nome_Real'] + ":**")
        md.append("- [ ] **Concordância com as Decisões:** As personas críticas (*Diabo*, *Anali*, *Reg*) agiram com o ceticismo esperado?")
        md.append("- [ ] **Validação da Categoria do Juiz:** A classificação atribuída pelo juiz nas LOFAs reflete fielmente o texto?")
        md.append("- [ ] **Anotação de Divergência / Ajuste Manual:** __________________________________________________\n")
        md.append("---\n")

    # -------------------------------------------------------------------------
    # SEÇÃO 3: AUDITORIA DETALHADA DAS 10 STARTUPS ATIVAS (SUCESSOS REAIS)
    # -------------------------------------------------------------------------
    md.append("## 3. Auditoria Detalhada das Startups Ativas / Sucessos Reais (S01 a S10)")
    md.append("Esta seção avalia a capacidade do comitê em reconhecer premissas saudáveis e plausibilidade de validação em modelos vencedores, sem incorrer em viés de omissão.\n")

    for _, r in ativas_df.iterrows():
        md.append(f"### 🟢 [{r['ID_Startup']}] {r['Nome_Real']} (Status: Ativa)")
        md.append(f"**Tese Anonimizada Apresentada à IA:** *{r['Nome_Anonimizado']}*  ")
        md.append(f"**Setor:** {r['Setor_Industria']} | **Ano de Fundação:** {int(r['Ano_Fundacao'])}  ")
        md.append(f"**Evento Crítico Histórico Superado:** `{r['Evento_Critico']}` ({int(r['Ano_Evento_Critico'])})  ")
        md.append(f"**Categoria do Evento Crítico:** `{r['Categoria_Evento_Critico']}`  ")
        md.append(f"**Contexto da Equipe e Mercado na Gênese:**  \n> *\"{r['Contexto_Mercado_Equipe']}\"*\n")

        md.append("#### Auditoria das 8 Personas para " + r['Nome_Real'] + ":\n")
        md.append("| Persona | Decisão Lean | Categoria Juiz (CB Insights) | Premissa de Salto de Fé (LOFA) Formulada | Experimento de MVP Prioritário Sugerido |")
        md.append("| :--- | :---: | :--- | :--- | :--- |")

        for pref, nome, _ in PERSONAS:
            dec = formatar_decisao_tag(r[f"{pref}_Decisao_Lean"])
            cat = r.get(f"{pref}_LOFA_Categoria", "N/A")
            lofa = r.get(f"{pref}_LOFA", "N/A")
            mvp = r.get(f"{pref}_MVP", "N/A")

            md.append(f"| **`{pref}`** ({nome}) | {dec} | `{cat}` | {lofa} | {mvp} |")

        md.append("\n**Validação Manual do Pesquisador para " + r['Nome_Real'] + ":**")
        md.append("- [ ] **Plausibilidade da Decisão:** O percentual de aprovação ou exigência de pivotagem é justificado pelo estágio de gênese?")
        md.append("- [ ] **Qualidade do MVP Sugerido:** O experimento desenhado no ciclo Construir-Medir-Aprender é executável a baixo custo?")
        md.append("- [ ] **Anotação / Insights para a Discussão:** __________________________________________________\n")
        md.append("---\n")

    # -------------------------------------------------------------------------
    # SEÇÃO 4: MAPA DE INSUMOS PARA OS SCRIPTS DE ANÁLISE GRÁFICA DO TCC
    # -------------------------------------------------------------------------
    md.append("## 4. Roteiro de Geração de Figuras e Gráficos para o Capítulo 4")
    md.append("A partir da consolidação deste dataset (`resultados_v6_lean_8personas_com_categorias_lofa.csv`), os seguintes gráficos e figuras devem ser gerados em alta resolução (300 DPI) para inserção no TCC:\n")
    md.append("1. **Figura 4.1 — Heatmap da Matriz de Decisões (20 Startups $\\times$ 8 Personas):** Visualização matricial em cores (Verde = MVP, Amarelo = Pivot, Vermelho = Descarte), destacando a transição do colapso da V3 para o discernimento da V6;")
    md.append("2. **Figura 4.2 — Gráfico de Barras do Delta de Discriminação Líquida (Sensibilidade vs. Falso Positivo):** Ranking das personas por poder de separação de sinal, evidenciando o topo com `Anali` (+60 p.p.) e `Prod` (+50 p.p.);")
    md.append("3. **Figura 4.3 — Gráfico de Barras da Taxa de Aderência Causal (% de Acerto da Causa de Falha por Persona):** Demonstração visual de como o `Diabo` (80%), `Anjo` (80%), `Inov` (80%) e `Epist` (70%) enquadraram as premissas nas causas reais do CB Insights;")
    md.append("4. **Figura 4.4 — Diagrama de Dispersão Causal (Matriz de Confusão de Categorias):** Cruzamento entre a categoria real da CB Insights e a categoria diagnosticada pelo comitê nas startups que falharam.")

    conteudo_final = "\n".join(md)

    # Grava na pasta devils-advocate
    with open(md_saida_devils, "w", encoding="utf-8") as f:
        f.write(conteudo_final)
    print(f"Painel salvo em: {md_saida_devils}")

    # Grava também na pasta capitulos_tcc se existir
    dir_capitulos = os.path.dirname(md_saida_capitulos)
    if os.path.exists(dir_capitulos):
        with open(md_saida_capitulos, "w", encoding="utf-8") as f:
            f.write(conteudo_final)
        print(f"Painel salvo em: {md_saida_capitulos}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerador do Painel de Validação e Auditoria Manual")
    parser.add_argument("--input", type=str, default=DEFAULT_CSV_ENTRADA)
    parser.add_argument("--output", type=str, default=DEFAULT_MD_SAIDA_DEVILS)
    parser.add_argument("--output-capitulos", type=str, default=DEFAULT_MD_SAIDA_CAPITULOS)
    args = parser.parse_args()

    gerar_painel(csv_entrada=args.input, md_saida_devils=args.output, md_saida_capitulos=args.output_capitulos)
