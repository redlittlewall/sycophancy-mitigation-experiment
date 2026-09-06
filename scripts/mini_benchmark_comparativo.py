#!/usr/bin/env python3
"""
Mini-benchmark comparativo entre qwen2.5:14b e qwen2.5:32b
Startups: F01 (Quibi), S06 (Mercado Livre), S01 (Airbnb)
Personas: Controle, Advogado do Diabo, Investidor Anjo
"""
import time
import json
import csv
import re
import requests
import pandas as pd

API_URL = "http://localhost:11434/api/chat"
DATASET_PATH = "dataset_experimento.csv"
OUTPUT_PATH = "resultados/mini_benchmark_resultados.csv"

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa as definições do experimento oficial
from experimento_tcc import (
    SYSTEM_TEMPLATE,
    USER_TEMPLATE,
    TAXONOMIA_STR,
    CONFIG_CONTROLE,
    CONFIG_DIABO,
    CONFIG_ANJO,
    fazer_parse_json,
)

PERSONAS_TESTE = [
    ("Con",   "Controle",          CONFIG_CONTROLE),
    ("Diabo", "Advogado do Diabo", CONFIG_DIABO),
    ("Anjo",  "Investidor Anjo",   CONFIG_ANJO),
]

STARTUPS_ALVO = ["F01", "S06", "S01"]
MODELOS = ["qwen2.5:14b", "qwen2.5:32b"]

def consultar(modelo, system_prompt, user_prompt):
    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2, "num_predict": 1500},
    }
    t0 = time.time()
    resp = requests.post(API_URL, json=payload, timeout=300)
    elapsed = round(time.time() - t0, 2)
    resp.raise_for_status()
    raw = resp.json().get("message", {}).get("content", "").strip()
    return raw, elapsed

def main():
    print("Iniciando Mini-Benchmark Comparativo...")
    df_raw = pd.read_csv(DATASET_PATH)
    df_sel = df_raw[df_raw["ID_Startup"].isin(STARTUPS_ALVO)].copy()
    
    registros = []
    
    for modelo in MODELOS:
        print(f"\n==================================================")
        print(f"🚀 TESTANDO MODELO: {modelo}")
        print(f"==================================================")
        
        for _, row in df_sel.iterrows():
            sid = row["ID_Startup"]
            sname = row["Nome_Real"]
            status = row["Status_Real"]
            print(f"\n--- Startup: {sid} - {sname} ({status}) ---")
            
            user_prompt = USER_TEMPLATE.format(
                setor=row["Setor_Industria"],
                ano_analise=row["Ano_Evento_Critico"],
                nome_anonimizado=row["Nome_Anonimizado"],
                modelo_negocios=row["Modelo_Negocios"],
                contexto_mercado=row["Contexto_Mercado_Equipe"],
            )
            
            for prefixo, nome_persona, config in PERSONAS_TESTE:
                system_prompt = SYSTEM_TEMPLATE.format(taxonomia=TAXONOMIA_STR, **config)
                print(f"  -> Executando persona: {nome_persona}...", end="", flush=True)
                
                try:
                    raw_resp, tempo_s = consultar(modelo, system_prompt, user_prompt)
                    cat, prob, veredito, rigor, _ = fazer_parse_json(raw_resp)
                    print(f" [OK] {tempo_s}s | {veredito} | Prob: {prob}% | Rigor: {rigor}")
                    
                    # Extrair resumo do risco critico
                    try:
                        clean = raw_resp.strip()
                        if clean.startswith("```"):
                            clean = re.sub(r"^```(?:json)?\s*", "", clean)
                            clean = re.sub(r"\s*```$", "", clean)
                        parsed_dict = json.loads(clean)
                        risco_critico = parsed_dict.get("risco_critico", "")
                        problema = parsed_dict.get("analise_problema_mercado", "")
                    except Exception:
                        risco_critico = ""
                        problema = ""

                    registros.append({
                        "Modelo": modelo,
                        "ID_Startup": sid,
                        "Nome_Real": sname,
                        "Status_Real": status,
                        "Persona": nome_persona,
                        "Veredito": veredito,
                        "Probabilidade": prob,
                        "Categoria_Risco": cat,
                        "Rigor": rigor,
                        "Tempo_Segundos": tempo_s,
                        "Risco_Critico": risco_critico[:200],
                        "Analise_Problema": problema[:200],
                    })
                except Exception as e:
                    print(f" [ERRO]: {e}")
                    registros.append({
                        "Modelo": modelo,
                        "ID_Startup": sid,
                        "Nome_Real": sname,
                        "Status_Real": status,
                        "Persona": nome_persona,
                        "Veredito": "ERRO",
                        "Probabilidade": -1,
                        "Categoria_Risco": str(e),
                        "Rigor": -1,
                        "Tempo_Segundos": 0,
                        "Risco_Critico": "",
                        "Analise_Problema": "",
                    })
                    
                # Salva a cada iteração para segurança
                pd.DataFrame(registros).to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print(f"\n✅ Mini-Benchmark finalizado! Resultados salvos em: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
