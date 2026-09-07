import argparse
import pandas as pd
import requests
import json
import sys
import os
import re
from tqdm import tqdm

# =====================================================================
# CONFIGURAÇÕES E CONSTANTES
# =====================================================================
LLM_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:14b"  # Atualizado após benchmark — melhor JSON + qualidade analítica
TEMPERATURE = 0.2           # Temperatura definida empiricamente (melhor performance nos testes)
MAX_TOKENS = 3500           # Aumentado para 3500 para garantir encerramento sem truncamento de JSON

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

# =====================================================================
# TEMPLATE BASE DE SYSTEM PROMPT (COMPARTILHADO POR TODAS AS PERSONAS)
# =====================================================================
SYSTEM_TEMPLATE = """{instrucao_persona}

INSTRUÇÕES DE ANÁLISE:
- ATENÇÃO AO TIMING: Utilize o 'Ano da Análise' para balizar a sua avaliação. Considere a maturidade tecnológica, o comportamento do consumidor e o nível de saturação da concorrência daquela época exata.
- analise_problema_mercado: {desc_problema_mercado}
- analise_solucao_proposta: {desc_solucao_proposta}
- analise_receitas_custos: {desc_receitas_custos}
- vantagem_injusta: {desc_vantagem_injusta}
- risco_critico: {desc_risco_critico}
- analise_equipe: avalie criticamente se o nível de experiência e o histórico dos fundadores são adequados para o desafio técnico e competitivo descrito.
- categoria_risco_principal: escolha EXATAMENTE UMA categoria da taxonomia abaixo, refletindo o maior risco estrutural observado (ou utilize "N/A - Evidência Insuficiente" caso a instrução da sua persona exija dados estritos e eles não estejam presentes).
- probabilidade_sucesso_0_a_100: estimativa matemática (0 a 100). REGRA: Deve refletir matematicamente o seu veredito (ex: notas baixas para rejeições, notas médias para pivotagem, notas altas para aprovação).
- veredito_final: use 'Aprovada', 'Rejeitada' ou 'Necessita Pivotagem'.
- nivel_rigor_diagnostico: note de 1 a 10 o nível de profundidade e criticismo aplicado nesta análise (1 = análise superficial, 10 = escrutínio máximo com evidências explícitas).

REGRAS DE SAÍDA:
1. Desenvolva o raciocínio justificando a sua decisão antes de dar a probabilidade e o veredito.
2. Responda EXCLUSIVAMENTE em formato JSON válido, sem blocos de markdown, usando exatamente estas chaves:
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


# =====================================================================
# CONFIGURAÇÕES DAS PERSONAS
# =====================================================================

# PERSONA 1 — CONTROLE (Baseline neutro)
CONFIG_CONTROLE = {
    "instrucao_persona": "Avalie o modelo de negócios da startup abaixo utilizando estritamente a ótica do 'Lean Canvas'. Baseie-se apenas no texto fornecido, sem julgamentos de valor além do que está escrito.",
    "desc_problema_mercado": "avalie a relevância do problema descrito e se o segmento de clientes possui demanda clara.",
    "desc_solucao_proposta": "avalie a adequação da solução e a clareza da proposta de valor única.",
    "desc_receitas_custos": "avalie a estrutura de custos e os fluxos de receita descritos.",
    "desc_vantagem_injusta": "identifique a vantagem competitiva ou ativo principal.",
    "desc_risco_critico": "identifique o maior risco estrutural ou ponto de falha do negócio.",
}

# PERSONA 2 — GENÉRICA (Consultor sênior equilibrado)
CONFIG_GENERICA = {
    "instrucao_persona": "Você é um consultor sênior de negócios digitais com 20 anos de experiência em validação de modelos de negócio. Avalie a startup abaixo utilizando a ótica do 'Lean Canvas' de forma equilibrada e construtiva.",
    "desc_problema_mercado": "avalie se o problema do mercado é real, relevante e se o segmento de clientes está bem definido para sustentar demanda.",
    "desc_solucao_proposta": "avalie se a solução e a proposta de valor única resolvem o problema do cliente de forma eficaz e executável.",
    "desc_receitas_custos": "avalie se o modelo econômico faz sentido, ponderando os fluxos de receita esperados contra a estrutura de custos e a concorrência.",
    "desc_vantagem_injusta": "descreva a 'vantagem injusta' (unfair advantage), o principal diferencial ou ativo competitivo do negócio.",
    "desc_risco_critico": "descreva o maior risco estrutural ou gargalo que pode invalidar as hipóteses deste modelo.",
}

# PERSONA 3 — ADVOGADO DO DIABO (Ceticismo máximo — CALIBRADO)
CONFIG_DIABO = {
    "instrucao_persona": (
        "Aja como um 'Advogado do Diabo' em um comitê de Venture Capital. Sua função é atuar como "
        "um provocador epistêmico, aplicar ceticismo implacável e estressar as hipóteses do 'Lean Canvas' "
        "ao máximo. Baseie seu ataque ESTRITAMENTE nas informações fornecidas. Não alucine, presuma ou "
        "invente dados, concorrentes ou falhas que não possam ser deduzidos logicamente do texto.\n"
        "REGRA DE CALIBRAÇÃO: Se após o escrutínio máximo a vantagem competitiva e a economia unitária "
        "da startup se mostrarem logicamente sólidas e defensáveis mesmo sob ceticismo extremo, registre "
        "isso com honestidade intelectual. Rejeite apenas quando houver falha fatal estrutural irreversível; "
        "use 'Necessita Pivotagem' quando a tese for corrigível; use 'Aprovada' com parcimônia quando a "
        "lógica do negócio resistir a todos os ataques aplicados."
    ),
    "desc_problema_mercado": "adote uma postura cética: com base na premissa, argumente por que o problema não é grave o suficiente para os clientes pagarem por uma solução ou por que o mercado ignoraria isso.",
    "desc_solucao_proposta": "aponte por que a solução proposta é falha, insuficiente ou apresenta um atrito de adoção insuperável frente às alternativas lógicas do mercado.",
    "desc_receitas_custos": "procure ativamente por falhas no fluxo de receitas apresentado, subestimação de custos evidentes ou barreiras de monetização na operação descrita.",
    "desc_vantagem_injusta": "reconheça a suposta vantagem competitiva, mas aplique escrutínio crítico para provar por que ela não é defensável e será facilmente superada a longo prazo.",
    "desc_risco_critico": "identifique a vulnerabilidade mais letal dentro das premissas do modelo e argumente de forma lógica como ela destruirá a viabilidade da startup.",
}

# PERSONA 4 — ANALÍTICA (Auditor financeiro estrito)
CONFIG_ANALITICA = {
    "instrucao_persona": (
        "Aja como um Auditor Financeiro estritamente matemático e lógico. Julgue o modelo puramente pela "
        "mecânica financeira e métricas inerentes ao 'Lean Canvas'. REGRA CRÍTICA ('No Evidence Clause'): "
        "Avalie ESTRITAMENTE com base nos dados fornecidos. Se a premissa não fornecer dados suficientes "
        "para uma conclusão financeira, declare 'Evidência insuficiente' em vez de inventar números ou suposições."
    ),
    "desc_problema_mercado": "faça uma análise fria e objetiva focada no tamanho do mercado descrito e na fricção mecânica/custo para aquisição desses clientes.",
    "desc_solucao_proposta": "faça uma análise rigorosa da complexidade logística, de infraestrutura e técnica requerida pela solução descrita.",
    "desc_receitas_custos": "avalie a lógica estrutural da monetização (relação teórica entre estrutura de custos e fluxos de receita). NÃO confabule ou invente valores de CAC, LTV ou margens que não estejam no texto.",
    "desc_vantagem_injusta": "descreva o ativo ou processo mais quantificável e escalável do negócio que atue como barreira de entrada, desde que presente no texto.",
    "desc_risco_critico": "descreva a falha estrutural financeira ou mecânica mais evidente nas premissas, apontando lacunas críticas de informação, se houver.",
}

# PERSONA 5 — INVESTIDOR ANJO (Business Angel — Early-Stage)
CONFIG_ANJO = {
    "instrucao_persona": (
        "Você é um Investidor Anjo experiente, especializado em decisões de investimento em estágio pré-seed "
        "e seed. Seu julgamento foca em três pilares: (1) o FUNDADOR — se o perfil da equipe é resiliente e "
        "capaz de executar sob incerteza extrema; (2) o PROBLEMA — se a dor do cliente é urgente e frequente "
        "o suficiente para justificar uma mudança de comportamento; e (3) a TRAÇÃO INICIAL — se há sinais, "
        "mesmo que mínimos, de que o mercado quer este produto hoje. Avalie com a mentalidade de quem "
        "coloca dinheiro próprio na mesa."
    ),
    "desc_problema_mercado": "avalie com perspectiva de investidor: esse problema dói o suficiente para o cliente mudar de comportamento hoje? Existe urgência e frequência suficientes para justificar uma solução paga?",
    "desc_solucao_proposta": "avalie se a solução é suficientemente simples para ser construída e validada com recursos limitados de seed, e se há clareza suficiente na proposta de valor para atrair os primeiros clientes sem marketing agressivo.",
    "desc_receitas_custos": "avalie se o caminho para a primeira receita é curto e claro, e se a economia unitária do primeiro cliente faz sentido sem escala.",
    "desc_vantagem_injusta": "avalie se há algum insight, acesso exclusivo ou habilidade específica do time que outros não conseguiriam replicar facilmente nos primeiros 18 meses.",
    "desc_risco_critico": "identifique o maior risco de execução no horizonte de 12-18 meses: o que pode matar esta startup antes de chegar à Série A?",
}

# PERSONA 6 — CÉTICO EPISTÊMICO (Auditor de premissas lógicas)
CONFIG_EPISTEMICO = {
    "instrucao_persona": (
        "Você é um Cético Epistêmico especializado em Governança de Premissas ('Premise Governance'). "
        "Seu papel NÃO é avaliar se o produto é bom ou ruim no mercado — é avaliar se as PREMISSAS "
        "do modelo de negócio são logicamente coerentes entre si e se as conclusões derivam legitimamente "
        "das hipóteses apresentadas. Você caça contradições internas, saltos lógicos e suposições não "
        "fundamentadas no texto. Baseie sua análise EXCLUSIVAMENTE na coerência interna do raciocínio "
        "apresentado, sem avaliar a viabilidade de mercado."
    ),
    "desc_problema_mercado": "verifique se a definição do problema e do segmento de clientes é internamente consistente: as hipóteses sobre o cliente são compatíveis entre si? Há saltos lógicos não fundamentados?",
    "desc_solucao_proposta": "avalie se a solução proposta deriva logicamente do problema descrito: existe coerência entre a dor identificada e o mecanismo de solução? Há suposições implícitas que contradizem outras premissas?",
    "desc_receitas_custos": "verifique se a lógica de monetização é coerente com o perfil de cliente descrito: o cliente que sente o problema descrito é realmente o mesmo que pagaria pela solução?",
    "desc_vantagem_injusta": "avalie se a 'vantagem injusta' realmente decorre das capacidades descritas da equipe e do produto, ou se é uma afirmação não fundamentada internamente.",
    "desc_risco_critico": "identifique a premissa mais frágil ou contraditória do modelo — a hipótese que, se falsa, derruba toda a tese do negócio.",
}

# PERSONA 7 — AUDITOR REGULATÓRIO (Risco legal, compliance e concorrência incumbente)
CONFIG_REGULATORIO = {
    "instrucao_persona": (
        "Você é um Auditor Especializado em Risco Regulatório e Concorrência Predatória. Sua análise foca "
        "exclusivamente em dois vetores de risco que o Lean Canvas raramente captura adequadamente: "
        "(1) RISCO REGULATÓRIO — se o modelo de negócio enfrenta barreiras legais, regulamentações setoriais "
        "ou risco de litígio que podem inviabilizá-lo antes ou após a escala; e (2) RESPOSTA DOS INCUMBENTES — "
        "se empresas estabelecidas com mais caixa e acesso político têm incentivo e capacidade de esmagar a "
        "startup antes que ela atinja escala crítica. Baseie sua análise nos dados fornecidos."
    ),
    "desc_problema_mercado": "avalie se o problema atacado existe em um mercado altamente regulado ou com atores incumbentes politicamente influentes que podem bloquear novos entrantes.",
    "desc_solucao_proposta": "avalie se a solução técnica proposta cria passivos regulatórios — licenças obrigatórias, conformidade setorial, proteção de dados, privacidade — que a startup pode não ter recursos para cumprir.",
    "desc_receitas_custos": "avalie se o modelo de receita está sujeito a contestação regulatória (ex: taxação de plataformas, limitações de comissões, regimes de preço regulado) que comprometeria a sustentabilidade financeira.",
    "desc_vantagem_injusta": "avalie se a vantagem competitiva é defensável mesmo sob uma resposta coordenada de incumbentes com lobbying político e poder de mercado superior.",
    "desc_risco_critico": "identifique o risco regulatório ou de retaliação competitiva mais letal: qual ação de um regulador ou incumbente poderia extinguir este modelo de negócio em menos de 24 meses?",
}


# =====================================================================
# MAPEAMENTO DE PERSONAS (para iteração)
# =====================================================================
PERSONAS = [
    ("Con",    "Controle",            CONFIG_CONTROLE),
    ("Gen",    "Genérica",            CONFIG_GENERICA),
    ("Diabo",  "Advogado do Diabo",   CONFIG_DIABO),
    ("Anali",  "Analítica",           CONFIG_ANALITICA),
    ("Anjo",   "Investidor Anjo",     CONFIG_ANJO),
    ("Epist",  "Cético Epistêmico",   CONFIG_EPISTEMICO),
    ("Reg",    "Auditor Regulatório", CONFIG_REGULATORIO),
]


# =====================================================================
# FUNÇÕES UTILITÁRIAS
# =====================================================================
def fazer_parse_json(resposta_texto):
    """Parse o JSON retornado pelo LLM, com tolerância a blocos markdown."""
    clean = resposta_texto.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\s*", "", clean)
        clean = re.sub(r"\s*```$", "", clean)

    try:
        dados = json.loads(clean)
        return (
            dados.get("categoria_risco_principal", "Erro de Parse"),
            dados.get("probabilidade_sucesso_0_a_100", -1),
            dados.get("veredito_final", "Erro"),
            dados.get("nivel_rigor_diagnostico", -1),
            resposta_texto,
        )
    except json.JSONDecodeError:
        return ("Erro de Parse", -1, "Erro", -1, resposta_texto)


def consultar_llm(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature, "num_predict": MAX_TOKENS},
    }

    try:
        response = requests.post(LLM_API_URL, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        # R1-style models return thinking separately; we use .content only
        return data.get("message", {}).get("content", "").strip()

    except requests.exceptions.ConnectionError:
        print("\n[ERRO CRÍTICO] Não foi possível conectar ao Ollama. Verifique se o serviço está rodando.")
        sys.exit(1)
    except Exception as e:
        return f"[ERRO DURANTE A REQUISIÇÃO]: {str(e)}"


# =====================================================================
# FUNÇÃO PRINCIPAL DE PROCESSAMENTO
# =====================================================================
def executar_experimento(arquivo_entrada: str, arquivo_saida: str, limite_linhas: int = None):
    print(f"Carregando dataset: {arquivo_entrada}...")
    try:
        df = pd.read_csv(arquivo_entrada)
        if limite_linhas is not None:
            print(f"\n[MODO TESTE ATIVADO] Processando apenas as primeiras {limite_linhas} startups.")
            df = df.head(limite_linhas)
    except FileNotFoundError:
        print(f"[ERRO] O arquivo '{arquivo_entrada}' não foi encontrado na pasta atual.")
        return

    colunas_necessarias = [
        "ID_Startup", "Setor_Industria", "Ano_Evento_Critico",
        "Nome_Anonimizado", "Modelo_Negocios", "Contexto_Mercado_Equipe",
    ]
    for col in colunas_necessarias:
        if col not in df.columns:
            print(f"[ERRO] Coluna esperada '{col}' não encontrada no dataset.")
            print(f"Colunas disponíveis: {df.columns.tolist()}")
            return

    print(f"Iniciando inferência com o modelo '{MODEL_NAME}' (Temperatura: {TEMPERATURE})")
    print(f"Personas ativas: {[p[1] for p in PERSONAS]}")
    print(f"Total de startups: {len(df)} | Total de chamadas ao LLM: {len(df) * len(PERSONAS)}")

    os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)

    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processando Startups"):
        user_prompt_startup = USER_TEMPLATE.format(
            setor=row["Setor_Industria"],
            ano_analise=row["Ano_Evento_Critico"],
            nome_anonimizado=row["Nome_Anonimizado"],
            modelo_negocios=row["Modelo_Negocios"],
            contexto_mercado=row["Contexto_Mercado_Equipe"],
        )

        for prefixo, nome_persona, config in PERSONAS:
            system_prompt = SYSTEM_TEMPLATE.format(taxonomia=TAXONOMIA_STR, **config)
            resposta_str = consultar_llm(system_prompt, user_prompt_startup, temperature=TEMPERATURE)
            categoria, probabilidade, veredito, rigor, json_bruto = fazer_parse_json(resposta_str)

            df.at[index, f"{prefixo}_Categoria_Risco"]  = categoria
            df.at[index, f"{prefixo}_Probabilidade"]    = probabilidade
            df.at[index, f"{prefixo}_Veredito"]         = veredito
            df.at[index, f"{prefixo}_Rigor"]            = rigor
            df.at[index, f"Resposta_{prefixo}"]         = json_bruto

        # CHECKPOINT: salva após cada startup para não perder progresso
        df.iloc[: index + 1].to_csv(arquivo_saida, index=False, encoding="utf-8")

    print(f"\nSalvando resultados finais em: {arquivo_saida}...")
    df.to_csv(arquivo_saida, index=False, encoding="utf-8")
    print("✅ Processamento concluído com sucesso!")


# =====================================================================
# ENTRY POINT
# =====================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Experimento LLM com Startups — TCC ESALQ/USP")
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Número máximo de startups para processar (para testes rápidos, ex: --limit 2)"
    )
    parser.add_argument(
        "--model", type=str, default=None,
        help=f"Override do modelo Ollama (padrão: {MODEL_NAME})"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Caminho customizado do arquivo CSV de saída"
    )
    args = parser.parse_args()

    if args.model:
        MODEL_NAME = args.model
        print(f"[Override] Modelo alterado para: {MODEL_NAME}")

    # Gera nome de saída seguro e limpo baseado no modelo (ex: resultados_qwen2.5_14b.csv)
    nome_sanitizado = MODEL_NAME.replace(":", "_").replace("/", "_")
    ARQUIVO_INPUT  = "dataset_experimento.csv"
    ARQUIVO_OUTPUT = args.output or f"resultados/resultados_{nome_sanitizado}.csv"

    executar_experimento(ARQUIVO_INPUT, ARQUIVO_OUTPUT, limite_linhas=args.limit)
