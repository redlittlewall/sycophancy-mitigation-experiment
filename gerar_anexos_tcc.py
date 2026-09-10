#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Gerador Canônico de Figuras e Tabelas Acadêmicas — TCC ESALQ/USP
Arquitetura Lean Canvas com Auditoria de Showstoppers (Maurya / Ries)
Autor: Murilo Ferrarezi Chiari | Orientador: Prof. Dr. Daniel Valotto
=============================================================================
Lê os resultados consolidados do experimento e gera:
1. Figuras em alta resolução (300 DPI, padrão tipográfico ABNT/ESALQ);
2. Tabelas estruturadas no padrão estatístico do IBGE em formato CSV e Markdown.
=============================================================================
"""

import argparse
import os
import sys

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"
os.makedirs("/tmp/matplotlib_cache", exist_ok=True)

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

# Configurações de tipografia e estilo ABNT / ESALQ
mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
mpl.rcParams["text.color"] = "#222222"
mpl.rcParams["axes.labelcolor"] = "#222222"
mpl.rcParams["xtick.color"] = "#222222"
mpl.rcParams["ytick.color"] = "#222222"
mpl.rcParams["font.size"] = 10
mpl.rcParams["axes.titlesize"] = 12
mpl.rcParams["axes.titleweight"] = "bold"
mpl.rcParams["axes.labelsize"] = 11
mpl.rcParams["axes.labelweight"] = "bold"
mpl.rcParams["figure.dpi"] = 300

PASTA_ANEXOS = "anexos_tcc"

PERSONAS_ORDEM = [
    ("Base", "Modelo Puro (Base)", "Controle"),
    ("Epist", "Cético Epistêmico", "Consistência"),
    ("Diabo", "Advogado do Diabo", "Tríade Crítica"),
    ("Anali", "Analista Financeiro", "Tríade Crítica"),
    ("Reg", "Auditor Regulatório", "Tríade Crítica"),
    ("Anjo", "Investidor Anjo", "Tríade Propositiva"),
    ("Prod", "Champion de Produto", "Tríade Propositiva"),
    ("Inov", "Estrategista de Inovação", "Tríade Propositiva"),
]


def carregar_dados(caminho_csv: str) -> pd.DataFrame:
    if not os.path.exists(caminho_csv):
        print(f"[ERRO] Arquivo de dados não encontrado: {caminho_csv}")
        sys.exit(1)
    df = pd.read_csv(caminho_csv)
    return df


def gerar_figura1_distribuicao_decisoes(df: pd.DataFrame, pasta_saida: str):
    """
    Figura 1: Gráfico de Barras Empilhadas (100%) da Distribuição de Decisões
    por Persona para Startups com Falha vs. Ativas.
    """
    print("-> Gerando Figura 1: Distribuição de Decisões Lean...")
    fig, (ax_falhas, ax_ativas) = plt.subplots(1, 2, figsize=(15, 6), sharey=True)

    falhas = df[df["Status_Real"] == "Falha"]
    ativas = df[df["Status_Real"] == "Ativa"]

    cores = {
        "Avançar para MVP": "#27ae60",                     # Verde Esmeralda
        "Necessita Pivotagem": "#f39c12",                 # Âmbar / Laranja
        "Reprovação por Showstopper (Descarte)": "#c0392b" # Vermelho Coral
    }

    labels_legenda = {
        "Avançar para MVP": "Avançar para MVP",
        "Necessita Pivotagem": "Necessita Pivotagem",
        "Reprovação por Showstopper (Descarte)": "Showstopper (Descarte)"
    }

    nomes_personas = [p[1] for p in PERSONAS_ORDEM]
    prefixos = [p[0] for p in PERSONAS_ORDEM]

    # Processar Falhas
    dados_f = {"MVP": [], "Pivot": [], "Descarte": []}
    for p in prefixos:
        col = f"{p}_Decisao_Lean"
        tot = len(falhas)
        mvp = (falhas[col] == "Avançar para MVP").sum() / tot * 100
        piv = (falhas[col] == "Necessita Pivotagem").sum() / tot * 100
        des = (falhas[col] == "Reprovação por Showstopper (Descarte)").sum() / tot * 100
        dados_f["MVP"].append(mvp)
        dados_f["Pivot"].append(piv)
        dados_f["Descarte"].append(des)

    y_pos = np.arange(len(nomes_personas))

    # Plot Falhas
    b1 = ax_falhas.barh(y_pos, dados_f["Descarte"], color=cores["Reprovação por Showstopper (Descarte)"], edgecolor="white", height=0.65, label=labels_legenda["Reprovação por Showstopper (Descarte)"])
    b2 = ax_falhas.barh(y_pos, dados_f["Pivot"], left=dados_f["Descarte"], color=cores["Necessita Pivotagem"], edgecolor="white", height=0.65, label=labels_legenda["Necessita Pivotagem"])
    left_mvp = [d + p for d, p in zip(dados_f["Descarte"], dados_f["Pivot"])]
    b3 = ax_falhas.barh(y_pos, dados_f["MVP"], left=left_mvp, color=cores["Avançar para MVP"], edgecolor="white", height=0.65, label=labels_legenda["Avançar para MVP"])

    ax_falhas.set_title("A. Startups com Falha Real (n = 10)", fontsize=12, pad=12)
    ax_falhas.set_xlabel("Percentual de Avaliações (%)")
    ax_falhas.set_yticks(y_pos)
    ax_falhas.set_yticklabels(nomes_personas, fontweight="bold")
    ax_falhas.set_xlim(0, 100)
    ax_falhas.grid(axis="x", linestyle="--", alpha=0.5)

    # Processar Ativas
    dados_a = {"MVP": [], "Pivot": [], "Descarte": []}
    for p in prefixos:
        col = f"{p}_Decisao_Lean"
        tot = len(ativas)
        mvp = (ativas[col] == "Avançar para MVP").sum() / tot * 100
        piv = (ativas[col] == "Necessita Pivotagem").sum() / tot * 100
        des = (ativas[col] == "Reprovação por Showstopper (Descarte)").sum() / tot * 100
        dados_a["MVP"].append(mvp)
        dados_a["Pivot"].append(piv)
        dados_a["Descarte"].append(des)

    # Plot Ativas
    ax_ativas.barh(y_pos, dados_a["Descarte"], color=cores["Reprovação por Showstopper (Descarte)"], edgecolor="white", height=0.65)
    ax_ativas.barh(y_pos, dados_a["Pivot"], left=dados_a["Descarte"], color=cores["Necessita Pivotagem"], edgecolor="white", height=0.65)
    left_mvp_a = [d + p for d, p in zip(dados_a["Descarte"], dados_a["Pivot"])]
    ax_ativas.barh(y_pos, dados_a["MVP"], left=left_mvp_a, color=cores["Avançar para MVP"], edgecolor="white", height=0.65)

    ax_ativas.set_title("B. Startups Ativas no Mercado (n = 10)", fontsize=12, pad=12)
    ax_ativas.set_xlabel("Percentual de Avaliações (%)")
    ax_ativas.set_xlim(0, 100)
    ax_ativas.grid(axis="x", linestyle="--", alpha=0.5)

    # Legenda global centralizada no topo
    fig.legend(loc="upper center", bbox_to_anchor=(0.5, 1.05), ncol=3, frameon=True, fontsize=10)

    plt.tight_layout()
    caminho = os.path.join(pasta_saida, "figura1_distribuicao_decisoes_lean.png")
    plt.savefig(caminho, bbox_inches="tight")
    plt.close()
    print(f"   [OK] Salvo em: {caminho}")


def gerar_figura2_heatmap_decisoes(df: pd.DataFrame, pasta_saida: str):
    """
    Figura 2: Heatmap Matricial Completo (20 Startups x 8 Personas)
    Codificação Categorial: 0 (Descarte), 1 (Pivotagem), 2 (MVP).
    """
    print("-> Gerando Figura 2: Heatmap Matricial de Decisões...")
    prefixos = [p[0] for p in PERSONAS_ORDEM]
    nomes_personas = [p[1] for p in PERSONAS_ORDEM]

    # Mapeamento numérico e rótulos
    mapa_num = {
        "Reprovação por Showstopper (Descarte)": 0,
        "Necessita Pivotagem": 1,
        "Avançar para MVP": 2
    }
    mapa_rotulo = {
        0: "Descarte",
        1: "Pivot",
        2: "MVP"
    }

    # Ordenar startups: Falhas primeiro, depois Ativas
    ordem_startups = df["Nome_Real"].tolist()
    matriz_num = []
    matriz_txt = []

    for idx, row in df.iterrows():
        linha_n = []
        linha_t = []
        for p in prefixos:
            v = row[f"{p}_Decisao_Lean"]
            n = mapa_num.get(v, 1)
            linha_n.append(n)
            linha_t.append(mapa_rotulo[n])
        matriz_num.append(linha_n)
        matriz_txt.append(linha_t)

    matriz_num = np.array(matriz_num)

    fig, ax = plt.subplots(figsize=(12, 10))

    # Paleta customizada: Vermelho (0), Âmbar (1), Verde (2)
    cmap = mpl.colors.ListedColormap(["#d9534f", "#f0ad4e", "#5cb85c"])
    bounds = [-0.5, 0.5, 1.5, 2.5]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    sns.heatmap(
        matriz_num,
        cmap=cmap,
        norm=norm,
        annot=np.array(matriz_txt),
        fmt="",
        cbar=False,
        linewidths=1.5,
        linecolor="white",
        yticklabels=[f"{row['Nome_Real']} ({row['Status_Real']})" for _, row in df.iterrows()],
        xticklabels=nomes_personas,
        ax=ax,
        annot_kws={"fontsize": 9, "fontweight": "bold", "color": "white"}
    )

    # Linha divisória horizontal separando Falhas de Ativas
    ax.axhline(10, color="#2c3e50", linewidth=3, linestyle="-")
    ax.text(8.1, 5, "GRUPO 1: FALHAS HISTÓRICAS", rotation=270, verticalalignment="center", fontweight="bold", fontsize=10, color="#c0392b")
    ax.text(8.1, 15, "GRUPO 2: ATIVAS / SUCESSO", rotation=270, verticalalignment="center", fontweight="bold", fontsize=10, color="#27ae60")

    ax.set_title("Veredito Lean por Condição Experimental (Ano de Gênese)", fontsize=13, pad=15)
    plt.xticks(rotation=30, ha="right", fontweight="bold")
    plt.yticks(fontweight="bold")

    # Legenda manual no rodapé
    patches = [
        mpl.patches.Patch(color="#d9534f", label="Reprovação por Showstopper (Descarte)"),
        mpl.patches.Patch(color="#f0ad4e", label="Necessita Pivotagem"),
        mpl.patches.Patch(color="#5cb85c", label="Avançar para MVP")
    ]
    ax.legend(handles=patches, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=True, fontsize=10)

    plt.tight_layout()
    caminho = os.path.join(pasta_saida, "figura2_heatmap_startups_personas.png")
    plt.savefig(caminho, bbox_inches="tight")
    plt.close()
    print(f"   [OK] Salvo em: {caminho}")


def gerar_figura3_taxa_bloqueio_falhas(df: pd.DataFrame, pasta_saida: str):
    """
    Figura 3: Taxa de Bloqueio nas Startups com Falha Real (Pivotagem + Descarte)
    Destacando a eficácia das Personas Críticas em relação ao Controle.
    """
    print("-> Gerando Figura 3: Taxa de Bloqueio nas Falhas...")
    falhas = df[df["Status_Real"] == "Falha"]
    tot = len(falhas)

    prefixos = [p[0] for p in PERSONAS_ORDEM]
    nomes_curtos = [p[1] for p in PERSONAS_ORDEM]

    taxas_bloqueio = []
    taxas_descarte = []
    taxas_pivot = []

    for p in prefixos:
        col = f"{p}_Decisao_Lean"
        des = (falhas[col] == "Reprovação por Showstopper (Descarte)").sum() / tot * 100
        piv = (falhas[col] == "Necessita Pivotagem").sum() / tot * 100
        taxas_bloqueio.append(des + piv)
        taxas_descarte.append(des)
        taxas_pivot.append(piv)

    fig, ax = plt.subplots(figsize=(10, 5.5))

    cores_barras = ["#7f8c8d", "#d35400", "#c0392b", "#2980b9", "#16a085", "#8e44ad", "#27ae60", "#2c3e50"]
    x = np.arange(len(prefixos))

    barras = ax.bar(x, taxas_bloqueio, color=cores_barras, width=0.55, edgecolor="#333333", linewidth=0.8)

    # Linha de referência do Baseline Puro (Base = 60%)
    taxa_base = taxas_bloqueio[0]
    ax.axhline(taxa_base, color="#7f8c8d", linestyle="--", linewidth=1.5, label=f"Linha de Base (Controle Puro = {taxa_base:.0f}%)")

    for bar, tb, td in zip(barras, taxas_bloqueio, taxas_descarte):
        altura = bar.get_height()
        texto = f"{tb:.0f}%\n({td:.0f}% desc)" if td > 0 else f"{tb:.0f}%"
        ax.annotate(texto,
                    xy=(bar.get_x() + bar.get_width() / 2, altura),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_ylabel("Taxa de Bloqueio das Falhas (% Pivot + Descarte)")
    ax.set_title("Capacidade de Detecção de Riscos nas Startups com Falha Histórica", fontsize=12, pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(nomes_curtos, rotation=25, ha="right", fontweight="bold")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", frameon=True)

    plt.tight_layout()
    caminho = os.path.join(pasta_saida, "figura3_taxa_bloqueio_falhas.png")
    plt.savefig(caminho, bbox_inches="tight")
    plt.close()
    print(f"   [OK] Salvo em: {caminho}")


def gerar_figura4_aderencia_causal(df: pd.DataFrame, pasta_saida: str):
    """
    Figura 4: Taxa de Aderência Causal das LOFAs na Taxonomia CB Insights
    (Acerto Estrito vs. Acerto Amplo por Persona nas Startups que Falharam).
    """
    print("-> Gerando Figura 4: Aderência Causal CB Insights...")
    falhas = df[df["Status_Real"] == "Falha"]
    tot = len(falhas)

    prefixos = [p[0] for p in PERSONAS_ORDEM]
    nomes_curtos = [p[1] for p in PERSONAS_ORDEM]

    taxas_estritas = []
    taxas_amplas = []

    for p in prefixos:
        est = falhas[f"{p}_Acerto_Causal_Estrito"].sum() / tot * 100
        amp = falhas[f"{p}_Acerto_Causal_Amplo"].sum() / tot * 100
        taxas_estritas.append(est)
        taxas_amplas.append(amp)

    x = np.arange(len(prefixos))
    largura = 0.35

    fig, ax = plt.subplots(figsize=(11, 5.5))

    b_est = ax.bar(x - largura/2, taxas_estritas, largura, label="Acerto Estrito (Causa Primária)", color="#2980b9", edgecolor="white")
    b_amp = ax.bar(x + largura/2, taxas_amplas, largura, label="Acerto Amplo (Causa Primária ou Secundárias)", color="#27ae60", edgecolor="white")

    for b in b_est:
        h = b.get_height()
        ax.annotate(f"{h:.0f}%", xy=(b.get_x() + b.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    for b in b_amp:
        h = b.get_height()
        ax.annotate(f"{h:.0f}%", xy=(b.get_x() + b.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax.set_ylabel("Taxa de Aderência Causal (%)")
    ax.set_title("Correspondência entre a Premissa Crítica (LOFA) e a Causa Real do Fracasso", fontsize=12, pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(nomes_curtos, rotation=25, ha="right", fontweight="bold")
    ax.set_ylim(0, 105)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(loc="upper left", frameon=True)

    plt.tight_layout()
    caminho = os.path.join(pasta_saida, "figura4_aderencia_causal_cbinsights.png")
    plt.savefig(caminho, bbox_inches="tight")
    plt.close()
    print(f"   [OK] Salvo em: {caminho}")


def gerar_figura5_distribuicao_causas(df: pd.DataFrame, pasta_saida: str):
    """
    Figura 5: Distribuição de Frequência das Categorias Diagnosticadas (LOFAs nas Falhas)
    versus Gabarito Histórico Real.
    """
    print("-> Gerando Figura 5: Distribuição de Causas Diagnosticadas...")
    falhas = df[df["Status_Real"] == "Falha"]

    # Contagem no Gabarito Real
    gabarito_counts = falhas["Rotulo_Categorico"].value_counts()

    # Contagem nas LOFAs de todas as personas
    diagnosticos = []
    prefixos = [p[0] for p in PERSONAS_ORDEM]
    for p in prefixos:
        diagnosticos.extend(falhas[f"{p}_LOFA_Categoria"].dropna().tolist())

    diag_counts = pd.Series(diagnosticos).value_counts()

    # Consolidar dataframe comparativo
    todas_categorias = list(set(gabarito_counts.index).union(set(diag_counts.index)))
    comp_df = pd.DataFrame(index=todas_categorias)
    comp_df["Gabarito_Real_Pct"] = (gabarito_counts / len(falhas) * 100).fillna(0)
    comp_df["Diagnostico_IA_Pct"] = (diag_counts / len(diagnosticos) * 100).fillna(0)
    comp_df = comp_df.sort_values(by="Diagnostico_IA_Pct", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(comp_df))
    h = 0.38

    ax.barh(y + h/2, comp_df["Diagnostico_IA_Pct"], h, label="Diagnóstico do Comitê de LLMs (LOFAs)", color="#34495e")
    ax.barh(y - h/2, comp_df["Gabarito_Real_Pct"], h, label="Causa Primária Histórica (CB Insights)", color="#e74c3c")

    ax.set_yticks(y)
    ax.set_yticklabels(comp_df.index, fontweight="bold")
    ax.set_xlabel("Frequência Relativa (%)")
    ax.set_title("Prevalência de Causas: Diagnóstico Precoce da IA vs. Fato Histórico", fontsize=12, pad=12)
    ax.legend(loc="lower right", frameon=True)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    plt.tight_layout()
    caminho = os.path.join(pasta_saida, "figura5_distribuicao_causas_diagnosticadas.png")
    plt.savefig(caminho, bbox_inches="tight")
    plt.close()
    print(f"   [OK] Salvo em: {caminho}")


def gerar_tabelas_ibge(df: pd.DataFrame, pasta_saida: str):
    """
    Gera tabelas estruturadas no padrão estatístico do IBGE.
    """
    print("-> Gerando Tabelas Estatísticas (Padrão IBGE)...")

    # -------------------------------------------------------------------------
    # TABELA 1: Distribuição Geral de Decisões Lean por Status Real
    # -------------------------------------------------------------------------
    prefixos = [p[0] for p in PERSONAS_ORDEM]
    records = []
    for p in prefixos:
        for _, row in df.iterrows():
            records.append({
                "Status": row["Status_Real"],
                "Decisao": row[f"{p}_Decisao_Lean"]
            })
    df_long = pd.DataFrame(records)
    tabela1 = pd.crosstab(df_long["Status"], df_long["Decisao"], margins=True)
    caminho_t1 = os.path.join(pasta_saida, "tabela1_distribuicao_decisoes_ibge.csv")
    tabela1.to_csv(caminho_t1, encoding="utf-8")
    print(f"   [OK] Tabela 1 salva em: {caminho_t1}")

    # -------------------------------------------------------------------------
    # TABELA 2: Desempenho Discriminatório por Persona
    # -------------------------------------------------------------------------
    linhas_t2 = []
    falhas = df[df["Status_Real"] == "Falha"]
    ativas = df[df["Status_Real"] == "Ativa"]

    for p, nome, papel in PERSONAS_ORDEM:
        col = f"{p}_Decisao_Lean"
        
        # Falhas
        tot_f = len(falhas)
        mvp_f = (falhas[col] == "Avançar para MVP").sum() / tot_f * 100
        piv_f = (falhas[col] == "Necessita Pivotagem").sum() / tot_f * 100
        des_f = (falhas[col] == "Reprovação por Showstopper (Descarte)").sum() / tot_f * 100
        bloq_f = piv_f + des_f

        # Ativas
        tot_a = len(ativas)
        mvp_a = (ativas[col] == "Avançar para MVP").sum() / tot_a * 100
        piv_a = (ativas[col] == "Necessita Pivotagem").sum() / tot_a * 100
        des_a = (ativas[col] == "Reprovação por Showstopper (Descarte)").sum() / tot_a * 100

        linhas_t2.append({
            "Condição Experimental": nome,
            "Papel": papel,
            "Falha: MVP (%)": round(mvp_f, 1),
            "Falha: Pivotagem (%)": round(piv_f, 1),
            "Falha: Descarte (%)": round(des_f, 1),
            "Falha: Taxa Total de Bloqueio (%)": round(bloq_f, 1),
            "Ativa: MVP (%)": round(mvp_a, 1),
            "Ativa: Pivotagem (%)": round(piv_a, 1),
            "Ativa: Descarte (%)": round(des_a, 1)
        })

    tabela2 = pd.DataFrame(linhas_t2)
    caminho_t2 = os.path.join(pasta_saida, "tabela2_desempenho_por_persona_ibge.csv")
    tabela2.to_csv(caminho_t2, index=False, encoding="utf-8")
    print(f"   [OK] Tabela 2 salva em: {caminho_t2}")

    # -------------------------------------------------------------------------
    # TABELA 3: Aderência Causal das LOFAs na Taxonomia CB Insights
    # -------------------------------------------------------------------------
    linhas_t3 = []
    for p, nome, papel in PERSONAS_ORDEM:
        est = falhas[f"{p}_Acerto_Causal_Estrito"].sum()
        amp = falhas[f"{p}_Acerto_Causal_Amplo"].sum()
        tot = len(falhas)
        linhas_t3.append({
            "Persona": nome,
            "Papel": papel,
            "Acertos Estritos (Primária)": f"{int(est)} de {tot}",
            "Taxa Estrita (%)": round((est / tot) * 100, 1),
            "Acertos Amplos (Primária ou Secundária)": f"{int(amp)} de {tot}",
            "Taxa Ampla (%)": round((amp / tot) * 100, 1)
        })

    tabela3 = pd.DataFrame(linhas_t3)
    caminho_t3 = os.path.join(pasta_saida, "tabela3_aderencia_causal_cbinsights_ibge.csv")
    tabela3.to_csv(caminho_t3, index=False, encoding="utf-8")
    print(f"   [OK] Tabela 3 salva em: {caminho_t3}")

    # -------------------------------------------------------------------------
    # TABELA 4: Matriz de Decisões Completa (20 Startups x 8 Personas)
    # -------------------------------------------------------------------------
    colunas_t4 = ["Nome_Real", "Status_Real", "Ano_Fundacao", "Setor_Industria"]
    for p in prefixos:
        colunas_t4.append(f"{p}_Decisao_Lean")
    tabela4 = df[colunas_t4].copy()
    caminho_t4 = os.path.join(pasta_saida, "tabela4_matriz_veredito_completa.csv")
    tabela4.to_csv(caminho_t4, index=False, encoding="utf-8")
    print(f"   [OK] Tabela 4 salva em: {caminho_t4}")


def main():
    parser = argparse.ArgumentParser(description="Gerador Canônico de Artefatos para o TCC")
    parser.add_argument("--input", type=str, default="resultados/resultados_lean_canvas_com_categorias_lofa.csv")
    parser.add_argument("--output-dir", type=str, default=PASTA_ANEXOS)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    print("=" * 70)
    print("GERAÇÃO DE ARTEFATOS ACADÊMICOS (FIGURAS 300 DPI + TABELAS IBGE)")
    print(f"Fonte: {args.input} | Destino: {args.output_dir}")
    print("=" * 70)

    df = carregar_dados(args.input)

    gerar_figura1_distribuicao_decisoes(df, args.output_dir)
    gerar_figura2_heatmap_decisoes(df, args.output_dir)
    gerar_figura3_taxa_bloqueio_falhas(df, args.output_dir)
    gerar_figura4_aderencia_causal(df, args.output_dir)
    gerar_figura5_distribuicao_causas(df, args.output_dir)
    gerar_tabelas_ibge(df, args.output_dir)

    print("=" * 70)
    print("TODOS OS ARTEFATOS GERADOS COM SUCESSO!")
    print("=" * 70)


if __name__ == "__main__":
    main()
