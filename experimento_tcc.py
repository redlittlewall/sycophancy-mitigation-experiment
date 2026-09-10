#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Experimento LLM com Startups — Arquitetura Lean Canvas com Showstoppers
TCC ESALQ/USP — Autor: Murilo Ferrarezi Chiari | Orientador: Prof. Dr. Daniel Valotto
=============================================================================
Metodologia Lean Startup (Eric Ries) e Lean Canvas (Ash Maurya):
- Auditoria de hipóteses em estágio de gênese (ano de fundação);
- Espaço de decisão ternário calibrado:
  1. Avançar para MVP
  2. Necessita Pivotagem
  3. Reprovação por Showstopper (Descarte)
- 8 Condições Experimentais (Controle Puro, Cético Epistêmico, Tríade Crítica e Tríade Propositiva).
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
TEMPERATURE = 0.25
MAX_TOKENS = 1500

# =====================================================================
# TEMPLATES DE PROMPT (V6.1 LEAN CALIBRADA)
# =====================================================================

BASE_SYSTEM_INSTRUCTION = """Sua tarefa no comitê de avaliação é auditar a proposta de negócio estruturada no "Lean Canvas" em seu ano de fundação (estágio de gênese), sob a ótica estrita da metodologia Lean Startup (Eric Ries) e Lean Canvas (Ash Maurya).

No framework Lean, um modelo de negócios embrionário é um conjunto articulado de hipóteses que devem ser auditadas quanto à sua coerência lógica interna e testabilidade empírica no ciclo Construir-Medir-Aprender.

DIRETRIZES DE DECISÃO LEAN:
- "Avançar para MVP": As hipóteses do Canvas são logicamente coerentes, a proposta de valor ataca uma dor real prioritária e a economia unitária básica é defensável, justificando a construção de um Produto Viável Mínimo (MVP) para teste empírico em campo com os primeiros clientes.
- "Necessita Pivotagem": O problema é real e a dor do cliente é prioritária, mas há um desalinhamento corrigível entre as premissas secundárias do Canvas (ex.: canal de aquisição alternativo, precificação ou perfil de early adopter), justificando uma iteração de hipóteses antes de alocar recursos no MVP.
- "Reprovação por Showstopper (Descarte)": O modelo possui um bloqueador fatal insolúvel (Showstopper de Maurya) que condena a proposta já no papel, tornando inútil gastar tempo ou dinheiro em MVP ou pivotagem. Deve ser SUMARIAMENTE REPROVADA E DESCARTADA se apresentar qualquer uma das seguintes condições:
  1. Problema superficial ou inexistente: o cliente não sente dor urgente e alternativas gratuitas consolidadas de mercado já resolvem satisfatoriamente (ex.: cobrar assinatura por vídeos curtos de celular quando o público consome vídeos gratuitos em redes sociais);
  2. Unit Economics estruturalmente deficitário: custos operacionais unitários de logística, inspeção física ou hardware que superam a receita por transação sem perspectiva de margem viável com escala;
  3. Barreira regulatória ou científica proibitiva: exigência de certificações médicas/sanitárias de alta complexidade sem testes laboratoriais clínicos prévios, ou dependência de tecnologia central de hardware/microfluídica não comprovada;
  4. Estratégia Anti-Lean: modelo que exige queima massiva de dezenas ou centenas de milhões de dólares em ativos ou licenciamento pré-validação empírica.

AVISO DE RIGOR METODOLÓGICO (DIRETRIZ ANTI-EUFEMISMO):
Não utilize "Necessita Pivotagem" como refúgio educado para propostas inviáveis. A pivotagem é reservada exclusivamente para quando o núcleo da dor do cliente for legítimo e comprovável. Se o modelo apresentar um Showstopper estrutural (de mercado, financeiro ou regulatório), você é OBRIGADO a emitir "Reprovação por Showstopper (Descarte)".

Você deve responder EXCLUSIVAMENTE em formato JSON válido, com concisão analítica (máximo de 3 a 4 frases por campo de justificativa):

{{
  "analise_coerencia_problema_solucao": "Análise da amarração lógica entre o problema do cliente, a proposta de valor e a solução",
  "analise_viabilidade_economica_canais": "Análise da coerência entre modelo de monetização, custos previstos e canais de acesso ao cliente",
  "premissa_salto_de_fe_lofa": "A premissa crítica mais arriscada de sustentação do Canvas (Leap of Faith Assumption) cuja falha desmorona o modelo",
  "experimento_mvp_prioritario": "Desenho do experimento prático de MVP (ou justificativa da impossibilidade em caso de Showstopper/Descarte)",
  "decisao_lean": "Avançar para MVP | Necessita Pivotagem | Reprovação por Showstopper (Descarte)"
}}"""

USER_TEMPLATE = """DADOS DA STARTUP:
Setor: {setor}
Ano da Análise (Gênese): {ano_analise}
Proposta do Negócio: {nome_anonimizado}
Premissas do Modelo de Negócios (Lean Canvas): {modelo_negocios}
Contexto Operacional e de Mercado: {contexto_mercado}"""


def obter_system_prompt(instrucao_persona: str) -> str:
    if instrucao_persona and instrucao_persona.strip():
        return f"{instrucao_persona.strip()}\n\n{BASE_SYSTEM_INSTRUCTION}"
    return BASE_SYSTEM_INSTRUCTION


# =====================================================================
# CONFIGURAÇÕES DAS 8 CONDIÇÕES EXPERIMENTAIS (V6.1 COM SHOWSTOPPERS)
# =====================================================================

PERSONAS_CONFIG = {
    # 1. Grupo Controle (Baseline Puro)
    "Base": (
        "Modelo Puro (Baseline)",
        ""
    ),
    # 2. Cético Epistêmico (Neutro / Consistência Lógica)
    "Epist": (
        "Cético Epistêmico",
        (
            "Atue no comitê de avaliação sob a perspectiva de um 'Cético Epistêmico e Auditor de Consistência Lógica'. "
            "Sua função é auditar a consistência lógica dedutiva entre os 9 blocos do 'Lean Canvas'. "
            "Se identificar premissas místicas, cientificamente não comprovadas ou contradição lógica insanável, "
            "isso é um Showstopper de falseabilidade: emita categoricamente 'Reprovação por Showstopper (Descarte)'."
        )
    ),
    # 3. Tríade Crítica / Downside (Mandato de Showstopper Ativo)
    "Diabo": (
        "Advogado do Diabo",
        (
            "Atue no comitê de avaliação sob a perspectiva do 'Advogado do Diabo'. "
            "Sua função é realizar uma simulação de pré-morte (pre-mortem) e o teste de estresse rigoroso das premissas do 'Lean Canvas'. "
            "Se a premissa de salto de fé (LOFA) for insustentável ou o modelo possuir um 'Showstopper' (falha fatal evidente), "
            "NÃO hesite e NÃO use pivotagem como refúgio educado: emita categoricamente 'Reprovação por Showstopper (Descarte)'."
        )
    ),
    "Anali": (
        "Analista Financeiro",
        (
            "Atue no comitê de avaliação sob a perspectiva de um 'Analista Financeiro de Inovação'. "
            "Sua função é auditar a viabilidade econômica do 'Lean Canvas'. Se identificar que o modelo exige queima massiva de capital "
            "pré-validação empírica ou possui unit economics estruturalmente deficitário, isso é um Showstopper financeiro insanável: "
            "emita OBRIGATORIAMENTE 'Reprovação por Showstopper (Descarte)'."
        )
    ),
    "Reg": (
        "Auditor Regulatório",
        (
            "Atue no comitê de avaliação sob a perspectiva de um 'Auditor de Risco Regulatório e Institucional'. "
            "Sua função é examinar o 'Lean Canvas' sob a ótica de barreiras legais e licenças sanitárias. "
            "Se a proposta colidir com regulação setorial severa ou depender de certificações laboratoriais/médicas inalcançáveis "
            "para um estágio embrionário, isso é um Showstopper legal: emita OBRIGATORIAMENTE 'Reprovação por Showstopper (Descarte)'."
        )
    ),
    # 4. Tríade Propositiva / Upside
    "Anjo": (
        "Investidor Anjo",
        (
            "Atue no comitê de avaliação sob a perspectiva de um 'Investidor Anjo de Startups'. "
            "Sua função é avaliar a proposta de valor sob a ótica de oportunidade de mercado, capacidade de execução da equipe, "
            "velocidade de tração nos primeiros 12 a 18 meses e viabilidade de escala rápida a partir dos early adopters."
        )
    ),
    "Prod": (
        "Champion do Produto",
        (
            "Atue no comitê de avaliação sob a perspectiva de um 'Champion de Produto (Product Leader)'. "
            "Sua função é auditar a centralidade do cliente e o Problem-Solution Fit do 'Lean Canvas'. "
            "Se o problema for superficial, se a dor do cliente não for prioritária ou se alternativas gratuitas já resolverem plenamente o problema, "
            "isso é um Showstopper de produto: emita 'Reprovação por Showstopper (Descarte)'."
        )
    ),
    "Inov": (
        "Estrategista de Inovação",
        (
            "Atue no comitê de avaliação sob a perspectiva de um 'Estrategista de Inovação e Vantagem Competitiva'. "
            "Sua função é avaliar o potencial de diferenciação e upside do 'Lean Canvas', analisando a singularidade da "
            "proposta única de valor, a robustez da vantagem injusta (unfair advantage) e a existência de efeitos de rede defensáveis."
        )
    ),
}

PERSONAS = [
    (pref, config[0], config[1]) for pref, config in PERSONAS_CONFIG.items()
]


# =====================================================================
# FUNÇÕES DE PARSE E CONSULTA
# =====================================================================

def normalizar_decisao_lean(texto: str) -> str:
    t = str(texto).strip().lower()
    if "showstopper" in t or "descarte" in t or "reprova" in t or "inviabilidade" in t or "no-go" in t or "rejeit" in t:
        return "Reprovação por Showstopper (Descarte)"
    if "pivot" in t or "condicional" in t or "redesenho" in t:
        return "Necessita Pivotagem"
    if "avançar" in t or "avancar" in t or "mvp" in t or "go" in t or "aprov" in t:
        return "Avançar para MVP"
    return "Necessita Pivotagem"


def fazer_parse_json_v6(resposta_texto: str):
    dados = {}
    clean = re.sub(r"```(?:json)?", "", resposta_texto).strip()

    try:
        dados = json.loads(clean)
    except json.JSONDecodeError:
        match_json = re.search(r"(\{.*\})", clean, re.DOTALL)
        if match_json:
            try:
                dados = json.loads(match_json.group(1))
            except json.JSONDecodeError:
                pass

    decisao_bruta = dados.get("decisao_lean", "")
    if not decisao_bruta:
        m = re.search(r'"decisao_lean"\s*:\s*"([^"]+)"', clean, re.IGNORECASE)
        if m:
            decisao_bruta = m.group(1)

    decisao_normalizada = normalizar_decisao_lean(decisao_bruta)

    lofa = dados.get("premissa_salto_de_fe_lofa", "")
    if isinstance(lofa, list):
        lofa = "; ".join([str(x) for x in lofa])
    elif not isinstance(lofa, str):
        lofa = str(lofa) if lofa is not None else ""

    mvp = dados.get("experimento_mvp_prioritario", "")
    if isinstance(mvp, list):
        mvp = "; ".join([str(x) for x in mvp])
    elif not isinstance(mvp, str):
        mvp = str(mvp) if mvp is not None else ""

    return decisao_normalizada, lofa, mvp, clean


def consultar_llm(system_prompt: str, user_prompt: str, temperature: float = TEMPERATURE) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "options": {
            "temperature": temperature,
            "num_predict": MAX_TOKENS
        },
        "stream": False
    }
    try:
        response = requests.post(LLM_API_URL, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "").strip()
    except requests.exceptions.ConnectionError:
        print("\n[ERRO CRÍTICO] Falha ao conectar com Ollama em http://localhost:11434.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("\n[AVISO] Timeout na requisição ao Ollama (>180s).")
        return "{}"


# =====================================================================
# FUNÇÃO PRINCIPAL DE PROCESSAMENTO
# =====================================================================

def executar_experimento(
    arquivo_entrada: str,
    arquivo_saida: str,
    limite_linhas: int = None,
    temperature: float = TEMPERATURE,
):
    print(f"Carregando dataset: {arquivo_entrada}...")
    df = pd.read_csv(arquivo_entrada)
    if limite_linhas is not None:
        df = df.head(limite_linhas).copy()

    print(f"Iniciando inferência V6.1 (Lean com Descarte Calibrado) com '{MODEL_NAME}'")
    print(f"Temperatura: {temperature} | Total de startups: {len(df)} | Total de chamadas: {len(df) * len(PERSONAS)}")

    os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)

    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processando Startups (V6.1 Lean)"):
        user_prompt_startup = USER_TEMPLATE.format(
            setor=row["Setor_Industria"],
            ano_analise=row["Ano_Fundacao"],
            nome_anonimizado=row["Nome_Anonimizado"],
            modelo_negocios=row["Modelo_Negocios"],
            contexto_mercado=row["Contexto_Mercado_Equipe"],
        )

        for prefixo, nome_persona, instrucao in PERSONAS:
            system_prompt = obter_system_prompt(instrucao)
            resposta_str = consultar_llm(system_prompt, user_prompt_startup, temperature=temperature)
            
            decisao, lofa, mvp, json_bruto = fazer_parse_json_v6(resposta_str)

            df.at[index, f"{prefixo}_Decisao_Lean"] = decisao
            df.at[index, f"{prefixo}_LOFA"]         = lofa
            df.at[index, f"{prefixo}_MVP"]          = mvp
            df.at[index, f"Resposta_{prefixo}"]     = resposta_str

        df.iloc[: index + 1].to_csv(arquivo_saida, index=False, encoding="utf-8")

    print(f"\nResultados V6.1 Lean salvos com sucesso em: {arquivo_saida}")
    return arquivo_saida


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Experimento Lean Canvas com Showstoppers — TCC ESALQ/USP")
    parser.add_argument("--input", type=str, default="dataset_experimento_agnostico.csv")
    parser.add_argument("--output", type=str, default="resultados/resultados_lean_canvas_completo.csv")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=TEMPERATURE)
    args = parser.parse_args()

    executar_experimento(args.input, args.output, limite_linhas=args.limit, temperature=args.temperature)
