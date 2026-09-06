import time
import json
import requests
import pandas as pd
import sys

LLM_API_URL = "http://localhost:11434/api/chat"
STARTUP_TESTE_CSV = "dataset_experimento.csv"

TAXONOMIA_CATEGORIAS = [
    "Sem necessidade de mercado",
    "Fim do caixa",
    "Equipe inadequada",
    "Concorrência predatória",
    "Problema de preço ou custo",
    "Produto ruim",
    "Modelo de negócios falho",
    "Problema regulatório ou legal",
    "Marketing ineficaz",
    "N/A - Evidência Insuficiente",
]
TAXONOMIA_STR = ", ".join(TAXONOMIA_CATEGORIAS)

SYSTEM_TEMPLATE_DIABO = """Aja como um 'Advogado do Diabo' em um comitê de Venture Capital. Sua função é atuar como um provocador epistêmico, aplicar ceticismo implacável e estressar as hipóteses do 'Lean Canvas' ao máximo. Baseie seu ataque ESTRITAMENTE nas informações fornecidas. Não alucine, presuma ou invente dados, concorrentes ou falhas que não possam ser deduzidos logicamente do texto.

INSTRUÇÕES DE ANÁLISE:
- ATENÇÃO AO TIMING: Utilize o 'Ano da Análise' para balizar a sua avaliação. Considere a maturidade tecnológica, o comportamento do consumidor e o nível de saturação da concorrência daquela época exata.
- analise_problema_mercado: adote uma postura cética: com base na premissa, argumente por que o problema não é grave o suficiente para os clientes pagarem por uma solução ou por que o mercado ignoraria isso.
- analise_solucao_proposta: aponte por que a solução proposta é falha, insuficiente ou apresenta um atrito de adoção insuperável frente às alternativas lógicas do mercado.
- analise_receitas_custos: procure ativamente por falhas no fluxo de receitas apresentado, subestimação de custos evidentes ou barreiras de monetização na operação descrita.
- vantagem_injusta: reconheça a suposta vantagem competitiva, mas aplique escrutínio crítico para provar por que ela não é defensável e será facilmente superada a longo prazo.
- risco_critico: identifique a vulnerabilidade mais letal dentro das premissas do modelo e argumente de forma lógica como ela destruirá a viabilidade da startup.
- analise_equipe: avalie criticamente se o nível de experiência e o histórico dos fundadores são adequados para o desafio técnico e competitivo descrito.
- categoria_risco_principal: escolha EXATAMENTE UMA categoria da taxonomia abaixo, refletindo o maior risco estrutural observado (ou utilize "N/A - Evidência Insuficiente").
- probabilidade_sucesso_0_a_100: estimativa matemática (0 a 100). REGRA: Deve refletir matematicamente o seu veredito (ex: notas baixas para rejeições, notas médias para pivotagem, notas altas para aprovação).
- veredito_final: use 'Aprovada', 'Rejeitada' ou 'Necessita Pivotagem'.
- nivel_rigor_diagnostico: atribua uma nota de 1 a 10 indicando o nível de criticismo e profundidade do teste de estresse aplicado.

REGRAS DE SAÍDA:
1. Desenvolva o raciocínio justificando a sua decisão antes de dar a probabilidade e o veredito.
2. Responda EXCLUSIVAMENTE em formato JSON válido, usando exatamente estas chaves:
{{
  "analise_problema_mercado": "",
  "analise_solucao_proposta": "",
  "analise_receitas_custos": "",
  "vantagem_injusta": "",
  "risco_critico": "",
  "analise_equipe": "",
  "categoria_risco_principal": "",
  "probabilidade_sucesso_0_a_100": 0,
  "veredito_final": "",
  "nivel_rigor_diagnostico": 0
}}

CLASSIFICAÇÃO PERMITIDA PARA categoria_risco_principal:
{taxonomia}"""

USER_TEMPLATE = """DADOS DA STARTUP:
Setor: {setor}
Ano da Análise: {ano_analise}
Proposta: {nome_anonimizado}
Modelo de Negócios (Premissa): {modelo_negocios}
Estrutura da Equipe e Cenário de Mercado: {contexto_mercado}"""


def testar_modelo(model_name: str, startup_id: str = "F01", temperature: float = 0.2):
    df = pd.read_csv(STARTUP_TESTE_CSV)
    row = df[df["ID_Startup"] == startup_id].iloc[0]

    user_prompt = USER_TEMPLATE.format(
        setor=row["Setor_Industria"],
        ano_analise=row["Ano_Evento_Critico"],
        nome_anonimizado=row["Nome_Anonimizado"],
        modelo_negocios=row["Modelo_Negocios"],
        contexto_mercado=row["Contexto_Mercado_Equipe"],
    )
    system_prompt = SYSTEM_TEMPLATE_DIABO.format(taxonomia=TAXONOMIA_STR)

    print(f"\n" + "="*70)
    print(f"🚀 INICIANDO BENCHMARK: Modelo '{model_name}'")
    print(f"Startup: {row['Nome_Real']} ({startup_id}) | Persona: Advogado do Diabo | Temp: {temperature}")
    print("="*70)

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": temperature,
            "num_predict": 2500
        },
    }

    t0 = time.time()
    try:
        response = requests.post(LLM_API_URL, json=payload, timeout=300)
        response.raise_for_status()
        t1 = time.time()
        elapsed = t1 - t0
        data = response.json()
    except Exception as e:
        print(f"❌ Erro na requisição para {model_name}: {e}")
        return None

    msg_obj = data.get("message", {})
    content = msg_obj.get("content", "").strip()
    thinking = msg_obj.get("thinking", "")
    eval_count = data.get("eval_count", 0)
    eval_duration_ns = data.get("eval_duration", 1)
    tok_per_sec = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else 0

    # Parse JSON (com limpeza de markdown codeblocks se necessário)
    clean_content = content.strip()
    if clean_content.startswith("```"):
        import re
        clean_content = re.sub(r"^```(?:json)?\s*", "", clean_content)
        clean_content = re.sub(r"\s*```$", "", clean_content)

    try:
        parsed = json.loads(clean_content)
        json_valido = True
        veredito = parsed.get("veredito_final", "N/A")
        prob = parsed.get("probabilidade_sucesso_0_a_100", "N/A")
        risco = parsed.get("categoria_risco_principal", "N/A")
        rigor = parsed.get("nivel_rigor_diagnostico", "N/A")
    except Exception as e:
        json_valido = False
        veredito = "ERRO_JSON"
        prob = -1
        risco = "ERRO_JSON"
        rigor = -1

    # Estimativa para o experimento completo (20 startups x 4 ou 7 personas)
    estimativa_4_personas_min = (elapsed * 20 * 4) / 60
    estimativa_7_personas_min = (elapsed * 20 * 7) / 60

    print(f"⏱️  Tempo total de resposta: {elapsed:.2f} segundos")
    print(f"⚡ Tokens gerados: {eval_count} ({tok_per_sec:.1f} tokens/segundo)")
    print(f"📋 JSON válido: {'✅ Sim' if json_valido else '❌ Não'}")
    print(f"⚖️  Veredito: {veredito} | Prob: {prob}% | Risco: {risco} | Rigor: {rigor}")
    if json_valido and isinstance(parsed, dict):
        print(f"\n💬 Amostra da Crítica Qualitativa:")
        print(f"   • Risco Crítico: {parsed.get('risco_critico', '')[:200]}...")
        print(f"   • Problema/Mercado: {parsed.get('analise_problema_mercado', '')[:200]}...")
    print(f"\n⏳ Projeção 20 startups x 4 personas: {estimativa_4_personas_min:.1f} minutos (~{estimativa_4_personas_min/60:.1f}h)")
    print(f"⏳ Projeção 20 startups x 7 personas: {estimativa_7_personas_min:.1f} minutos (~{estimativa_7_personas_min/60:.1f}h)")
    print("="*70)

    return {
        "modelo": model_name,
        "tempo_segundos": round(elapsed, 2),
        "tokens_gerados": eval_count,
        "tokens_por_segundo": round(tok_per_sec, 1),
        "json_valido": json_valido,
        "veredito": veredito,
        "probabilidade": prob,
        "risco_detectado": risco,
        "projecao_4_personas_min": round(estimativa_4_personas_min, 1),
        "projecao_7_personas_min": round(estimativa_7_personas_min, 1),
    }


if __name__ == "__main__":
    modelo = sys.argv[1] if len(sys.argv) > 1 else "llama3"
    startup = sys.argv[2] if len(sys.argv) > 2 else "F01"
    testar_modelo(modelo, startup)
