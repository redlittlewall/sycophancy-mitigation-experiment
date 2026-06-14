import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

# Configurações Tipográficas (ABNT/ESALQ)
mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
mpl.rcParams["text.color"] = "black"
mpl.rcParams["axes.labelcolor"] = "black"
mpl.rcParams["xtick.color"] = "black"
mpl.rcParams["ytick.color"] = "black"
mpl.rcParams["font.size"] = 11


def gerar_anexos_tcc():
    # 1. Carregar Dados
    caminho_entrada = "resultados/resultados_experimento.csv"
    try:
        df = pd.read_csv(caminho_entrada)
    except FileNotFoundError:
        print("[ERRO] Arquivo CSV não encontrado.")
        return

    os.makedirs("anexos_tcc", exist_ok=True)

    # Mapeamento
    personas = {
        "Controle (Baseline)": "Con",
        "Genérica": "Gen",
        "Analítica": "Anali",
        "Advogado do Diabo": "Diabo",
    }

    # Limpeza básica (transformar em numérico)
    for p in personas.values():
        df[f"{p}_Probabilidade"] = pd.to_numeric(
            df[f"{p}_Probabilidade"], errors="coerce"
        )

    print("Gerando artefatos para a tese...")

    # =====================================================================
    # FIGURA 1: Gráfico de Barras - Média de Probabilidade de Sucesso
    # =====================================================================
    medias_prob = {
        nome: df[f"{prefixo}_Probabilidade"].mean()
        for nome, prefixo in personas.items()
    }

    fig, ax = plt.subplots(figsize=(8, 5))

    nomes = list(medias_prob.keys())
    valores = list(medias_prob.values())

    # Criar um degradê de cinza para ilustrar a "queda" de probabilidade
    cores = ["#B0B0B0", "#7F7F7F", "#4C4C4C", "#1A1A1A"]

    barras = ax.bar(nomes, valores, color=cores, width=0.5)

    ax.grid(False)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(1.5)
    ax.spines["bottom"].set_linewidth(1.5)

    ax.set_ylabel(
        "Média de Probabilidade de Sucesso (%)", labelpad=12, fontweight="bold"
    )
    ax.set_ylim(0, 100)

    # Adicionar o valor exato acima de cada barra para clareza acadêmica
    for barra in barras:
        yval = barra.get_height()
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            yval + 2,
            f"{yval:.1f}%",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(
        "anexos_tcc/figura1_queda_probabilidade.png",
        dpi=300,
        bbox_inches="tight",
        format="png",
    )
    print("-> Figura 1 salva (figura1_queda_probabilidade.png)")

    # =====================================================================
    # TABELA 1: Distribuição de Vereditos por Persona
    # =====================================================================
    dados_veredito = []

    for nome, prefixo in personas.items():
        col_ver = f"{prefixo}_Veredito"
        # Contagem exata dos textos
        contagem = df[col_ver].apply(lambda x: str(x).strip()).value_counts().to_dict()

        dados_veredito.append(
            {
                "Persona": nome,
                "Aprovada": contagem.get("Aprovada", 0),
                "Necessita Pivotagem": contagem.get("Necessita Pivotagem", 0),
                "Rejeitada": contagem.get("Rejeitada", 0),
            }
        )

    df_tabela1 = pd.DataFrame(dados_veredito)
    df_tabela1.to_csv(
        "anexos_tcc/tabela1_distribuicao_vereditos.csv", index=False, encoding="utf-8"
    )
    print("-> Tabela 1 salva (tabela1_distribuicao_vereditos.csv)")

    # =====================================================================
    # TABELA 2: Matriz de Acurácia dos Riscos (Recorte de Casos Notórios)
    # =====================================================================
    startups_alvo = ["Airbnb", "Juicero", "Nubank", "Quibi", "Uber", "Beepi"]
    df_alvo = df[df["Nome_Real"].isin(startups_alvo)].copy()

    tabela2_cols = {
        "Startup": df_alvo["Nome_Real"],
        "Setor": df_alvo["Setor_Industria"],
        "Gabarito: Causa Principal (Real)": df_alvo["Rotulo_Categorico"],
        "Diagnóstico IA: Analítica": df_alvo["Anali_Categoria_Risco"],
        "Diagnóstico IA: Advogado do Diabo": df_alvo["Diabo_Categoria_Risco"],
    }

    df_tabela2 = pd.DataFrame(tabela2_cols)
    df_tabela2.to_csv(
        "anexos_tcc/tabela2_matriz_riscos_diagnosticos.csv",
        index=False,
        encoding="utf-8",
    )
    print("-> Tabela 2 salva (tabela2_matriz_riscos_diagnosticos.csv)")

    print("\nProcesso concluído! Os arquivos estão na pasta 'anexos_tcc'.")


if __name__ == "__main__":
    gerar_anexos_tcc()
