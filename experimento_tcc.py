import argparse
import pandas as pd
import requests
import json
import sys
import os
from tqdm import tqdm

# =====================================================================
# CONFIGURAÇÕES E CONSTANTES
# =====================================================================
LLM_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3"
TEMPERATURE = 0.2
MAX_TOKENS = 800

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

SYSTEM_TEMPLATE = """{instrucao_persona}

INSTRUÇÕES DE ANÁLISE:
- ATENÇÃO AO TIMING: Utilize o 'Ano da Análise' para balizar a sua avaliação. Considere a maturidade tecnológica, o comportamento do consumidor e o nível de saturação da concorrência daquela época exata.
- analise_problema_mercado: {desc_problema_mercado}
- analise_solucao_proposta: {desc_solucao_proposta}
- analise_receitas_custos: {desc_receitas_custos}
- vantagem_injusta: {desc_vantagem_injusta}
- risco_critico: {desc_risco_critico}
- analise_equipe: "avalie criticamente se o nível de experiência e o histórico dos fundadores são adequados para o desafio técnico e competitivo descrito."
- categoria_risco_principal: escolha EXATAMENTE UMA categoria da taxonomia abaixo, refletindo o maior risco estrutural observado (ou utilize "N/A - Evidência Insuficiente" caso a instrução da sua persona exija dados estritos e eles não estejam presentes).
- probabilidade_sucesso_0_a_100: estimativa matemática (0 a 100). REGRA: Deve refletir matematicamente o seu veredito (ex: notas baixas para rejeições, notas médias para pivotagem, notas altas para aprovação).
- veredito_final: use 'Aprovada', 'Rejeitada' ou 'Necessita Pivotagem'.

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
  "veredito_final": ""
}}

CLASSIFICAÇÃO PERMITIDA PARA categoria_risco_principal:
{taxonomia}"""

USER_TEMPLATE = """DADOS DA STARTUP:
Setor: {setor}
Ano da Análise: {ano_analise}
Proposta: {nome_anonimizado}
Modelo de Negócios (Premissa): {modelo_negocios}
Estrutura da Equipe e Cenário de Mercado: {contexto_mercado}"""


# 2. CONFIGURAÇÕES DAS PERSONAS (Ajustadas para a nova estrutura)
CONFIG_CONTROLE = {
    "instrucao_persona": "Avalie o modelo de negócios da startup abaixo utilizando estritamente a ótica do 'Lean Canvas'. Baseie-se apenas no texto fornecido.",
    "desc_problema_mercado": "avalie a relevância do problema descrito e se o segmento de clientes possui demanda clara.",
    "desc_solucao_proposta": "avalie a adequação da solução e a clareza da proposta de valor única.",
    "desc_receitas_custos": "avalie a estrutura de custos e os fluxos de receita descritos.",
    "desc_vantagem_injusta": "identifique a vantagem competitiva ou ativo principal.",
    "desc_risco_critico": "identifique o maior risco estrutural ou ponto de falha do negócio.",
}

CONFIG_GENERICA = {
    "instrucao_persona": "Você é um consultor sênior de negócios digitais. Avalie o modelo de negócios da startup abaixo utilizando estritamente a ótica do 'Lean Canvas'.",
    "desc_problema_mercado": "avalie se o problema do mercado é real, relevante e se o segmento de clientes está bem definido para sustentar demanda.",
    "desc_solucao_proposta": "avalie se a solução e a proposta de valor única resolvem o problema do cliente de forma eficaz e executável.",
    "desc_receitas_custos": "avalie se o modelo econômico faz sentido, ponderando os fluxos de receita esperados contra a estrutura de custos e a concorrência.",
    "desc_vantagem_injusta": "descreva a 'vantagem injusta' (unfair advantage), o principal diferencial ou ativo competitivo do negócio.",
    "desc_risco_critico": "descreva o maior risco estrutural ou gargalo que pode invalidar as hipóteses deste modelo.",
}

CONFIG_DIABO = {
    "instrucao_persona": "Aja como um 'Advogado do Diabo' em um comitê de Venture Capital. Sua função é atuar como um provocador epistêmico, aplicar ceticismo implacável e estressar as hipóteses do 'Lean Canvas' ao máximo. Baseie seu ataque ESTRITAMENTE nas informações fornecidas. Não alucine, presuma ou invente dados, concorrentes ou falhas que não possam ser deduzidos logicamente do texto.",
    "desc_problema_mercado": "adote uma postura cética: com base na premissa, argumente por que o problema não é grave o suficiente para os clientes pagarem por uma solução ou por que o mercado ignoraria isso.",
    "desc_solucao_proposta": "aponte por que a solução proposta é falha, insuficiente ou apresenta um atrito de adoção insuperável frente às alternativas lógicas do mercado.",
    "desc_receitas_custos": "procure ativamente por falhas no fluxo de receitas apresentado, subestimação de custos evidentes ou barreiras de monetização na operação descrita.",
    "desc_vantagem_injusta": "reconheça a suposta vantagem competitiva, mas aplique escrutínio crítico para provar por que ela não é defensável e será facilmente superada a longo prazo.",
    "desc_risco_critico": "identifique a vulnerabilidade mais letal dentro das premissas do modelo e argumente de forma lógica como ela destruirá a viabilidade da startup.",
}

CONFIG_ANALITICA = {
    "instrucao_persona": "Aja como um Auditor Financeiro estritamente matemático e lógico. Julgue o modelo puramente pela mecânica financeira e métricas inerentes ao 'Lean Canvas'. REGRA CRÍTICA ('No Evidence Clause'): Avalie ESTRITAMENTE com base nos dados fornecidos. Se a premissa não fornecer dados suficientes para uma conclusão financeira, declare 'Evidência insuficiente' em vez de inventar números ou suposições.",
    "desc_problema_mercado": "faça uma análise fria e objetiva focada no tamanho do mercado descrito e na fricção mecânica/custo para aquisição desses clientes.",
    "desc_solucao_proposta": "faça uma análise rigorosa da complexidade logística, de infraestrutura e técnica requerida pela solução descrita.",
    "desc_receitas_custos": "avalie a lógica estrutural da monetização (relação teórica entre estrutura de custos e fluxos de receita). NÃO confabule ou invente valores de CAC, LTV ou margens que não estejam no texto.",
    "desc_vantagem_injusta": "descreva o ativo ou processo mais quantificável e escalável do negócio que atue como barreira de entrada, desde que presente no texto.",
    "desc_risco_critico": "descreva a falha estrutural financeira ou mecânica mais evidente nas premissas, apontando lacunas críticas de informação, se houver.",
}


def fazer_parse_json(resposta_texto):
    try:
        # Tenta converter a string que veio do LLM num dicionário Python
        dados = json.loads(resposta_texto)
        return (
            dados.get("categoria_risco_principal", "Erro de Parse"),
            dados.get("probabilidade_sucesso_0_a_100", -1),
            dados.get("veredito_final", "Erro"),
            resposta_texto,  # Salva o JSON bruto por segurança
        )
    except json.JSONDecodeError:
        return ("Erro de Parse", -1, "Erro", resposta_texto)


def consultar_llm(
    system_prompt: str, user_prompt: str, temperature: float = 0.0
) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature, "num_predict": MAX_TOKENS},
    }

    try:
        response = requests.post(LLM_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "").strip()

    except requests.exceptions.ConnectionError:
        print("\n[ERRO CRÍTICO] Não foi possível conectar ao LLM.")
        sys.exit(1)
    except Exception as e:
        return f"[ERRO DURANTE A REQUISIÇÃO]: {str(e)}"


# =====================================================================
# FUNÇÃO PRINCIPAL DE PROCESSAMENTO
# =====================================================================
def executar_experimento(
    arquivo_entrada: str, arquivo_saida: str, limite_linhas: int = None
):
    print(f"Carregando dataset: {arquivo_entrada}...")
    try:
        df = pd.read_csv(arquivo_entrada)

        if limite_linhas is not None:
            print(
                f"\n[MODO TESTE ATIVADO] Processando apenas as primeiras {limite_linhas} startups."
            )
            df = df.head(limite_linhas)
    except FileNotFoundError:
        print(
            f"[ERRO] O arquivo '{arquivo_entrada}' não foi encontrado na pasta atual."
        )
        return

    colunas_necessarias = [
        "ID_Startup",
        "Setor_Industria",
        "Ano_Evento_Critico",
        "Nome_Anonimizado",
        "Modelo_Negocios",
        "Contexto_Mercado_Equipe",
    ]
    for col in colunas_necessarias:
        if col not in df.columns:
            print(f"[ERRO] Coluna esperada '{col}' não encontrada no dataset.")
            print(f"Colunas disponíveis: {df.columns.tolist()}")
            return

    print(
        f"Iniciando inferência com o modelo {MODEL_NAME} (Temperatura: {TEMPERATURE})"
    )
    print(f"Total de startups a processar: {len(df)}")

    # Cria diretório de saída caso não exista
    os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)

    for index, row in tqdm(df.iterrows(), total=len(df), desc="A processar Startups"):
        setor = row["Setor_Industria"]
        ano_analise = row["Ano_Evento_Critico"]
        nome_anonimizado = row["Nome_Anonimizado"]
        modelo_negocios = row["Modelo_Negocios"]
        contexto_mercado = row["Contexto_Mercado_Equipe"]
        user_prompt_startup = USER_TEMPLATE.format(
            setor=setor,
            ano_analise=ano_analise,
            nome_anonimizado=nome_anonimizado,
            modelo_negocios=modelo_negocios,
            contexto_mercado=contexto_mercado,
        )

        # 1. Prompt Controle
        system_controle = SYSTEM_TEMPLATE.format(
            taxonomia=TAXONOMIA_STR, **CONFIG_CONTROLE
        )

        resp_controle_str = consultar_llm(
            system_controle, user_prompt_startup, temperature=TEMPERATURE
        )
        cat_con, prob_con, veredit_con, json_con = fazer_parse_json(resp_controle_str)

        # Adicione aos DataFrames parciais
        df.at[index, "Con_Categoria_Risco"] = cat_con
        df.at[index, "Con_Probabilidade"] = prob_con
        df.at[index, "Con_Veredito"] = veredit_con
        df.at[index, "Resposta_Controle"] = json_con

        # 2. Prompt Genérico
        system_generico = SYSTEM_TEMPLATE.format(
            taxonomia=TAXONOMIA_STR, **CONFIG_GENERICA
        )

        resp_generico_str = consultar_llm(
            system_generico, user_prompt_startup, temperature=TEMPERATURE
        )
        cat_gen, prob_gen, veredito_gen, json_gen = fazer_parse_json(resp_generico_str)

        # Adicione aos DataFrames parciais
        df.at[index, "Gen_Categoria_Risco"] = cat_gen
        df.at[index, "Gen_Probabilidade"] = prob_gen
        df.at[index, "Gen_Veredito"] = veredito_gen
        df.at[index, "Resposta_Generica"] = json_gen

        # 3. Prompt Advogado do Diabo
        system_diabo = SYSTEM_TEMPLATE.format(taxonomia=TAXONOMIA_STR, **CONFIG_DIABO)
        resp_diabo_str = consultar_llm(
            system_diabo, user_prompt_startup, temperature=TEMPERATURE
        )
        cat_diabo, prob_diabo, veredito_diabo, json_diabo = fazer_parse_json(
            resp_diabo_str
        )

        df.at[index, "Diabo_Categoria_Risco"] = cat_diabo
        df.at[index, "Diabo_Probabilidade"] = prob_diabo
        df.at[index, "Diabo_Veredito"] = veredito_diabo
        df.at[index, "Resposta_Advogado_Diabo"] = json_diabo

        # 4. Prompt Analítico
        system_analitico = SYSTEM_TEMPLATE.format(
            taxonomia=TAXONOMIA_STR, **CONFIG_ANALITICA
        )
        resp_analitico_str = consultar_llm(
            system_analitico, user_prompt_startup, temperature=TEMPERATURE
        )
        cat_anali, prob_anali, veredito_anali, json_anali = fazer_parse_json(
            resp_analitico_str
        )

        df.at[index, "Anali_Categoria_Risco"] = cat_anali
        df.at[index, "Anali_Probabilidade"] = prob_anali
        df.at[index, "Anali_Veredito"] = veredito_anali
        df.at[index, "Resposta_Analitica"] = json_anali

        # SALVAMENTO PARCIAL (CHECKPOINT)
        df_parcial = df.iloc[: index + 1].copy()
        df_parcial.to_csv(arquivo_saida, index=False, encoding="utf-8")

    print(f"\nSalvando resultados finais em: {arquivo_saida}...")
    df.to_csv(arquivo_saida, index=False, encoding="utf-8")
    print("Processamento concluído com sucesso!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script para experimento LLM com Startups."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Número máximo de startups para processar (para testes rápidos)",
    )
    args = parser.parse_args()

    ARQUIVO_INPUT = "dataset_experimento.csv"
    ARQUIVO_OUTPUT = "resultados/resultados_experimento_21.2.csv"

    executar_experimento(ARQUIVO_INPUT, ARQUIVO_OUTPUT, limite_linhas=args.limit)
