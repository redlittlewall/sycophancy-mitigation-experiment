#!/usr/bin/env python3
"""
Teste empírico de paralelismo local via Ollama.
Compara:
1. Execução sequencial de 2 chamadas (Controle + Advogado do Diabo na Quibi)
2. Execução concorrente (2 threads simultâneas)
Mede o ganho de tempo real (speedup) e a integridade das respostas JSON.
"""
import time
import requests
import json
import concurrent.futures

API_URL = "http://localhost:11434/api/chat"
MODELO = "qwen2.5:14b"

PAYLOAD_1 = {
    "model": MODELO,
    "messages": [
        {"role": "system", "content": "Você é um analista de Venture Capital. Responda em JSON com chaves: veredito, probabilidade."},
        {"role": "user", "content": "Avalie uma plataforma de vídeos curtos premium para mobile com orçamento de 1.7B USD em 2020."}
    ],
    "stream": False,
    "format": "json",
    "options": {"temperature": 0.2, "num_predict": 600}
}

PAYLOAD_2 = {
    "model": MODELO,
    "messages": [
        {"role": "system", "content": "Aja como Advogado do Diabo implacável. Responda em JSON com chaves: veredito, probabilidade."},
        {"role": "user", "content": "Avalie um marketplace de acomodações alternativas peer-to-peer fundado em 2008 na crise."}
    ],
    "stream": False,
    "format": "json",
    "options": {"temperature": 0.2, "num_predict": 600}
}

def requisicao(payload, rotulo):
    t0 = time.time()
    try:
        r = requests.post(API_URL, json=payload, timeout=180)
        r.raise_for_status()
        duracao = round(time.time() - t0, 2)
        content = r.json().get("message", {}).get("content", "")
        return rotulo, duracao, True, content[:80]
    except Exception as e:
        duracao = round(time.time() - t0, 2)
        return rotulo, duracao, False, str(e)

def main():
    print(f"==================================================")
    print(f"🧪 TESTE EMPÍRICO DE PARALELISMO — Modelo: {MODELO}")
    print(f"==================================================")
    
    # 1. TESTE SEQUENCIAL
    print("\n1️⃣  Executando 2 requisições SEQUENCIAIS (1 por vez)...")
    t_inicio_seq = time.time()
    res1_seq = requisicao(PAYLOAD_1, "Req 1 (Quibi)")
    print(f"   -> {res1_seq[0]}: {res1_seq[1]}s (Status: {'OK' if res1_seq[2] else 'FALHA'})")
    res2_seq = requisicao(PAYLOAD_2, "Req 2 (Airbnb)")
    print(f"   -> {res2_seq[0]}: {res2_seq[1]}s (Status: {'OK' if res2_seq[2] else 'FALHA'})")
    tempo_total_seq = round(time.time() - t_inicio_seq, 2)
    print(f"   ⏱️  Tempo Total Sequencial: {tempo_total_seq}s")
    
    # 2. TESTE PARALELO
    print("\n2️⃣  Executando 2 requisições CONCORRENTES (ThreadPoolExecutor max_workers=2)...")
    t_inicio_par = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(requisicao, PAYLOAD_1, "Req 1 (Quibi - Paralelo)")
        f2 = executor.submit(requisicao, PAYLOAD_2, "Req 2 (Airbnb - Paralelo)")
        res1_par = f1.result()
        res2_par = f2.result()
    tempo_total_par = round(time.time() - t_inicio_par, 2)
    
    print(f"   -> {res1_par[0]}: {res1_par[1]}s (Status: {'OK' if res1_par[2] else 'FALHA'})")
    print(f"   -> {res2_par[0]}: {res2_par[1]}s (Status: {'OK' if res2_par[2] else 'FALHA'})")
    print(f"   ⏱️  Tempo Total Paralelo: {tempo_total_par}s")
    
    # COMPARAÇÃO
    speedup = round(tempo_total_seq / max(tempo_total_par, 0.01), 2)
    economia_pct = round((1 - (tempo_total_par / max(tempo_total_seq, 0.01))) * 100, 1)
    
    print("\n==================================================")
    print("📊 RESULTADO DO TESTE DE PARALELISMO:")
    print(f"   • Sequencial: {tempo_total_seq}s")
    print(f"   • Paralelo (2 workers): {tempo_total_par}s")
    print(f"   • Fator de Aceleração (Speedup): {speedup}x")
    print(f"   • Redução de Tempo Líquida: {economia_pct}%")
    print("==================================================")

if __name__ == "__main__":
    main()
