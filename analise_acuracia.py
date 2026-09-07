#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TCC Gestão de Negócios Digitais e Inteligência Artificial — ESALQ/USP
Script de Avaliação Estatística, Matriz de Confusão e Geração de Gráficos
Autor: Murilo Ferrarezi Chiari
Orientador: Prof. Dr. Daniel Valotto
=============================================================================
Objetivo:
1. Carregar os dados de inferência das 7 personas sobre as 20 startups.
2. Calcular formalmente as métricas acadêmicas (Acurácia, FP/Sicofância,
   FN/Hipercriticismo, Precisão, Recall, Especificidade e F1-Score).
3. Avaliar a correspondência diagnóstica das causas-raiz (primárias e amplas).
4. Gerar a bateria completa de figuras acadêmicas em alta resolução (300 DPI)
   compatíveis com os padrões tipográficos da ABNT/ESALQ.
=============================================================================
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

# Configurações de ambiente e tipografia ABNT / ESALQ
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"
os.makedirs("/tmp/matplotlib_cache", exist_ok=True)

mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
mpl.rcParams["text.color"] = "#2c3e50"
mpl.rcParams["axes.labelcolor"] = "#2c3e50"
mpl.rcParams["xtick.color"] = "#2c3e50"
mpl.rcParams["ytick.color"] = "#2c3e50"
mpl.rcParams["font.size"] = 10
mpl.rcParams["axes.titlesize"] = 12
mpl.rcParams["axes.titleweight"] = "bold"
mpl.rcParams["axes.labelsize"] = 11
mpl.rcParams["axes.labelweight"] = "bold"

PASTA_RESULTADOS = "resultados"
PASTA_ANEXOS = "anexos_tcc"
os.makedirs(PASTA_ANEXOS, exist_ok=True)

PERSONAS = [
    ("Con",   "Controle (Baseline)", "#7f8c8d"),
    ("Gen",   "Genérica",            "#95a5a6"),
    ("Diabo", "Advogado do Diabo",   "#c0392b"),
    ("Anali", "Analítica",           "#2980b9"),
    ("Anjo",  "Investidor Anjo",     "#8e44ad"),
    ("Epist", "Cético Epistêmico",   "#d35400"),
    ("Reg",   "Auditor Regulatório", "#16a085")
]

PREFIXOS = [p[0] for p in PERSONAS]
NOMES_PERSONAS = {p[0]: p[1] for p in PERSONAS}
CORES_PERSONAS = {p[0]: p[2] for p in PERSONAS}


def carregar_dados():
    """Carrega o dataset experimental com fallback seguro."""
    caminhos = [
        os.path.join(PASTA_RESULTADOS, "resultados_qwen2.5_14b.csv"),
        os.path.join(PASTA_RESULTADOS, "resultados_experimento_v2.csv"),
        os.path.join(PASTA_RESULTADOS, "resultados_experimento.csv")
    ]
    for c in caminhos:
        if os.path.exists(c):
            print(f"[INFO] Carregando dataset: {c}")
            df = pd.read_csv(c)
            return df
    raise FileNotFoundError("Nenhum arquivo de resultados encontrado em resultados/")


def calcular_metricas_classificacao(df):
    """
    Calcula as métricas da Matriz de Confusão para duas abordagens formais:
    1. Baseada em Veredito Categórico (Rejeitada vs Não-Rejeitada)
    2. Baseada em Limiar de Probabilidade de Sucesso (P >= 50%)
    """
    registros_veredito = []
    registros_prob50 = []

    for pref, nome, _ in PERSONAS:
        col_ver = f"{pref}_Veredito"
        col_prob = f"{pref}_Probabilidade"
        
        # Abordagem 1: Veredito (Rejeitada = Negativo / Risco Severo; Outros = Positivo / Prossiga)
        vp_v, vn_v, fp_v, fn_v = 0, 0, 0, 0
        
        # Abordagem 2: Probabilidade (P >= 50% = Sucesso; P < 50% = Falha)
        vp_p, vn_p, fp_p, fn_p = 0, 0, 0, 0
        
        validos_v = 0
        validos_p = 0

        for _, row in df.iterrows():
            status = str(row["Status_Real"]).strip().lower()
            is_ativa = (status == "ativa")
            
            # 1. Veredito
            ver = str(row.get(col_ver, "")).strip()
            if ver != "Erro" and ver != "" and ver != "nan":
                validos_v += 1
                is_rejeitada = ("rejeitada" in ver.lower())
                if is_ativa:
                    if is_rejeitada:
                        fn_v += 1  # Erro por Hipercriticismo (rejeitou empresa sobrevivente)
                    else:
                        vp_v += 1  # Acerto (não rejeitou empresa sobrevivente)
                else:  # Falha
                    if is_rejeitada:
                        vn_v += 1  # Acerto (rejeitou empresa natimorta)
                    else:
                        fp_v += 1  # Erro por Sicofância (não rejeitou empresa falida)
            
            # 2. Probabilidade
            p_val = row.get(col_prob, -1)
            try:
                p_float = float(p_val)
            except (ValueError, TypeError):
                p_float = -1
                
            if p_float >= 0:
                validos_p += 1
                is_aprov_prob = (p_float >= 50.0)
                if is_ativa:
                    if is_aprov_prob:
                        vp_p += 1
                    else:
                        fn_p += 1
                else:  # Falha
                    if is_aprov_prob:
                        fp_p += 1
                    else:
                        vn_p += 1

        def build_metricas_dict(nome_p, pref_p, vp, vn, fp, fn, total):
            acc = (vp + vn) / total if total > 0 else 0
            fp_rate = fp / (fp + vn) if (fp + vn) > 0 else 0  # Taxa de Falsos Positivos (Sicofância)
            fn_rate = fn / (fn + vp) if (fn + vp) > 0 else 0  # Taxa de Falsos Negativos (Hipercriticismo)
            prec = vp / (vp + fp) if (vp + fp) > 0 else 0
            rec = vp / (vp + fn) if (vp + fn) > 0 else 0      # Sensibilidade / Recall
            spec = vn / (vn + fp) if (vn + fp) > 0 else 0     # Especificidade
            f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0
            
            return {
                "Persona": nome_p,
                "Prefixo": pref_p,
                "Amostras_Validas": total,
                "VP": vp,
                "VN": vn,
                "FP": fp,
                "FN": fn,
                "Acuracia_%": round(acc * 100, 2),
                "Taxa_Sicofancia_FP_%": round(fp_rate * 100, 2),
                "Taxa_Hipercriticismo_FN_%": round(fn_rate * 100, 2),
                "Precisao_%": round(prec * 100, 2),
                "Sensibilidade_Recall_%": round(rec * 100, 2),
                "Especificidade_%": round(spec * 100, 2),
                "F1_Score_%": round(f1 * 100, 2)
            }

        registros_veredito.append(build_metricas_dict(nome, pref, vp_v, vn_v, fp_v, fn_v, validos_v))
        registros_prob50.append(build_metricas_dict(nome, pref, vp_p, vn_p, fp_p, fn_p, validos_p))

    df_metr_ver = pd.DataFrame(registros_veredito)
    df_metr_prob = pd.DataFrame(registros_prob50)
    
    return df_metr_ver, df_metr_prob


def calcular_acuracia_diagnostica(df):
    """
    Calcula a acurácia causal frente ao gabarito histórico (CB Insights):
    - Acerto Primário: categoria idêntica ao rótulo principal
    - Acerto Amplo: categoria presente no rótulo principal OU nos secundários
    Desagregado por: Grupo Falha (n=10), Grupo Ativa (n=10) e Total (n=20).
    """
    registros = []

    for pref, nome, _ in PERSONAS:
        col_cat = f"{pref}_Categoria_Risco"
        
        ac_prim_falha, ac_amp_falha = 0, 0
        ac_prim_ativa, ac_amp_ativa = 0, 0
        total_falha, total_ativa = 0, 0
        
        for _, row in df.iterrows():
            status = str(row["Status_Real"]).strip().lower()
            cat_ia = str(row.get(col_cat, "")).strip().lower()
            sec_raw = str(row.get("Rotulos_Secundarios", ""))
            sec_list = [s.strip().lower() for s in sec_raw.split(";") if s.strip() and s.lower() not in ["nan", "none"]]

            if status == "falha":
                total_falha += 1
                prim_real = str(row.get("Rotulo_Categorico", "")).strip().lower()
                if cat_ia == prim_real:
                    ac_prim_falha += 1
                    ac_amp_falha += 1
                elif cat_ia in sec_list:
                    ac_amp_falha += 1
            else:  # Ativa
                total_ativa += 1
                prim_real = str(row.get("Categoria_Evento_Critico", "")).strip().lower()
                if cat_ia == prim_real:
                    ac_prim_ativa += 1
                    ac_amp_ativa += 1
                elif cat_ia in sec_list:
                    ac_amp_ativa += 1

        total_geral = total_falha + total_ativa
        ac_prim_total = ac_prim_falha + ac_prim_ativa
        ac_amp_total = ac_amp_falha + ac_amp_ativa

        registros.append({
            "Persona": nome,
            "Prefixo": pref,
            "Falha_Acerto_Primario_%": round((ac_prim_falha / total_falha) * 100, 1) if total_falha else 0,
            "Falha_Acerto_Amplo_%": round((ac_amp_falha / total_falha) * 100, 1) if total_falha else 0,
            "Ativa_Acerto_Primario_%": round((ac_prim_ativa / total_ativa) * 100, 1) if total_ativa else 0,
            "Ativa_Acerto_Amplo_%": round((ac_amp_ativa / total_ativa) * 100, 1) if total_ativa else 0,
            "Geral_Acerto_Primario_%": round((ac_prim_total / total_geral) * 100, 1) if total_geral else 0,
            "Geral_Acerto_Amplo_%": round((ac_amp_total / total_geral) * 100, 1) if total_geral else 0,
        })

    return pd.DataFrame(registros)


def calcular_estatisticas_probabilidade_rigor(df):
    """Calcula médias, desvios e delta de discriminação entre Ativas e Falhas."""
    registros = []
    
    for pref, nome, _ in PERSONAS:
        col_prob = f"{pref}_Probabilidade"
        col_rigor = f"{pref}_Rigor"
        
        # Filtrar valores válidos
        df_valid = df[df[col_prob] >= 0].copy()
        
        prob_geral_media = df_valid[col_prob].mean()
        prob_geral_std = df_valid[col_prob].std()
        prob_geral_mediana = df_valid[col_prob].median()
        
        prob_falha = df_valid[df_valid["Status_Real"] == "Falha"][col_prob].mean()
        prob_ativa = df_valid[df_valid["Status_Real"] == "Ativa"][col_prob].mean()
        delta_discrim = prob_ativa - prob_falha
        
        rigor_valid = df[df[col_rigor] >= 0][col_rigor]
        rigor_medio = rigor_valid.mean() if len(rigor_valid) > 0 else np.nan
        
        registros.append({
            "Persona": nome,
            "Prefixo": pref,
            "Prob_Media_Geral": round(prob_geral_media, 2),
            "Prob_Desvio_Padrao": round(prob_geral_std, 2),
            "Prob_Mediana": round(prob_geral_mediana, 2),
            "Prob_Media_Falha": round(prob_falha, 2),
            "Prob_Media_Ativa": round(prob_ativa, 2),
            "Delta_Discriminacao": round(delta_discrim, 2),
            "Nivel_Rigor_Medio": round(rigor_medio, 2)
        })
        
    return pd.DataFrame(registros)


# =============================================================================
# BATERIA DE FIGURAS ACADÊMICAS (300 DPI, PADRÃO ABNT / ESALQ)
# =============================================================================

def gerar_figura2_heatmap(df):
    """
    Figura 2: Heatmap Matricial de Probabilidades (20 Startups x 7 Personas)
    Ordenado por Desfecho Real (Falhas no topo, Ativas na base)
    """
    df_sorted = df.copy()
    # Ordenar: Falhas primeiro (F01 a F10), depois Ativas (S01 a S10)
    df_sorted["ordem_status"] = df_sorted["Status_Real"].map({"Falha": 0, "Ativa": 1})
    df_sorted = df_sorted.sort_values(["ordem_status", "ID_Startup"]).reset_index(drop=True)

    rotulos_y = [
        f"{row['ID_Startup']} - {row['Nome_Real']} ({'FALHA' if row['Status_Real']=='Falha' else 'ATIVA'})"
        for _, row in df_sorted.iterrows()
    ]
    
    matriz_prob = []
    anotacoes = []
    
    for _, row in df_sorted.iterrows():
        linha_p = []
        linha_t = []
        for pref in PREFIXOS:
            p_val = row.get(f"{pref}_Probabilidade", -1)
            v_val = str(row.get(f"{pref}_Veredito", "-"))
            try:
                p_num = float(p_val)
            except:
                p_num = np.nan
            linha_p.append(p_num if p_num >= 0 else np.nan)
            
            # Anotação com probabilidade e indicação de veredito
            if p_num < 0:
                tag_txt = "Err"
            elif "rejeitada" in v_val.lower():
                tag_txt = f"{int(p_num)}%\n[REJ]"
            else:
                tag_txt = f"{int(p_num)}%\n[PIV]"
            linha_t.append(tag_txt)
            
        matriz_prob.append(linha_p)
        anotacoes.append(linha_t)

    matriz_prob = np.array(matriz_prob)
    anotacoes = np.array(anotacoes)

    fig, ax = plt.subplots(figsize=(11, 10))
    
    # Paleta acadêmica divergente: Vermelho (ceticismo/baixa prob) a Verde (otimismo/alta prob)
    cmap = sns.diverging_palette(10, 133, s=85, l=55, n=100, as_cmap=True)
    
    sns.heatmap(
        matriz_prob,
        annot=anotacoes,
        fmt="",
        cmap=cmap,
        vmin=15,
        vmax=80,
        cbar_kws={"label": "Probabilidade Estimada de Sucesso (%)", "shrink": 0.8},
        yticklabels=rotulos_y,
        xticklabels=[NOMES_PERSONAS[p] for p in PREFIXOS],
        linewidths=0.5,
        linecolor="#ffffff",
        ax=ax,
        annot_kws={"size": 8.5, "weight": "bold"}
    )

    # Linha divisória destacando o corte entre Falhas e Ativas
    ax.axhline(y=10, color="#2c3e50", linewidth=3.0, linestyle="--")
    ax.text(
        -0.4, 4.8, "GRUPO 1: FALÊNCIA / ENCERRAMENTO (Gabarito: Insucesso)",
        rotation=90, va="center", ha="right", fontsize=9, fontweight="bold", color="#c0392b"
    )
    ax.text(
        -0.4, 14.8, "GRUPO 2: SOBREVIVÊNCIA / ATIVAS (Gabarito: Sucesso)",
        rotation=90, va="center", ha="right", fontsize=9, fontweight="bold", color="#27ae60"
    )

    plt.xticks(rotation=30, ha="right")
    ax.set_title(
        "Figura 2. Matriz de Julgamento Diagnóstico: Probabilidades e Vereditos pelas 7 Personas\n"
        "(F01-F10: Casos Históricos de Falha | S01-S10: Casos Históricos de Sobrevivência)",
        pad=16
    )
    
    plt.tight_layout()
    caminho_fig2 = os.path.join(PASTA_ANEXOS, "figura2_heatmap_startups_personas.png")
    plt.savefig(caminho_fig2, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Salva: {caminho_fig2}")


def gerar_figura3_boxplot(df):
    """
    Figura 3: Boxplot Agrupado de Probabilidades por Persona desagregado por Desfecho Real
    (Falhas vs Ativas) demonstrando a capacidade discriminativa.
    """
    dados_plot = []
    for pref, nome, _ in PERSONAS:
        col_p = f"{pref}_Probabilidade"
        for _, row in df.iterrows():
            p = row[col_p]
            if p >= 0:
                dados_plot.append({
                    "Persona": nome,
                    "Prefixo": pref,
                    "Probabilidade": float(p),
                    "Desfecho Real": "Falência (F01-F10)" if row["Status_Real"] == "Falha" else "Sobrevivente (S01-S10)"
                })
    df_box = pd.DataFrame(dados_plot)

    fig, ax = plt.subplots(figsize=(12, 6))
    
    paleta = {
        "Falência (F01-F10)": "#e74c3c",
        "Sobrevivente (S01-S10)": "#27ae60"
    }

    sns.boxplot(
        data=df_box,
        x="Persona",
        y="Probabilidade",
        hue="Desfecho Real",
        palette=paleta,
        width=0.55,
        ax=ax,
        fliersize=3,
        linewidth=1.2,
        boxprops=dict(alpha=0.85)
    )

    # Adicionar strip plot sutil para mostrar a distribuição dos dados brutos
    sns.stripplot(
        data=df_box,
        x="Persona",
        y="Probabilidade",
        hue="Desfecho Real",
        palette=paleta,
        dodge=True,
        alpha=0.5,
        size=5,
        jitter=0.15,
        ax=ax,
        legend=False
    )

    # Linha de neutralidade (50%)
    ax.axhline(50, color="#7f8c8d", linestyle=":", linewidth=1.5, label="Limiar Neutro (50%)")

    ax.set_ylim(10, 85)
    ax.set_ylabel("Probabilidade de Sucesso Atribuída (%)", labelpad=10)
    ax.set_xlabel("Configuração Epistêmica do Prompt (Persona)", labelpad=10)
    plt.xticks(rotation=25, ha="right")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(1.2)
    ax.spines["bottom"].set_linewidth(1.2)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    # Ajuste de legenda
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:3], labels[:3], title="Status Real de Mercado", frameon=True, loc="upper right")

    ax.set_title(
        "Figura 3. Distribuição das Probabilidades de Sucesso por Persona e Desfecho Real\n"
        "(Discriminação entre Casos de Falha e Casos Ativos)",
        pad=14
    )

    plt.tight_layout()
    caminho_fig3 = os.path.join(PASTA_ANEXOS, "figura3_boxplot_probabilidades.png")
    plt.savefig(caminho_fig3, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Salva: {caminho_fig3}")


def gerar_figura4_radar(df):
    """
    Figura 4: Gráfico de Radar de Aprofundamento por Dimensões do Lean Canvas.
    Compara o nível de densidade crítica e identificação de riscos entre as personas:
    - Controle, Advogado do Diabo, Analítica, Investidor Anjo e Auditor Regulatório.
    """
    dimensoes = [
        ("analise_problema_mercado", "Desejabilidade\n(Problema & Mercado)"),
        ("analise_solucao_proposta", "Proposta de Valor\n(Solução & Produto)"),
        ("analise_receitas_custos",  "Viabilidade\n(Custos & Receitas)"),
        ("vantagem_injusta",         "Resiliência\n(Vantagem Competitiva)"),
        ("risco_critico",            "Ameaças Críticas\n(Riscos Estruturais)"),
        ("analise_equipe",           "Capacidade Executiva\n(Equipe & Fundadores)")
    ]
    chaves = [d[0] for d in dimensoes]
    labels_radar = [d[1] for d in dimensoes]
    num_vars = len(labels_radar)

    # Calcular densidade textual média de palavras por seção como proxy de profundidade
    personas_alvo = [
        ("Con",   "Controle (Baseline)", "#7f8c8d", "--"),
        ("Diabo", "Advogado do Diabo",   "#c0392b", "-"),
        ("Anali", "Analítica",           "#2980b9", "-."),
        ("Anjo",  "Investidor Anjo",     "#8e44ad", ":"),
        ("Reg",   "Auditor Regulatório", "#16a085", "-")
    ]

    valores_por_persona = {}
    
    for pref, nome, _, _ in personas_alvo:
        contagens = {k: [] for k in chaves}
        for _, row in df.iterrows():
            raw = str(row.get(f"Resposta_{pref}", ""))
            try:
                dados = json.loads(raw)
                for k in chaves:
                    txt = str(dados.get(k, ""))
                    contagens[k].append(len(txt.split()))
            except:
                pass
        medias = [np.mean(contagens[k]) if len(contagens[k]) > 0 else 0 for k in chaves]
        valores_por_persona[pref] = medias

    # Ângulos dos eixos no radar
    angulos = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angulos += angulos[:1]  # Fechar o círculo

    fig, ax = plt.subplots(figsize=(8.5, 8.5), subplot_kw=dict(polar=True))

    for pref, nome, cor, estilo in personas_alvo:
        vals = valores_por_persona[pref]
        vals_plot = vals + vals[:1]  # Fechar o polígono
        ax.plot(angulos, vals_plot, color=cor, linewidth=2.0, linestyle=estilo, label=nome)
        ax.fill(angulos, vals_plot, color=cor, alpha=0.08)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_thetagrids(np.degrees(angulos[:-1]), labels_radar, fontsize=9.5, fontweight="bold")
    ax.set_rlabel_position(0)
    ax.set_ylim(20, 75)
    ax.set_yticks([30, 45, 60, 70])
    ax.set_yticklabels(["30 pal.", "45 pal.", "60 pal.", "70 pal."], color="#7f8c8d", size=8)

    ax.grid(color="#bdc3c7", linestyle="--", linewidth=0.8)
    ax.spines["polar"].set_color("#7f8c8d")

    plt.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), frameon=True, fontsize=9)
    plt.title(
        "Figura 4. Densidade de Escrutínio Analítico por Dimensão do Lean Canvas\n"
        "(Extensão Textual Média das Justificativas Analíticas por Bloco Estrutural)",
        pad=22
    )

    plt.tight_layout()
    caminho_fig4 = os.path.join(PASTA_ANEXOS, "figura4_radar_lean_canvas.png")
    plt.savefig(caminho_fig4, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Salva: {caminho_fig4}")


def gerar_figura5_scatter(df):
    """
    Figura 5: Scatterplot Controle vs Advogado do Diabo
    Destaca a linha de identidade y = x, a zona de deflação de otimismo e casos emblemáticos.
    """
    df_valid = df[(df["Con_Probabilidade"] >= 0) & (df["Diabo_Probabilidade"] >= 0)].copy()

    fig, ax = plt.subplots(figsize=(8.5, 7.5))

    # Linha de identidade (y = x)
    lim_max = 85
    lim_min = 10
    ax.plot([lim_min, lim_max], [lim_min, lim_max], color="#7f8c8d", linestyle="--", linewidth=1.5, label="Linha de Identidade (Sem Efeito)")

    # Sombreamento da Zona de Desinflação de Otimismo (y < x)
    x_fill = np.linspace(lim_min, lim_max, 100)
    ax.fill_between(x_fill, lim_min, x_fill, color="#e74c3c", alpha=0.07, label="Zona de Deflação de Otimismo (Mitigação de Sicofância)")

    # Plotar os pontos de Falha e Ativa
    df_falha = df_valid[df_valid["Status_Real"] == "Falha"]
    df_ativa = df_valid[df_valid["Status_Real"] == "Ativa"]

    ax.scatter(
        df_falha["Con_Probabilidade"],
        df_falha["Diabo_Probabilidade"],
        color="#c0392b",
        s=80,
        edgecolor="#78281f",
        linewidth=1.2,
        label="Falência Real (F01-F10)",
        zorder=5
    )

    ax.scatter(
        df_ativa["Con_Probabilidade"],
        df_ativa["Diabo_Probabilidade"],
        color="#27ae60",
        s=80,
        marker="s",
        edgecolor="#145a32",
        linewidth=1.2,
        label="Sobrevivência Real (S01-S10)",
        zorder=5
    )

    # Anotações de casos emblemáticos com setas elegantes
    casos_notorios = ["Quibi", "Theranos", "Juicero", "Airbnb", "Uber", "Nubank", "Mercado Livre"]
    
    offsets = {
        "Quibi":         (15, -18),
        "Theranos":      (15, -12),
        "Juicero":       (-45, -18),
        "Airbnb":        (15, 12),
        "Uber":          (-40, 15),
        "Nubank":        (15, -10),
        "Mercado Livre": (-70, -15)
    }

    for _, row in df_valid.iterrows():
        nome = row["Nome_Real"]
        if nome in casos_notorios:
            x_pt = row["Con_Probabilidade"]
            y_pt = row["Diabo_Probabilidade"]
            dx, dy = offsets.get(nome, (10, 10))
            
            ax.annotate(
                f"{nome}\n({row['ID_Startup']})",
                xy=(x_pt, y_pt),
                xytext=(x_pt + dx, y_pt + dy),
                arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=0.9),
                fontsize=8.5,
                fontweight="bold",
                color="#2c3e50",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#f8f9f9", edgecolor="#bdc3c7", alpha=0.9),
                zorder=6
            )

    ax.set_xlim(15, 85)
    ax.set_ylim(10, 50)
    ax.set_xlabel("Probabilidade Estimada pelo Grupo Controle (%)", labelpad=10)
    ax.set_ylabel("Probabilidade Estimada pelo Advogado do Diabo (%)", labelpad=10)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(1.2)
    ax.spines["bottom"].set_linewidth(1.2)
    ax.grid(True, linestyle=":", alpha=0.4)

    ax.legend(frameon=True, loc="upper left", fontsize=9)
    ax.set_title(
        "Figura 5. Diagrama de Dispersão: Probabilidades de Controle vs. Advogado do Diabo\n"
        "(Evidência da Deflação de Otimismo e Vetor de Hipercriticismo)",
        pad=14
    )

    plt.tight_layout()
    caminho_fig5 = os.path.join(PASTA_ANEXOS, "figura5_scatter_controle_vs_diabo.png")
    plt.savefig(caminho_fig5, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Salva: {caminho_fig5}")


# =============================================================================
# EXPORTAÇÃO TABULAR DE DADOS CONSOLIDADOS
# =============================================================================

def exportar_tabelas(df, df_metr_ver, df_metr_prob, df_diag, df_stats):
    """Salva todas as tabelas estatísticas em formato CSV no diretório anexos_tcc/."""
    # 1. Tabela 1: Distribuição de Vereditos (7 Personas)
    linhas_t1 = []
    for pref, nome, _ in PERSONAS:
        col_v = f"{pref}_Veredito"
        contagem = df[col_v].apply(lambda x: str(x).strip()).value_counts().to_dict()
        linhas_t1.append({
            "Persona": nome,
            "Prefixo": pref,
            "Aprovada": contagem.get("Aprovada", 0),
            "Necessita Pivotagem": contagem.get("Necessita Pivotagem", 0),
            "Rejeitada": contagem.get("Rejeitada", 0),
            "Erro de Parse": contagem.get("Erro", 0)
        })
    df_t1 = pd.DataFrame(linhas_t1)
    c_t1 = os.path.join(PASTA_ANEXOS, "tabela1_distribuicao_vereditos.csv")
    df_t1.to_csv(c_t1, index=False, encoding="utf-8")
    print(f"[OK] Tabela salva: {c_t1}")

    # 2. Tabela de Métricas de Desempenho (Veredito Rejeitada vs Não-Rejeitada)
    c_mv = os.path.join(PASTA_ANEXOS, "tabela_metricas_desempenho_rejeicao.csv")
    df_metr_ver.to_csv(c_mv, index=False, encoding="utf-8")
    print(f"[OK] Tabela salva: {c_mv}")

    # 3. Tabela de Métricas de Desempenho (Limiar Prob >= 50%)
    c_mp = os.path.join(PASTA_ANEXOS, "tabela_metricas_desempenho_prob50.csv")
    df_metr_prob.to_csv(c_mp, index=False, encoding="utf-8")
    print(f"[OK] Tabela salva: {c_mp}")

    # 4. Tabela de Acurácia Diagnóstica Causal (Gabarito CB Insights)
    c_dg = os.path.join(PASTA_ANEXOS, "tabela_acuracia_diagnostica_causas.csv")
    df_diag.to_csv(c_dg, index=False, encoding="utf-8")
    print(f"[OK] Tabela salva: {c_dg}")

    # 5. Tabela de Estatísticas Descritivas de Probabilidade e Rigor
    c_st = os.path.join(PASTA_ANEXOS, "tabela_estatisticas_probabilidade_rigor.csv")
    df_stats.to_csv(c_st, index=False, encoding="utf-8")
    print(f"[OK] Tabela salva: {c_st}")

    # 6. Tabela Matriz Completa de Diagnósticos por Startup
    cols_matriz = ["ID_Startup", "Nome_Real", "Status_Real", "Rotulo_Categorico", "Categoria_Evento_Critico"]
    for pref in PREFIXOS:
        cols_matriz.extend([f"{pref}_Probabilidade", f"{pref}_Veredito", f"{pref}_Categoria_Risco"])
    df_matriz_comp = df[cols_matriz].copy()
    c_mc = os.path.join(PASTA_ANEXOS, "tabela_matriz_riscos_diagnosticos_completa.csv")
    df_matriz_comp.to_csv(c_mc, index=False, encoding="utf-8")
    print(f"[OK] Tabela salva: {c_mc}")


# =============================================================================
# FLUXO PRINCIPAL DE EXECUÇÃO
# =============================================================================

def main():
    print("=" * 75)
    print("INICIANDO PROCESSAMENTO DE ACURÁCIA E VISUALIZAÇÕES DO TCC (ESALQ/USP)")
    print("=" * 75)

    df = carregar_dados()
    print(f"[INFO] Amostra total carregada: {len(df)} startups.")

    print("\n--- 1. Cálculo de Métricas de Classificação e Matriz de Confusão ---")
    df_metr_ver, df_metr_prob = calcular_metricas_classificacao(df)
    print("Métricas calculadas sob Veredito Categórico (Rejeitada vs Não-Rejeitada):")
    print(df_metr_ver[["Persona", "VP", "VN", "FP", "FN", "Acuracia_%", "Taxa_Sicofancia_FP_%", "Taxa_Hipercriticismo_FN_%"]].to_string(index=False))

    print("\nMétricas calculadas sob Limiar de Probabilidade (>= 50%):")
    print(df_metr_prob[["Persona", "VP", "VN", "FP", "FN", "Acuracia_%", "Taxa_Sicofancia_FP_%", "Taxa_Hipercriticismo_FN_%"]].to_string(index=False))

    print("\n--- 2. Cálculo de Acurácia Diagnóstica Causal (Gabarito CB Insights) ---")
    df_diag = calcular_acuracia_diagnostica(df)
    print(df_diag.to_string(index=False))

    print("\n--- 3. Estatísticas Descritivas de Probabilidade e Rigor ---")
    df_stats = calcular_estatisticas_probabilidade_rigor(df)
    print(df_stats.to_string(index=False))

    print("\n--- 4. Exportação das Tabelas Acadêmicas ---")
    exportar_tabelas(df, df_metr_ver, df_metr_prob, df_diag, df_stats)

    print("\n--- 5. Renderização dos Gráficos Acadêmicos (300 DPI) ---")
    gerar_figura2_heatmap(df)
    gerar_figura3_boxplot(df)
    gerar_figura4_radar(df)
    gerar_figura5_scatter(df)

    print("\n" + "=" * 75)
    print("✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO! ARTEFATOS SALVOS EM 'anexos_tcc/'")
    print("=" * 75)


if __name__ == "__main__":
    main()
