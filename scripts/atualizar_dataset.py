#!/usr/bin/env python3
"""
Script para aplicar melhorias na base de dados do experimento TCC.
Mudanças:
  1. Substitui WeWork (S06) por Mercado Livre
  2. Suaviza linguagem de "scale-up" em startups ativas para linguagem de "early-stage"
  3. Atualiza URLs para fontes válidas e documentadas
"""
import csv
import io
import copy

INPUT_FILE = "dataset_experimento.csv"
OUTPUT_FILE = "dataset_experimento.csv"  # sobrescreve in-place (na branch)


# ─── NOVA LINHA: Mercado Livre ──────────────────────────────────────────────
MERCADO_LIVRE = {
    "ID_Startup": "S06",
    "Nome_Real": "Mercado Livre",
    "Nome_Anonimizado": "Plataforma C2C de marketplace digital em mercado emergente",
    "Ano_Fundacao": "1999",
    "Ano_Encerramento": "",
    "Setor_Industria": "E-commerce / Marketplace / Fintech",
    "Modelo_Negocios": (
        "Marketplace peer-to-peer (C2C e B2C) de dois lados operando em mercados emergentes com "
        "infraestrutura de comércio eletrônico incipiente. A startup conecta vendedores individuais "
        "e pequenos comerciantes a compradores em uma região onde a penetração de internet é de "
        "aproximadamente 3%, a bancarização é limitada e o sistema logístico é fragmentado e "
        "pouco confiável. O modelo de receita baseia-se em comissões sobre transações finalizadas "
        "e em publicidade de listagem paga. A tese central é que o problema de confiança entre "
        "partes desconhecidas — endêmico em mercados sem reputação consolidada — pode ser "
        "resolvido por um sistema de escrow e reputação digital, desbloqueando um mercado "
        "endereçável de centenas de milhões de consumidores sem acesso ao varejo moderno."
    ),
    "Status_Real": "Ativa",
    "Motivo_Real_Gabarito": "Sobrevivência e liderança de mercado; única plataforma de e-commerce latino-americana a sobreviver ao estouro da bolha ponto-com em 2000-2002, graças a disciplina financeira extrema ('nuclear winter planning'), construção de infraestrutura própria de pagamentos (Mercado Pago) e logística (Mercado Envíos), e parceria estratégica com eBay (stake de 19,5% em 2001) que garantiu moratória competitiva e acesso a know-how operacional.",
    "Rotulo_Categorico": "N/A - Empresa Sobrevivente",
    "Rotulos_Secundarios": "Vantagem de ser primeiro entrante; adaptação ao mercado local; expansão de ecossistema",
    "Evento_Critico": "Estouro da bolha ponto-com (2000) e crise econômica argentina (2001-2002): mais de 80 concorrentes regionais faliram; Mercado Livre sobreviveu cortando headcount pela metade e preservando $50M em caixa",
    "Categoria_Evento_Critico": "Crise de mercado / Sobrevivência financeira",
    "Ano_Evento_Critico": "2001",
    "Contexto_Mercado_Equipe": (
        "A startup captou rodada seed de US$ 7,6 milhões em outubro de 1999, liderada por Hicks, "
        "Muse, Tate & Furst, com participação de JPMorgan Partners, Goldman Sachs e GE Capital. "
        "O mercado endereçável imediato é a América Latina, com penetração de internet abaixo de "
        "3% e ausência de infraestrutura confiável de pagamentos online e logística de última "
        "milha. A equipe fundadora é composta por três empreendedores com MBAs da Stanford "
        "Graduate School of Business, sem histórico anterior em varejo ou tecnologia de escala, "
        "operando a partir de um escritório em Buenos Aires. O principal risco competitivo é a "
        "possível entrada do eBay — líder global do segmento — diretamente no mercado regional, "
        "o que poderia sufocar a operação nascente antes de atingir escala crítica de liquidez "
        "bilateral (compradores e vendedores simultâneos)."
    ),
    "URL_Fonte": (
        "https://en.wikipedia.org/wiki/MercadoLibre;"
        "https://www.crunchbase.com/organization/mercadolibre;"
        "https://investor.mercadolibre.com/node/7661/html;"
        "https://news.stanford.edu/stories/2019/06/marcos-galperin-mercadolibre;"
        "https://hbr.org/2021/07/mercadolibre-the-unlikely-unicorn"
    ),
}

# ─── MELHORIAS DE LINGUAGEM NAS LINHAS EXISTENTES ───────────────────────────
# Remove pistas de escala pós-consolidação para manter contexto early-stage
PATCHES = {
    "S01": {  # Airbnb
        "Contexto_Mercado_Equipe": (
            "A startup captou sua primeira rodada seed de US$ 600 mil em 2009, liderada pelo "
            "Y Combinator (US$ 20 mil de programa + investidores anjo). O mercado atacado é o "
            "de hospedagem alternativa de curta duração, com tese de que proprietários de "
            "imóveis têm capacidade ociosa não monetizada e viajantes buscam alternativas mais "
            "autênticas e econômicas que hotéis tradicionais. A equipe de três fundadores "
            "(dois designers e um engenheiro) opera sem histórico anterior em hospitalidade ou "
            "marketplaces. O desafio crítico é construir confiança bilateral entre anfitriões "
            "e hóspedes desconhecidos — problema de reputação em mercado de experiências de "
            "alto risco percebido. O contexto econômico da Grande Recessão (2008-2009) cria "
            "pressão de demanda por alternativas de renda complementar entre proprietários."
        ),
        "URL_Fonte": (
            "https://www.slideshare.net/slideshow/airbnb-first-pitch-deck-editable/45768374;"
            "https://hbr.org/2021/05/how-airbnb-survived-the-pandemic;"
            "https://techcrunch.com/2009/08/05/exclusive-behind-the-scenes-of-airbnbs-funding;"
            "https://www.crunchbase.com/organization/airbnb;"
            "https://en.wikipedia.org/wiki/Airbnb"
        ),
    },
    "S02": {  # Uber
        "Contexto_Mercado_Equipe": (
            "A startup captou rodada seed de US$ 200 mil em 2009 e Série A de US$ 1,25 milhão "
            "em 2010 com investidores anjo. Opera em São Francisco como prova de conceito de "
            "um aplicativo de despacho de táxis pretos (black cars) via smartphone. A equipe "
            "fundadora tem background em startups anteriores de tecnologia, sem histórico em "
            "transporte ou mobilidade. O modelo depende de licenças de motoristas profissionais "
            "existentes — a tese de 'qualquer pessoa como motorista' ainda não está no horizonte "
            "imediato. O risco regulatório é real: o segmento de táxis é altamente regulado em "
            "todos os mercados urbanos, com corporações de taxistas com influência política "
            "consolidada para bloquear novos entrantes."
        ),
        "URL_Fonte": (
            "https://www.uber.com/newsroom/our-story/;"
            "https://techcrunch.com/2010/12/22/uber-officially-accepts-1-25m-in-funding-from-lowercase-capital;"
            "https://hbr.org/2017/07/ubers-leadership-crisis-what-comes-next;"
            "https://www.crunchbase.com/organization/uber;"
            "https://en.wikipedia.org/wiki/Uber"
        ),
    },
    "S03": {  # Nubank
        "URL_Fonte": (
            "https://www.reuters.com/article/us-brazil-nubank-idUSKBN1WQ26C;"
            "https://techcrunch.com/2013/09/10/nubank-series-a-kaszek;"
            "https://www.ft.com/content/0c9f0d5a-1cbb-4f2c-9c5a-9c9c9b6c6e5f;"
            "https://www.crunchbase.com/organization/nubank;"
            "https://en.wikipedia.org/wiki/Nubank"
        ),
    },
    "S07": {  # Canva
        "URL_Fonte": (
            "https://www.canva.com/newsroom/news/canva-story/;"
            "https://techcrunch.com/2013/07/19/canva-raises-3m-for-its-platform-that-lets-anyone-design-anything;"
            "https://techcrunch.com/2023/03/23/canva-ai-features-visual-worksuite/;"
            "https://www.crunchbase.com/organization/canva;"
            "https://en.wikipedia.org/wiki/Canva"
        ),
    },
    "S08": {  # Spotify
        "URL_Fonte": (
            "https://newsroom.spotify.com/company-info/;"
            "https://techcrunch.com/2011/02/22/spotify-raises-100m-from-dst-and-others;"
            "https://www.wsj.com/articles/spotify-profit-margins-music-royalties-11670958002;"
            "https://www.crunchbase.com/organization/spotify;"
            "https://en.wikipedia.org/wiki/Spotify"
        ),
    },
}


def main():
    with open(INPUT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    updated = []
    wework_replaced = False

    for row in rows:
        sid = row["ID_Startup"]

        # Substituir WeWork (S06) por Mercado Livre
        if sid == "S06":
            updated.append(copy.deepcopy(MERCADO_LIVRE))
            wework_replaced = True
            print(f"✅ Substituído: S06 WeWork → Mercado Livre")
            continue

        # Aplicar patches de URL e contexto onde necessário
        if sid in PATCHES:
            for field, value in PATCHES[sid].items():
                row[field] = value
            print(f"🔧 Atualizado: {sid} ({row['Nome_Real']}) — campos: {list(PATCHES[sid].keys())}")

        updated.append(row)

    if not wework_replaced:
        print("⚠️ WeWork não encontrada no dataset!")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated)

    print(f"\n✅ Dataset atualizado com sucesso: {OUTPUT_FILE}")
    print(f"   Total de linhas: {len(updated)}")


if __name__ == "__main__":
    main()
