#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Classificador Pós-Hoc de LOFA via LLM-as-a-Judge (Taxonomia CB Insights)
TCC ESALQ/USP — Autor: Murilo Ferrarezi Chiari | Orientador: Prof. Dr. Daniel Valotto
=============================================================================
Protocolo de Classificação Cega:
1. Recebe a premissa de salto de fé (LOFA) gerada em texto livre na V6.
2. Consulta o LLM atuando estritamente como juiz semântico desacoplado.
3. Enquadra a LOFA nas categorias padronizadas da taxonomia da CB Insights.
4. Cruza com o gabarito real de falhas (Rotulo_Categorico e Rotulos_Secundarios).
5. Gera métricas quantitativas de Aderência Causal por Persona.
=============================================================================
"""

import argparse
import json
import os
import re
import sys
import requests
import pandas as pd
from tqdm import tqdm

LLM_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:14b"
TEMPERATURE = 0.1  # Baixa temperatura para classificação determinística e consistente

CATEGORIAS_CB_INSIGHTS = [
    "Sem necessidade de mercado",
    "Fim do caixa",
    "Problema de preço ou custo",
    "Modelo de negócios falho",
    "Problema regulatório ou legal",
    "Produto ruim",
    "Concorrência predatória",
    "Equipe inadequada",
    "Outro",
]

SISTEMA_JUIZ = """Você é um especialista em análise de conteúdo e taxonomia de insucesso de startups.
Sua tarefa é analisar a "Premissa de Salto de Fé" (LOFA) formulada para um modelo de negócios e classificá-la em EXATAMENTE UMA das categorias padronizadas de falha da taxonomia CB Insights.

CATEGORIAS DISPONÍVEIS:
1. "Sem necessidade de mercado": Falta de demanda do cliente, ausência de dor real, público-alvo não quer o produto ou desinteresse.
2. "Fim do caixa": Esgotamento de reservas financeiras, queima descontrolada de capital (burn rate) ou incapacidade de captar investimento.
3. "Problema de preço ou custo": Custos operacionais unitários insustentáveis, margem unitária negativa ou preço inadequado ao consumidor.
4. "Modelo de negócios falho": Estrutura de monetização inviável, canais de aquisição ineficientes ou descompasso entre receita e custo.
5. "Problema regulatório ou legal": Barreiras de conformidade estatal, ausência de licenças, litígios judiciais ou bloqueio sanitário/institucional.
6. "Produto ruim": Falha funcional, hardware defeituoso, usabilidade deficiente ou tecnologia que não entrega o prometido.
7. "Concorrência predatória": Perda de tração para concorrentes diretos com maior escala, liquidez de rede ou capital.
8. "Equipe inadequada": Falta de competência técnica dos fundadores, desarmonia societária ou má execução operacional.
9. "Outro": Fatores que não se enquadram em nenhuma das anteriores.

Responda EXCLUSIVAMENTE em formato JSON válido:
{
  "categoria_cbinsights": "Nome exato de uma das categorias listadas",
  "justificativa_classificacao": "Uma frase objetiva explicando o enquadramento"
}"""

USER_TEMPLATE_JUIZ = """PREMISSA DE SALTO DE FÉ (LOFA) A SER CLASSIFICADA:
"{lofa_texto}"

Classifique em uma das categorias CB Insights."""


def consultar_juiz_llm(lofa_texto: str, model: str = MODEL_NAME) -> tuple:
    if not lofa_texto or str(lofa_texto).strip() == "" or str(lofa_texto).strip() == "nan":
        return "Outro", "LOFA não informada ou vazia"

    user_prompt = USER_TEMPLATE_JUIZ.format(lofa_texto=lofa_texto.strip())
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SISTEMA_JUIZ},
            {"role": "user", "content": user_prompt}
        ],
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": 300
        },
        "stream": False
    }

    try:
        resp = requests.post(LLM_API_URL, json=payload, timeout=60)
        resp.raise_for_status()
        conteudo = resp.json().get("message", {}).get("content", "").strip()

        # Parse JSON
        limpo = re.sub(r"```(?:json)?", "", conteudo).strip()
        dados = {}
        try:
            dados = json.loads(limpo)
        except json.JSONDecodeError:
            m = re.search(r"(\{.*\})", limpo, re.DOTALL)
            if m:
                dados = json.loads(m.group(1))

        categoria = dados.get("categoria_cbinsights", "Outro")
        justificativa = dados.get("justificativa_classificacao", "")

        # Normalização para lista canônica
        cat_normalizada = "Outro"
        for c in CATEGORIAS_CB_INSIGHTS:
            if c.lower() in categoria.lower():
                cat_normalizada = c
                break

        return cat_normalizada, justificativa

    except Exception as e:
        return "Outro", f"Erro no juiz: {str(e)}"


def verificar_aderencia(cat_prevista: str, rotulo_primario: str, rotulos_secundarios: str) -> tuple:
    """Verifica se a categoria atribuída pela LOFA bate com a causa real de falha."""
    if not rotulo_primario or str(rotulo_primario).strip() in ["nan", "N/A - Empresa Sobrevivente"]:
        return False, False  # É empresa ativa

    primario_match = cat_prevista.lower() in str(rotulo_primario).lower() or str(rotulo_primario).lower() in cat_prevista.lower()
    
    secundario_match = False
    if rotulos_secundarios and str(rotulos_secundarios) != "nan":
        for sec in str(rotulos_secundarios).split(";"):
            if cat_prevista.lower() in sec.strip().lower() or sec.strip().lower() in cat_prevista.lower():
                secundario_match = True
                break

    # Categorias financeiras correlacionadas (Fim do caixa, Problema de preço ou custo, Modelo de negócios falho)
    financ_cats = ["fim do caixa", "problema de preço ou custo", "modelo de negócios falho"]
    is_financ_match = False
    if cat_prevista.lower() in financ_cats:
        for f in financ_cats:
            if f in str(rotulo_primario).lower() or f in str(rotulos_secundarios).lower():
                is_financ_match = True
                break

    acerto_estrito = primario_match
    acerto_amplo = primario_match or secundario_match or is_financ_match

    return acerto_estrito, acerto_amplo


def executar_classificacao(arquivo_entrada: str, arquivo_saida: str):
    print(f"Carregando resultados de: {arquivo_entrada}")
    df = pd.read_csv(arquivo_entrada)

    personas = ["Base", "Epist", "Diabo", "Anali", "Reg", "Anjo", "Prod", "Inov"]
    total_lofas = len(df) * len(personas)
    print(f"Total de LOFAs a classificar: {total_lofas} ({len(df)} startups x {len(personas)} personas)")

    os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)

    for p in personas:
        col_lofa = f"{p}_LOFA"
        if col_lofa not in df.columns:
            print(f"[AVISO] Coluna {col_lofa} não encontrada.")
            continue

        print(f"\nClassificando LOFAs da Persona: {p}...")
        for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"Juiz CB Insights [{p}]"):
            lofa = str(row.get(col_lofa, ""))
            cat, just = consultar_juiz_llm(lofa)
            
            df.at[idx, f"{p}_LOFA_Categoria"] = cat
            df.at[idx, f"{p}_LOFA_Justificativa_Juiz"] = just

            # Se for empresa de falha, verifica aderência com gabarito
            acerto_estrito, acerto_amplo = verificar_aderencia(
                cat, 
                row.get("Rotulo_Categorico", ""), 
                row.get("Rotulos_Secundarios", "")
            )
            df.at[idx, f"{p}_Acerto_Causal_Estrito"] = acerto_estrito if row.get("Status_Real") == "Falha" else None
            df.at[idx, f"{p}_Acerto_Causal_Amplo"] = acerto_amplo if row.get("Status_Real") == "Falha" else None

    # Salva dataset enriquecido
    df.to_csv(arquivo_saida, index=False, encoding="utf-8")
    print(f"\nResultados com categorias de LOFA salvos em: {arquivo_saida}")

    # Relatório de Aderência Causal nas Falhas
    falhas_df = df[df["Status_Real"] == "Falha"]
    print("\n" + "=" * 75)
    print("RELATÓRIO QUANTITATIVO DE ADERÊNCIA CAUSAL (ACERTO DA CAUSA DA FALHA)")
    print("=" * 75)
    print(f"{'Persona':8} | {'Acertos Estritos':16} | {'Taxa Estrita (%)':16} | {'Acertos Amplos':16} | {'Taxa Ampla (%)':14}")
    print("-" * 75)

    for p in personas:
        estritos = falhas_df[f"{p}_Acerto_Causal_Estrito"].sum()
        amplos = falhas_df[f"{p}_Acerto_Causal_Amplo"].sum()
        total = len(falhas_df)
        pct_est = (estritos / total) * 100 if total > 0 else 0
        pct_amp = (amplos / total) * 100 if total > 0 else 0
        print(f"{p:8} | {int(estritos):2d} de {total:2d}         | {pct_est:5.1f}%          | {int(amplos):2d} de {total:2d}         | {pct_amp:5.1f}%")

    print("=" * 75)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classificador Pós-Hoc de LOFA via LLM-as-a-Judge")
    parser.add_argument("--input", type=str, default="resultados/resultados_lean_canvas_completo.csv")
    parser.add_argument("--output", type=str, default="resultados/resultados_lean_canvas_com_categorias_lofa.csv")
    args = parser.parse_args()

    executar_classificacao(args.input, args.output)
