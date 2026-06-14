import pandas as pd
import json
import re

# =====================================================================
# 1. FUNÇÕES AUXILIARES E CARREGAMENTO
# =====================================================================
df = pd.read_csv("resultados/resultados_experimento_21.2.csv")

prompts = ["Con", "Gen", "Anali", "Adv"]

colunas_resposta_csv = {
    "Con": "Resposta_Controle",
    "Gen": "Resposta_Generica",
    "Anali": "Resposta_Analitica",
    "Adv": "Resposta_Advogado_Diabo",
}

p_nomes_bonitos = {
    "Con": "Controle (Baseline)",
    "Gen": "Genérico",
    "Anali": "Analítico",
    "Adv": "Advogado do Diabo",
}


def extrair_campo_json(texto_celula, campo_alvo):
    if pd.isna(texto_celula):
        return "Não registrado."
    texto_str = str(texto_celula).strip()
    try:
        dados = json.loads(texto_str)
        if campo_alvo in dados:
            val = dados[campo_alvo]
            if isinstance(val, dict) and len(val) > 0:
                primeira_chave = list(val.keys())[0]
                return str(
                    val[primeira_chave][0]
                    if isinstance(val[primeira_chave], list)
                    else val[primeira_chave]
                )
            return str(val)
    except:
        pass

    padrao = r'"' + re.escape(campo_alvo) + r'"\s*:\s*(.*?)(?=\s*,\s*"|\s*\}\s*$)'
    match = re.search(padrao, texto_str, re.DOTALL)
    if match:
        conteudo = match.group(1).strip()
        if conteudo.startswith("{"):
            sub_match = re.search(r'":\s*\[?\s*"(.*?)"', conteudo)
            if sub_match:
                return sub_match.group(1)
        return (
            conteudo.strip('"')
            .strip("]")
            .strip("[")
            .strip('"')
            .replace("\\n", " ")
            .replace('\\"', '"')
        )

    return "Não identificado."


# =====================================================================
# 2. PROCESSAMENTO: VISÃO MATRICIAL (Startups em Linhas, Personas em Colunas)
# =====================================================================
linhas_html = ""
dados_modais_js = {}

stats_persona = {
    p: {
        "total": 0,
        "aprovadas": 0,
        "reprovadas": 0,
        "acertos_veredito": 0,
        "acertos_primarios": 0,
        "acertos_secundarios": 0,
        "erros_diagnostico": 0,
    }
    for p in prompts
}

for idx, row in df.iterrows():
    startup_id = str(row["ID_Startup"])
    nome_startup = str(row["Nome_Real"])
    setor = str(row["Setor_Industria"])
    status_real = str(row["Status_Real"]).upper()

    real_sucesso = 1 if status_real in ["ATIVA", "SUCESSO"] else 0

    if status_real == "FALHA":
        tag_principal_real = str(row["Rotulo_Categorico"])
        motivo_real = str(row["Motivo_Real_Gabarito"])
    else:
        tag_principal_real = str(row["Categoria_Evento_Critico"])
        motivo_real = str(row["Evento_Critico"])

    rotulos_secundarios = str(row.get("Rotulos_Secundarios", ""))

    tags_validas = [tag_principal_real.strip().lower()]
    if rotulos_secundarios and rotulos_secundarios.lower() not in ["nan", "none", ""]:
        secundarias = [
            t.strip().lower() for t in rotulos_secundarios.split(";") if t.strip()
        ]
        tags_validas.extend(secundarias)

    tag_badge_class = "badge-fail" if status_real == "FALHA" else "badge-success"

    tags_gabarito_html = (
        f'<span class="badge {tag_badge_class}">{tag_principal_real}</span>'
    )
    if rotulos_secundarios and rotulos_secundarios.lower() not in ["nan", "none", ""]:
        for tag_sec in rotulos_secundarios.split(";"):
            if tag_sec.strip():
                tags_gabarito_html += f' <span class="badge {tag_badge_class}" style="opacity: 0.8; border-style: dashed;" title="Causa Secundária">{tag_sec.strip()}</span>'

    premissa_input = str(row["Modelo_Negocios"])
    detalhes_prompts_html = ""

    # Inicia a linha da tabela com os dados da startup
    style_gabarito = (
        "background-color: #fadbd8; color: #78281f; font-weight: bold;"
        if status_real == "FALHA"
        else "background-color: #d4efdf; color: #145a32; font-weight: bold;"
    )

    linha_atual = f"""
    <tr onclick="abrirModal('{startup_id}')" class="clickable-row">
        <td><b>{startup_id}</b></td>
        <td>
            <div style="font-weight: bold; color: #2c3e50; margin-bottom: 3px;">{nome_startup}</div>
            <div style="font-size: 11px; color: #7f8c8d;">{setor}</div>
        </td>
        <td style="{style_gabarito} text-align: center; vertical-align: middle;">{status_real}</td>
    """

    # Processa as 4 personas para criar as 4 colunas na mesma linha
    for p in prompts:
        col_resp = colunas_resposta_csv[p]
        if pd.isna(row.get(col_resp)):
            linha_atual += "<td><span style='color: #ccc;'>N/A</span></td>"
            continue

        stats_persona[p]["total"] += 1

        tag_risco_ia = extrair_campo_json(row[col_resp], "categoria_risco_principal")
        texto_desejabilidade = extrair_campo_json(
            row[col_resp], "analise_problema_mercado"
        )
        texto_viabilidade = extrair_campo_json(row[col_resp], "analise_receitas_custos")
        texto_praticabilidade = extrair_campo_json(
            row[col_resp], "analise_solucao_proposta"
        )
        texto_forca = extrair_campo_json(row[col_resp], "vantagem_injusta")
        texto_fraqueza = extrair_campo_json(row[col_resp], "risco_critico")
        texto_veredito = extrair_campo_json(row[col_resp], "veredito_final").lower()

        # KPIs e Semáforos
        ia_aprovou = 1 if "aprovada" in texto_veredito else 0
        if ia_aprovou:
            stats_persona[p]["aprovadas"] += 1
        else:
            stats_persona[p]["reprovadas"] += 1

        if ia_aprovou == real_sucesso:
            stats_persona[p]["acertos_veredito"] += 1

        tag_risco_ia_lower = tag_risco_ia.strip().lower()
        if tag_risco_ia_lower == tag_principal_real.strip().lower():
            cor_tag_ia = (
                "background-color: #1e8449; color: white; border: 1px solid #145a32;"
            )
            icone_acerto = "🎯"
            stats_persona[p]["acertos_primarios"] += 1
        elif tag_risco_ia_lower in tags_validas:
            cor_tag_ia = (
                "background-color: #2ecc71; color: white; border: 1px dashed #145a32;"
            )
            icone_acerto = "✔️"
            stats_persona[p]["acertos_secundarios"] += 1
        else:
            cor_tag_ia = (
                "background-color: #e74c3c; color: white; border: 1px solid #922b21;"
            )
            icone_acerto = "❌"
            stats_persona[p]["erros_diagnostico"] += 1

        # Veredito Estilizado
        if "rejeitada" in texto_veredito:
            cor_veredito = "#c0392b"
            bg_veredito = "#f2d7d5"
            txt_veredito = "REJ"
        elif "pivotagem" in texto_veredito or "condições" in texto_veredito:
            cor_veredito = "#b9770e"
            bg_veredito = "#fdebd0"
            txt_veredito = "PIVOT"
        else:
            cor_veredito = "#196f3d"
            bg_veredito = "#d4efdf"
            txt_veredito = "APR"

        # Probabilidade
        val_prob = extrair_campo_json(row[col_resp], "probabilidade_sucesso_0_a_100")
        try:
            prob = int(float(val_prob))
            prob_str = f"{prob}%"
            alpha = max(0.1, min(1.0, prob / 100.0))
            cor_prob_bg = f"rgba(46, 204, 113, {alpha})"
        except:
            prob_str = "N/A"
            cor_prob_bg = "#eee"

        # Monta a célula da coluna da Persona
        celula_persona = f"""
        <td style="vertical-align: top;">
            <div style="margin-bottom: 5px;">
                <span class="badge" style="{cor_tag_ia} font-size: 10px; display: block; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{tag_risco_ia.upper()}">
                    {icone_acerto} {tag_risco_ia.upper()}
                </span>
            </div>
            <div style="display: flex; gap: 5px;">
                <span style="flex: 1; text-align: center; font-size: 10px; font-weight: bold; background-color: {bg_veredito}; color: {cor_veredito}; border-radius: 4px; padding: 3px;">{txt_veredito}</span>
                <span style="flex: 1; text-align: center; font-size: 10px; font-weight: bold; background-color: {cor_prob_bg}; border-radius: 4px; padding: 3px; color: #111; border: 1px solid #bdc3c7;">{prob_str}</span>
            </div>
        </td>
        """
        linha_atual += celula_persona

        # Monta o card interno do Modal (mantém igual)
        detalhes_prompts_html += f"""
        <div class="prompt-card">
            <div class="prompt-header">
                <h4>🧠 Persona: {p_nomes_bonitos[p]}</h4>
                <div class="prompt-badges">
                    <span style="background-color: {bg_veredito}; color: {cor_veredito}; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{txt_veredito}</span>
                    <span style="background-color: {cor_prob_bg}; padding: 4px 8px; border-radius: 4px; font-size: 11px; border: 1px solid #bdc3c7; font-weight: bold; color:#111;">CHANCE: {prob_str}</span>
                </div>
            </div>
            <p><b>Diagnóstico da IA:</b> <span class="badge" style="{cor_tag_ia} font-size:12px;">{icone_acerto} {tag_risco_ia.upper()}</span></p>
            <div class="analysis-grid">
                <div class="analysis-col"><p><b>Mercado:</b> {texto_desejabilidade}</p></div>
                <div class="analysis-col"><p><b>Solução:</b> {texto_praticabilidade}</p></div>
                <div class="analysis-col"><p><b>Economia:</b> {texto_viabilidade}</p></div>
            </div>
            <div class="swot-box">
                <p>🚀 <b>Vantagem Injusta:</b> {texto_forca}</p>
                <p>⚠️ <b>Risco Crítico:</b> {texto_fraqueza}</p>
            </div>
        </div>
        """

    linha_atual += "</tr>"
    linhas_html += linha_atual

    dados_modais_js[startup_id] = {
        "nome": nome_startup,
        "setor": setor,
        "status": status_real,
        "tags_gabarito_html": tags_gabarito_html,
        "motivo": motivo_real,
        "premissa": premissa_input,
        "detalhes_ia": detalhes_prompts_html,
    }

# =====================================================================
# 3. GERAÇÃO DO GRID DE ESTATÍSTICAS HTML
# =====================================================================
html_cards_stats = ""
for p in prompts:
    s = stats_persona[p]
    tot = max(1, s["total"])
    acuracia_perc = (s["acertos_veredito"] / tot) * 100

    html_cards_stats += f"""
    <div class="persona-card">
        <h3>{p_nomes_bonitos[p]}</h3>
        <div class="stat-line"><span>Aprovadas:</span> <span class="stat-value" style="color: #27ae60;">{s["aprovadas"]}</span></div>
        <div class="stat-line"><span>Rejeitadas/Pivot:</span> <span class="stat-value" style="color: #c0392b;">{s["reprovadas"]}</span></div>
        <div class="stat-line" style="margin-top: 8px; border-top: 2px solid #ecf0f1; padding-top: 5px;">
            <span>Acurácia (Veredito):</span> <span class="stat-value" style="color: #2980b9;">{s["acertos_veredito"]}/{tot} ({acuracia_perc:.1f}%)</span>
        </div>
        <div class="stat-line" style="margin-top: 8px; border-top: 2px solid #ecf0f1; padding-top: 5px;">
            <span>🎯 Causa Principal:</span> <span class="stat-value">{s["acertos_primarios"]}</span>
        </div>
        <div class="stat-line"><span>✔️ Causa Secundária:</span> <span class="stat-value">{s["acertos_secundarios"]}</span></div>
        <div class="stat-line"><span>❌ Divergências:</span> <span class="stat-value">{s["erros_diagnostico"]}</span></div>
    </div>
    """

js_dict_str = json.dumps(dados_modais_js, ensure_ascii=False)

# =====================================================================
# 4. RENDERIZAÇÃO DO HTML FINAL (Atualizado com colunas lado a lado)
# =====================================================================
html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <title>Painel Interativo de Análise - TCC</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; padding: 30px; background-color: #f4f7f6; color: #2c3e50; line-height: 1.6; }}
        h2 {{ color: #1a252f; margin-bottom: 5px; font-weight: 700; }}
        .subtitle {{ color: #7f8c8d; margin-top: 0; margin-bottom: 25px; font-size: 14px; }}
        
        /* Stats Grid */
        .persona-kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 15px; margin-bottom: 25px; }}
        .persona-card {{ background: white; border: 1px solid #e0e6ed; border-radius: 8px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); border-top: 4px solid #3498db; }}
        .persona-card h3 {{ margin: 0 0 10px 0; color: #2c3e50; font-size: 14px; border-bottom: 1px dashed #ecf0f1; padding-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat-line {{ display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px; padding-bottom: 2px; }}
        .stat-value {{ font-weight: 700; color: #34495e; }}
        
        /* Search Bar */
        .search-container {{ margin-bottom: 20px; }}
        .search-input {{ width: 100%; padding: 12px 20px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-family: 'Inter', sans-serif; font-size: 14px; transition: border-color 0.3s; }}
        .search-input:focus {{ border-color: #3498db; outline: none; }}

        /* Table */
        .table-container {{ background: white; padding: 0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); overflow-x: auto; border: 1px solid #ecf0f1; }}
        table {{ border-collapse: collapse; width: 100%; background: white; table-layout: fixed; }}
        th {{ background-color: #f8f9f9; color: #34495e; padding: 12px 10px; font-size: 11px; text-align: left; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #eaeded; }}
        td {{ padding: 10px; font-size: 12px; border-bottom: 1px solid #eaeded; vertical-align: middle; }}
        .clickable-row {{ cursor: pointer; transition: all 0.2s ease; }}
        .clickable-row:hover {{ background-color: #f4f6f7 !important; transform: scale(1.001); box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        
        /* Badges */
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; display: inline-block; margin-bottom: 3px; }}
        .badge-fail {{ background-color: #fdedd0; color: #e67e22; border: 1px solid #f5b041; }}
        .badge-success {{ background-color: #e8f8f5; color: #1e8449; border: 1px solid #2ecc71; }}
        
        /* Legend */
        .legend-box {{ display: flex; gap: 15px; margin-bottom: 20px; font-size: 12px; font-weight: 600; background: white; padding: 12px 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.04); }}
        .legend-item {{ display: flex; align-items: center; gap: 8px; }}
        .box-color {{ width: 16px; height: 16px; border-radius: 4px; }}
        
        /* Modal */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); }}
        .modal-content {{ background-color: #ffffff; margin: 2% auto; padding: 30px; border-radius: 12px; width: 85%; max-width: 1200px; max-height: 90vh; overflow-y: auto; box-shadow: 0 10px 40px rgba(0,0,0,0.2); animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1); }}
        @keyframes slideIn {{ from {{ opacity: 0; transform: translateY(-30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .close-btn {{ color: #a6acaf; float: right; font-size: 28px; font-weight: bold; cursor: pointer; transition: color 0.2s; }}
        .close-btn:hover {{ color: #2c3e50; }}
        .modal-header {{ border-bottom: 2px solid #ecf0f1; padding-bottom: 15px; margin-bottom: 20px; }}
        
        /* Grid & Cards inside Modal */
        .grid-gabarito {{ display: flex; gap: 25px; margin-bottom: 25px; background: #f8f9f9; border-radius: 8px; border-left: 5px solid #34495e; padding: 20px; }}
        .grid-cell {{ flex: 1; min-width: 0; }}
        .prompt-card {{ background: #ffffff; border: 1px solid #e5e8e8; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }}
        .prompt-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #d5dbdb; padding-bottom: 10px; margin-bottom: 15px; }}
        .prompt-header h4 {{ margin: 0; color: #2c3e50; font-size: 15px; }}
        .prompt-badges {{ display: flex; gap: 10px; }}
        
        .analysis-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px; }}
        .analysis-col p {{ margin: 0; font-size: 13px; color: #566573; }}
        .analysis-col b {{ color: #2c3e50; display: block; margin-bottom: 4px; }}
        
        .swot-box {{ background: #fdfefe; border: 1px solid #ebedf0; padding: 12px 15px; border-radius: 6px; }}
        .swot-box p {{ margin: 5px 0; font-size: 13px; }}
    </style>
</head>
<body>

    <h2>Matriz Interativa de Validação Qualitativa</h2>
    <p class="subtitle">Comparação direta do diagnóstico entre as 4 personas para cada Startup avaliada.</p>
    
    <div class="persona-kpi-grid">
        {html_cards_stats}
    </div>
    
    <div class="legend-box">
        <div class="legend-item"><div class="box-color" style="background-color: #1e8449;"></div> 🎯 Acertou Causa Principal</div>
        <div class="legend-item"><div class="box-color" style="background-color: #2ecc71; border: 1px dashed black;"></div> ✔️ Acertou Causa Secundária</div>
        <div class="legend-item"><div class="box-color" style="background-color: #e74c3c;"></div> ❌ Divergência (Alucinação/Erro)</div>
    </div>
    
    <div class="search-container">
        <input type="text" id="searchInput" class="search-input" onkeyup="filtrarTabela()" placeholder="🔍 Filtre por Startup, Setor ou Status Real...">
    </div>

    <div class="table-container">
        <table id="tabelaResultados">
            <thead>
                <tr>
                    <th style="width: 50px;">ID</th>
                    <th style="width: 160px;">Startup</th>
                    <th style="width: 80px; text-align: center;">Mundo Real</th>
                    <th style="width: 180px;">Controle (Baseline)</th>
                    <th style="width: 180px;">Genérica</th>
                    <th style="width: 180px;">Analítica</th>
                    <th style="width: 180px;">Advogado do Diabo</th>
                </tr>
            </thead>
            <tbody>
                {linhas_html}
            </tbody>
        </table>
    </div>

    <div id="modalDetalhes" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="fecharModal()">&times;</span>
            <div id="conteudoDinamicoModal"></div>
        </div>
    </div>

    <script>
        const dadosStartups = {js_dict_str};

        function filtrarTabela() {{
            let input = document.getElementById("searchInput");
            let filter = input.value.toUpperCase();
            let table = document.getElementById("tabelaResultados");
            let tr = table.getElementsByTagName("tr");

            for (let i = 1; i < tr.length; i++) {{
                let txtValue = tr[i].textContent || tr[i].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {{
                    tr[i].style.display = "";
                }} else {{
                    tr[i].style.display = "none";
                }}
            }}
        }}

        function abrirModal(id) {{
            const data = dadosStartups[id];
            if(!data) return;
            
            const corStatus = data.status === 'FALHA' ? '#78281f' : '#145a32';
            const bgStatus = data.status === 'FALHA' ? '#fadbd8' : '#d4efdf';

            let htmlModal = `
                <div class="modal-header">
                    <h2 style="margin:0;">${{data.nome}} <span style="font-size:14px; font-weight:normal; color:#7f8c8d;">(${{data.setor}})</span></h2>
                </div>
                
                <div class="grid-gabarito">
                    <div class="grid-cell" style="border-right: 1px solid #e5e8e8; padding-right: 20px;">
                        <h3 style="margin-top:0; font-size:13px; color:#7f8c8d; text-transform: uppercase;">📋 Premissa Avaliada pela IA</h3>
                        <p style="font-size:13.5px; line-height:1.6; margin:0; color:#2c3e50;">${{data.premissa}}</p>
                    </div>
                    <div class="grid-cell" style="padding-left: 10px;">
                        <h3 style="margin-top:0; font-size:13px; color:#7f8c8d; text-transform: uppercase;">🔍 Desfecho do Mundo Real</h3>
                        <p style="margin:8px 0;">
                            <span style="background-color: ${{bgStatus}}; color: ${{corStatus}}; font-weight:bold; padding:4px 8px; border-radius:4px; font-size:11px; margin-right:5px;">${{data.status}}</span> 
                            ${{data.tags_gabarito_html}}
                        </p>
                        <p style="font-size:13px; line-height:1.5; margin:10px 0 0 0; color:#34495e;"><b>Motivo Histórico:</b> ${{data.motivo}}</p>
                    </div>
                </div>

                <h3 style="font-size:15px; color:#2c3e50; margin-bottom:15px; padding-bottom:5px;">🧠 Análises Qualitativas das Personas Lado a Lado</h3>
                ${{data.detalhes_ia}}
            `;

            document.getElementById('conteudoDinamicoModal').innerHTML = htmlModal;
            document.getElementById('modalDetalhes').style.display = 'block';
            document.body.style.overflow = 'hidden';
        }}

        function fecharModal() {{
            document.getElementById('modalDetalhes').style.display = 'none';
            document.body.style.overflow = 'auto';
        }}

        window.onclick = function(event) {{
            const modal = document.getElementById('modalDetalhes');
            if (event.target == modal) {{
                fecharModal();
            }}
        }}
        
        document.addEventListener('keydown', function(event) {{
            if (event.key === "Escape") {{
                fecharModal();
            }}
        }});
    </script>
</body>
</html>
"""

with open("visao_matricial_avancada.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print(
    "✨ Matriz Avançada Gerada! Abra 'visao_matricial_avancada.html' no seu navegador."
)
