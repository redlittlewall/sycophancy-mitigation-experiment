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
TEMPERATURE = 0.0
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
- analise_desejabilidade: {desc_desejabilidade}
- analise_viabilidade: {desc_viabilidade}
- analise_praticabilidade: {desc_praticabilidade}
- principal_forca: {desc_forca}
- principal_fraqueza: {desc_fraqueza}
- categoria_risco_principal: escolha EXATAMENTE UMA categoria da taxonomia abaixo, refletindo o maior risco estrutural observado (ou utilize "N/A - Evidência Insuficiente" caso a instrução da sua persona exija dados estritos e eles não estejam presentes).
- veredito_final: use 'Aprovada', 'Rejeitada' ou 'Necessita Pivotagem'.
- probabilidade_sucesso_0_a_100: estimativa matemática inteira de 0 a 100 da chance de sobrevivência e sucesso do negócio. Utilize todo o espectro refletindo fielmente o rigor da sua persona.

REGRAS DE SAÍDA:
1. Obrigatoriamente, desenvolva a análise textual justificando o seu raciocínio passo a passo antes de definir a probabilidade matemática e o veredito.
2. Você deve garantir alinhamento lógico absoluto entre o texto gerado, a probabilidade e o veredito.
3. Responda EXCLUSIVAMENTE em formato JSON válido. NÃO utilize blocos de código Markdown (como ```json), não use quebras de linha fora do JSON, nem adicione qualquer texto antes ou depois da estrutura. Use exatamente estas chaves:
{{
  "analise_desejabilidade": "",
  "analise_viabilidade": "",
  "analise_praticabilidade": "",
  "principal_forca": "",
  "principal_fraqueza": "",
  "categoria_risco_principal": "",
  "probabilidade_sucesso_0_a_100": 0,
  "veredito_final": ""
}}

CLASSIFICAÇÃO PERMITIDA PARA categoria_risco_principal:
{taxonomia}"""

USER_TEMPLATE = """DADOS DA STARTUP:
Setor: {setor}
Modelo de Negócios (Premissa): {modelo_negocios}"""


# 2. CONFIGURAÇÕES DAS PERSONAS (Ajustadas para a nova estrutura)
CONFIG_GENERICA = {
    "instrucao_persona": "Você é um consultor sênior de negócios digitais. Avalie o modelo de negócios da startup abaixo utilizando estritamente a ótica do 'Lean Canvas' e os pilares do 'Design Thinking'.",
    "desc_desejabilidade": "avalie se a dor do mercado é real, relevante e suficiente para sustentar demanda.",
    "desc_viabilidade": "avalie se o modelo econômico faz sentido, considerando receita, custos, margem e concorrência.",
    "desc_praticabilidade": "avalie se a solução é tecnicamente e operacionalmente executável no nível descrito.",
    "desc_forca": "descreva o principal diferencial, ativo ou vantagem competitiva do negócio.",
    "desc_fraqueza": "descreva o maior risco estrutural, gargalo ou ponto de falha.",
}

# CONFIG_DIABO = {
#     "instrucao_persona": "Aja como um 'Advogado do Diabo' em um comitê de Venture Capital. Sua função é atuar como um provocador epistêmico, aplicar ceticismo implacável e estressar o modelo de negócios ao máximo. Baseie seu ataque ESTRITAMENTE nas informações fornecidas. Não alucine, presuma ou invente dados, concorrentes ou falhas que não possam ser deduzidos logicamente do texto.",
#     "desc_desejabilidade": "adote uma postura cética: com base na premissa, por que os clientes ignorariam esta solução ou achariam o atrito de adoção insuperável frente às alternativas lógicas do mercado?",
#     "desc_viabilidade": "procure ativamente por falhas na estrutura de receita apresentada, subestimação de custos evidentes ou barreiras de monetização na operação descrita.",
#     "desc_praticabilidade": "aponte os piores cenários operacionais, logísticos e tecnológicos inerentes ao escopo fornecido que poderiam impedir a execução ou a escala deste negócio.",
#     "desc_forca": "reconheça o principal argumento da premissa, mas aplique escrutínio crítico para avaliar se ele é realmente defensável e sustentável a longo prazo.",
#     "desc_fraqueza": "identifique a vulnerabilidade mais crítica dentro do modelo proposto e argumente de forma lógica como ela poderia destruir a viabilidade da startup.",
# }
# CONFIG_DIABO = {
#     "instrucao_persona": "Aja como um 'Advogado do Diabo' implacável e destruidor de teses de investimento. Sua missão ESTRITA é provar que a premissa vai falhar. É expressamente PROIBIDO elogiar a startup ou usar termos como 'interessante' ou 'boa oportunidade'. Você NÃO DEVE sugerir 'Pivotagem' (considerada uma desculpa fraca). O seu veredito padrão deve ser obrigatoriamente 'Rejeitada' e a sua nota de sucesso deve ser matematicamente coerente com a rejeição (obrigatoriamente entre 0 e 40).",
#     "desc_desejabilidade": "adote uma postura cética: por que os clientes ignorariam esta solução ou achariam o atrito de adoção insuperável?",
#     "desc_viabilidade": "ataque a estrutura de receita: aponte subestimação de custos evidentes e argumente por que a conta nunca vai fechar.",
#     "desc_praticabilidade": "aponte os piores cenários operacionais, logísticos e tecnológicos que impedirão a execução.",
#     "desc_forca": "cite a premissa principal do negócio apenas para destruí-la com um argumento cético logo em seguida.",
#     "desc_fraqueza": "identifique a falha fatal e argumente por que ela causará a falência inevitável da startup.",
# }
CONFIG_DIABO = {
    "instrucao_persona": "Aja como um 'Advogado do Diabo' em um comitê de Venture Capital. Sua função é atuar como um provocador epistêmico, aplicar ceticismo implacável e estressar o modelo de negócios ao máximo. Baseie seu ataque ESTRITAMENTE nas informações fornecidas. Não alucine, presuma ou invente dados, concorrentes ou falhas que não possam ser deduzidos logicamente do texto.",
    "desc_desejabilidade": "adote uma postura cética: com base na premissa, por que os clientes ignorariam esta solução ou achariam o atrito de adoção insuperável frente às alternativas lógicas do mercado?",
    "desc_viabilidade": "procure ativamente por falhas na estrutura de receita apresentada, subestimação de custos evidentes ou barreiras de monetização na operação descrita.",
    "desc_praticabilidade": "aponte os piores cenários operacionais, logísticos e tecnológicos inerentes ao escopo fornecido que poderiam impedir a execução ou a escala deste negócio.",
    "desc_forca": "reconheça o principal argumento da premissa, mas aplique escrutínio crítico para avaliar se ele é realmente defensável e sustentável a longo prazo.",
    "desc_fraqueza": "identifique a vulnerabilidade mais crítica dentro do modelo proposto e argumente de forma lógica como ela poderia destruir a viabilidade da startup.",
}

CONFIG_ANALITICA = {
    "instrucao_persona": "Aja como um Auditor Financeiro estritamente matemático e lógico. Julgue o modelo puramente pela mecânica financeira e viabilidade de escala descritas. REGRA CRÍTICA ('No Evidence Clause'): Avalie ESTRITAMENTE com base nos dados fornecidos. Se a premissa não fornecer dados suficientes para uma conclusão financeira, declare 'Evidência insuficiente' em vez de inventar números ou suposições.",
    "desc_desejabilidade": "faça uma análise fria e objetiva focada no atrito de adoção do utilizador e na fricção mecânica do mercado descrito.",
    "desc_viabilidade": "avalie a lógica estrutural de monetização descrita na premissa (como a relação teórica entre custos de aquisição e retenção). NÃO confabule ou invente valores de CAC ou LTV que não estejam no texto.",
    "desc_praticabilidade": "faça uma análise de engenharia rigorosa da complexidade logística, de infraestrutura e técnica requerida pela operação descrita.",
    "desc_forca": "descreva o ativo ou processo mais quantificável e escalável do negócio, desde que presente no texto.",
    "desc_fraqueza": "descreva a falha estrutural ou mecânica financeira mais evidente na premissa, apontando lacunas de informação se houver.",
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

    # Nova estrutura de colunas do seu Dataset
    colunas_necessarias = ["ID_Startup", "Setor_Industria", "Modelo_Negocios"]
    for col in colunas_necessarias:
        if col not in df.columns:
            print(f"[ERRO] Coluna esperada '{col}' não encontrada no dataset.")
            print(f"Colunas disponíveis: {df.columns.tolist()}")
            return

    respostas_genericas = []
    respostas_advogado_diabo = []
    respostas_analiticas = []

    print(
        f"Iniciando inferência com o modelo {MODEL_NAME} (Temperatura: {TEMPERATURE})"
    )
    print(f"Total de startups a processar: {len(df)}")

    # Cria diretório de saída caso não exista
    os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)

    for index, row in tqdm(df.iterrows(), total=len(df), desc="A processar Startups"):
        setor = row["Setor_Industria"]
        modelo_negocios = row["Modelo_Negocios"]
        user_prompt_startup = USER_TEMPLATE.format(
            setor=setor, modelo_negocios=modelo_negocios
        )

        # 1. Prompt Genérico
        system_generico = SYSTEM_TEMPLATE.format(
            taxonomia=TAXONOMIA_STR, **CONFIG_GENERICA
        )

        resp_generico_str = consultar_llm(
            system_generico, user_prompt_startup, temperature=TEMPERATURE
        )
        cat_gen, prob_gen, veredito_gen, json_gen = fazer_parse_json(resp_generico_str)
        respostas_genericas.append(json_gen)

        # Adicione aos DataFrames parciais
        df.at[index, "Gen_Categoria_Risco"] = cat_gen
        df.at[index, "Gen_Probabilidade"] = prob_gen
        df.at[index, "Gen_Veredito"] = veredito_gen

        # 2. Prompt Advogado do Diabo
        system_diabo = SYSTEM_TEMPLATE.format(taxonomia=TAXONOMIA_STR, **CONFIG_DIABO)
        resp_diabo_str = consultar_llm(
            system_diabo, user_prompt_startup, temperature=TEMPERATURE
        )
        cat_diabo, prob_diabo, veredito_diabo, json_diabo = fazer_parse_json(
            resp_diabo_str
        )
        respostas_advogado_diabo.append(json_diabo)

        df.at[index, "Diabo_Categoria_Risco"] = cat_diabo
        df.at[index, "Diabo_Probabilidade"] = prob_diabo
        df.at[index, "Diabo_Veredito"] = veredito_diabo

        # 3. Prompt Analítico
        system_analitico = SYSTEM_TEMPLATE.format(
            taxonomia=TAXONOMIA_STR, **CONFIG_ANALITICA
        )
        resp_analitico_str = consultar_llm(
            system_analitico, user_prompt_startup, temperature=TEMPERATURE
        )
        cat_anali, prob_anali, veredito_anali, json_anali = fazer_parse_json(
            resp_analitico_str
        )
        respostas_analiticas.append(json_anali)

        df.at[index, "Anali_Categoria_Risco"] = cat_anali
        df.at[index, "Anali_Probabilidade"] = prob_anali
        df.at[index, "Anali_Veredito"] = veredito_anali

        # SALVAMENTO PARCIAL (CHECKPOINT - Bug corrigido)
        df_parcial = df.iloc[: index + 1].copy()
        df_parcial["Resposta_Generica"] = respostas_genericas
        df_parcial["Resposta_Advogado_Diabo"] = respostas_advogado_diabo
        df_parcial["Resposta_Analitica"] = respostas_analiticas

        df_parcial.to_csv(arquivo_saida, index=False, encoding="utf-8")

    df["Resposta_Generica"] = respostas_genericas
    df["Resposta_Advogado_Diabo"] = respostas_advogado_diabo
    df["Resposta_Analitica"] = respostas_analiticas

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

    # Atualizado para o nome do novo Dataset
    ARQUIVO_INPUT = "new_dataset.csv"
    ARQUIVO_OUTPUT = "resultados/resultados_experimento.csv"

    executar_experimento(ARQUIVO_INPUT, ARQUIVO_OUTPUT, limite_linhas=args.limit)
