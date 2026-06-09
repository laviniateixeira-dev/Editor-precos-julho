import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import base64
import json
import os
import time
from datetime import datetime

# ==========================================
# INICIALIZAÇÃO DE SESSÃO GERAL E CACHE
# ==========================================
ARQUIVO_HISTORICO = "historico_pricing.csv"

if 'history_df' not in st.session_state:
    if os.path.exists(ARQUIVO_HISTORICO):
        st.session_state['history_df'] = pd.read_csv(ARQUIVO_HISTORICO)
    else:
        st.session_state['history_df'] = pd.DataFrame()

# Quebrador de cache para garantir que o GitHub mande o arquivo novo
if "cb_version" not in st.session_state:
    st.session_state["cb_version"] = int(time.time())

# ==========================================
# CONFIGURAÇÕES DA PÁGINA E LINKS
# ==========================================
feriado_atual = "corpus_2026"
BASE_URL_CURVA = f"https://raw.githubusercontent.com/laviniateixeira-dev/Pricing-Corpus-Christi/main/data/curva_{feriado_atual}.csv"

st.set_page_config(
    page_title="Pricing · Editor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PREMIUM VIBRANTE ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

:root {
  --buser-pink: #FF3377;
  --buser-pink-transp: rgba(255, 51, 119, 0.15);
}

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
h1, h2, h3, .pg-title, .section-title { font-family: 'DM Serif Display', serif !important; color: var(--text-color) !important; }

.pg-header { display: flex; align-items: flex-end; justify-content: space-between; padding-bottom: 0.2rem; }
.pg-eyebrow { font-size: .75rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; color: var(--buser-pink); margin-bottom: 4px; }
.pg-title { font-size: 2.5rem; font-weight: 400; line-height: 1.1; display: flex; align-items: center; }
.header-divider { border-bottom: 2px solid var(--buser-pink-transp); padding-bottom: 1rem; margin-bottom: 1.5rem; display: flex; justify-content: flex-end; }

.live-dot { height: 12px; width: 12px; background-color: var(--buser-pink); border-radius: 50%; display: inline-block; margin-right: 15px; box-shadow: 0 0 0 0 rgba(255, 51, 119, 0.7); animation: pulse-pink 2s infinite; }
@keyframes pulse-pink {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 51, 119, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 51, 119, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 51, 119, 0); }
}

.section-label { font-size: .75rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: var(--buser-pink) !important; margin-bottom: 8px; margin-top: 2rem; }

/* Configuração Geral dos Inputs */
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stTextInput"] div[data-baseweb="input"] { 
    background-color: transparent !important; 
    border: 1px solid var(--buser-pink) !important; 
    border-radius: 6px !important; 
    min-height: 42px !important; 
}
[data-testid="stTextInput"] input { background-color: transparent !important; border: none !important; }
[data-testid="stTextInput"] input, [data-testid="stTextInput"] input::placeholder { color: var(--buser-pink) !important; font-weight: 600 !important; -webkit-text-fill-color: var(--buser-pink) !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] *, [data-testid="stMultiSelect"] [data-baseweb="select"] * { color: var(--buser-pink) !important; font-weight: 600 !important; }

/* CORREÇÃO DAS TAGS DO MULTISELECT */
[data-testid="stMultiSelect"] [data-baseweb="tag"] { 
    background-color: transparent !important; 
    border: 1px solid var(--buser-pink) !important; 
    border-radius: 4px !important; 
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] span { 
    background-color: transparent !important; 
    color: var(--buser-pink) !important; 
    font-weight: 700 !important; 
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] div[role="button"] { background-color: transparent !important; }
[data-testid="stMultiSelect"] [data-baseweb="tag"] div[role="button"]:hover { background-color: var(--buser-pink-transp) !important; }
[data-testid="stMultiSelect"] [data-baseweb="tag"] div[role="button"] svg { fill: var(--buser-pink) !important; }

/* Configurações de Popover, Botões e Tabelas */
[data-baseweb="popover"] [data-baseweb="menu"] { background-color: var(--background-color) !important; border: 1px solid var(--buser-pink) !important; }
[data-baseweb="option"] { color: var(--buser-pink) !important; font-weight: 600 !important; }
[data-baseweb="option"]:hover, [aria-selected="true"][data-baseweb="option"] { background-color: var(--buser-pink-transp) !important; }
[data-testid="stButton"] button { border-color: var(--buser-pink) !important; color: var(--buser-pink) !important; font-weight: 600 !important; border-radius: 6px !important; }
[data-testid="stButton"] button:hover { background-color: var(--buser-pink) !important; color: white !important; }
[data-testid="stButton"] button[kind="primary"] { background-color: var(--buser-pink) !important; color: white !important; }
[data-testid="stDataTable"] { border: 1px solid rgba(150, 150, 150, 0.2) !important; border-radius: 8px !important; }
[data-testid="stTabs"] [data-baseweb="tab"] { font-family: 'DM Sans', sans-serif !important; padding-top: 10px; padding-bottom: 10px; }
[data-testid="stTabs"] [aria-selected="true"][data-baseweb="tab"] { color: var(--buser-pink) !important; border-bottom-color: var(--buser-pink) !important; font-weight: 700 !important; }
.acion-banner { display: flex; align-items: center; background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-left: 4px solid #10B981; border-radius: 8px; padding: 14px 20px; margin: 1.5rem 0 1rem; }
.acion-txt { font-size: .95rem; color: #10B981 !important; font-weight: 700; }
.warn-banner { background-color: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-left: 4px solid #F59E0B; border-radius: 8px; padding: 12px 18px; margin-bottom: 1rem; font-size: .9rem; color: #F59E0B; font-weight: 600; }
.footer { display: flex; justify-content: space-between; align-items: center; padding-top: 1.5rem; margin-top: 2rem; border-top: 1px solid rgba(150, 150, 150, 0.2); }
.ftxt { font-size: .8rem; font-weight: 500; color: var(--text-color); opacity: 0.6; }
</style>
""", unsafe_allow_html=True)

# ── LOAD & PREP ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data(base_url: str, version: int) -> pd.DataFrame:
    try:
        url = f"{base_url}?v={version}"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df
    except Exception:
        return pd.DataFrame()

def prep_editor(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    df = df.copy()
    
    if "data" in df.columns and "data_atual" not in df.columns:
        df = df.rename(columns={"data": "data_atual"})
    
    for c in df.columns:
        # Adicionei "ocupacao" aqui para garantir que ela vire numérico
        if any(keyword in c for keyword in ["lf", "ratio", "tkm", "price", "mult", "preco", "ocupacao"]):
            df[c] = pd.to_numeric(df[c].astype(str).str.replace("null", ""), errors="coerce")
        elif any(keyword in c for keyword in ["buscas", "pax", "capacidade", "vagas", "antecedencia"]):
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
            
    if "data_atual" in df.columns: df["data_atual"] = pd.to_datetime(df["data_atual"], errors="coerce")
    return df

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label" style="margin-top:0;">Controle de Dados</div>', unsafe_allow_html=True)

    if st.button("Atualizar Cache", use_container_width=True):
        st.session_state["cb_version"] = int(time.time())
        st.cache_data.clear()
        st.rerun()

    cb = st.session_state["cb_version"]
    df_editor_raw = prep_editor(load_data(BASE_URL_CURVA, cb))

# ── ABAS DA PÁGINA ────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Editor de Preços", "Histórico de Alterações"])

# ── FUNÇÃO 1: EDITOR DE PREÇOS ────────────────────────────────────────────────
def render_editor(df_raw: pd.DataFrame, tab_key: str, titulo: str):
    agora_t = datetime.now().strftime("%d/%m/%Y %H:%M")

    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown(f"""
        <div class="pg-header">
          <div>
            <div class="pg-eyebrow">Ações de Pricing</div>
            <div class="pg-title"><span class="live-dot"></span>{titulo}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_t2:
        opcoes_dropdown = ["Páscoa 2026", "Corpus 2025", "Maio 2026"]
        st.write("") 
        ref_nome = st.selectbox("Comparar com (Ref):", opcoes_dropdown, key=f"{tab_key}_ref_sel")
        
        mapa_ref = {
            "Páscoa 2026": "pascoa_2026",
            "Corpus 2025": "corpus_2025",
            "Maio 2026": "maio_2026"
        }
        ref_sel = mapa_ref.get(ref_nome, "pascoa_2026")

        col_data_ref = f"data_ref_{ref_sel}"
        col_buscas_ref = f"buscas_{ref_sel}"
        col_lf_ref = f"lf_{ref_sel}"
        col_ratio_ref = f"ratio_lf_{ref_sel}"
        col_tkm_ref = f"tkm_{ref_sel}"

        col_buscas_atual = f"buscas_{feriado_atual}"
        col_pax_atual = "pax_atual"
        col_lf_atual = "lf_atual"

    st.markdown(f'<div class="header-divider"><span style="color:var(--text-color); opacity: 0.6; font-size:0.85rem; font-weight: 500;">Atualizado via Databricks às {agora_t}</span></div>', unsafe_allow_html=True)

    if df_raw.empty:
        st.info("Nenhum dado encontrado para o editor. Verifique o arquivo no GitHub.")
        return

    essenciais = [col_data_ref, col_lf_ref, col_tkm_ref, col_buscas_atual, col_lf_atual]
    faltam = [c for c in essenciais if c not in df_raw.columns]
    if faltam:
        st.markdown(f'<div class="warn-banner">⚠️ Atenção: Faltam algumas colunas no CSV ({", ".join(faltam)}). Tente apertar o botão "Atualizar Cache" no menu lateral.</div>', unsafe_allow_html=True)

    def calc_row_id(row):
        data_val = row.get("data_atual")
        d_str = pd.to_datetime(data_val).strftime("%Y-%m-%d") if pd.notna(data_val) else ""
        return f"{d_str}|{row.get('turno','')}|{row.get('sentido','')}|{row.get('tipo_assento','')}"

    if "row_id" not in df_raw.columns:
        df_raw["row_id"] = df_raw.apply(calc_row_id, axis=1)

    dict_key = f"{tab_key}_edits_dict"
    if dict_key not in st.session_state: st.session_state[dict_key] = {}
    key_enviadas = f"{tab_key}_linhas_enviadas"
    if key_enviadas not in st.session_state: st.session_state[key_enviadas] = set()
    key_version = f"{tab_key}_editor_version"
    if key_version not in st.session_state: st.session_state[key_version] = 0

    st.markdown('<div class="section-label" style="margin-top: 0.5rem;">Filtros de Busca</div>', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        datas_c = sorted(df_raw["data_atual"].dt.date.dropna().unique())
        datas_c_sel = st.multiselect("Data da Viagem:", options=datas_c, default=datas_c, format_func=lambda d: d.strftime("%d/%m"), key=f"{tab_key}_datas")
    with col_f2:
        turnos_c = sorted(df_raw["turno"].dropna().unique())
        turnos_sel = st.multiselect("Turno:", options=turnos_c, default=turnos_c, key=f"{tab_key}_turnos")
    with col_f3:
        rota_c = st.text_input("Buscar Sentido:", placeholder="Ex: BHZ-RIO", key=f"{tab_key}_rota")

    df_cv = df_raw.copy()
    if datas_c_sel: df_cv = df_cv[df_cv["data_atual"].dt.date.isin(datas_c_sel)]
    if turnos_sel:  df_cv = df_cv[df_cv["turno"].isin(turnos_sel)]
    if rota_c:      df_cv = df_cv[df_cv["sentido"].str.upper().str.contains(rota_c.upper(), na=False)]

    mask_enviadas = df_cv["row_id"].isin(st.session_state[key_enviadas])
    n_ocultas = int(mask_enviadas.sum())
    df_cv_editor = df_cv[~mask_enviadas].reset_index(drop=True)

    if n_ocultas > 0:
        col_oc1, col_oc2 = st.columns([5, 1])
        with col_oc1:
            st.markdown(f'<div class="warn-banner">Atenção: {n_ocultas} linhas que você já enviou estão ocultas.</div>', unsafe_allow_html=True)
        with col_oc2:
            if st.button("Mostrar Todas", key=f"{tab_key}_mostrar"):
                st.session_state[key_enviadas] = set()
                st.rerun()

    # Adicionada "ocupacao_atual" aqui nas colunas brutas
    cols_editor = [
        "row_id", col_data_ref, "data_atual", "dia_da_semana", "antecedencia", 
        "rota_principal", "sentido", "tipo_assento", "turno", 
        col_buscas_ref, col_buscas_atual, col_pax_atual, "capacidade_atual", "vagas_restantes", "ocupacao_atual", 
        col_lf_ref, col_lf_atual, col_ratio_ref, "price_cc", col_tkm_ref, "tkm_atual", 
        "mult_atual_aplicado", "preco_cenario_atual", "mult_flutuacao", "preco_flutuacao", 
        "preco_maximo_feriado", "data_atualizacao"
    ]
    cols_presentes = [c for c in cols_editor if c in df_cv_editor.columns]
    df_editor = df_cv_editor[cols_presentes].copy()

    df_editor["data_fmt"] = pd.to_datetime(df_editor["data_atual"]).dt.strftime("%d/%m/%Y")
    
    if col_data_ref in df_editor.columns:
        df_editor["data_ref_fmt"] = pd.to_datetime(df_editor[col_data_ref], errors="coerce").dt.strftime("%d/%m/%Y").fillna("-")

    if col_ratio_ref in df_editor.columns: 
        df_editor["ratio_ref_fmt"] = df_editor[col_ratio_ref].astype(float).round(3).astype(str) + "x"
    
    if col_lf_ref in df_editor.columns: 
        df_editor["lf_ref_fmt"] = (df_editor[col_lf_ref] * 100).astype(float).round(1).astype(str) + "%"
    
    if col_lf_atual in df_editor.columns: 
        df_editor["lf_a_fmt"] = (df_editor[col_lf_atual] * 100).astype(float).round(1).astype(str) + "%"
        
    # Formatação da nova coluna ocupacao_atual em texto (%)
    if "ocupacao_atual" in df_editor.columns:
        df_editor["ocupacao_a_fmt"] = (df_editor["ocupacao_atual"].astype(float) * 100).round(1).astype(str) + "%"

    df_editor["incluir"] = True
    df_editor["Preco novo"] = None

    # Adicionada "ocupacao_a_fmt" aqui nas colunas visuais
    show_cols = [
        "incluir", "data_ref_fmt", "data_fmt", "dia_da_semana", "antecedencia", "rota_principal", "sentido", "tipo_assento", "turno", 
        col_buscas_ref, col_buscas_atual, col_pax_atual, "capacidade_atual", "vagas_restantes", "ocupacao_a_fmt",
        "lf_ref_fmt", "lf_a_fmt", "ratio_ref_fmt", "price_cc", col_tkm_ref, "tkm_atual", 
        "mult_atual_aplicado", "preco_cenario_atual", "mult_flutuacao", "preco_flutuacao", "preco_maximo_feriado", "data_atualizacao", "Preco novo"
    ]
    
    show_cols_safe = [c for c in show_cols if c in df_editor.columns]
    
    df_show = df_editor.set_index("row_id")[show_cols_safe].copy()

    # Adicionado "ocupacao_a_fmt" nas configurações de layout
    col_config = {
        "incluir": st.column_config.CheckboxColumn("Incluir", default=True),
        "data_ref_fmt": st.column_config.TextColumn(f"Data Ref. ({ref_nome})", disabled=True),
        "data_fmt": st.column_config.TextColumn("Data Atual", disabled=True),
        "dia_da_semana": st.column_config.TextColumn("Dia Semana", disabled=True),
        "antecedencia": st.column_config.NumberColumn("Antec.", disabled=True),
        "rota_principal": st.column_config.TextColumn("Rota", disabled=True),
        "sentido": st.column_config.TextColumn("Sentido", disabled=True),
        "tipo_assento": st.column_config.TextColumn("Assento", disabled=True),
        "turno": st.column_config.TextColumn("Turno", disabled=True),
        col_buscas_ref: st.column_config.NumberColumn(f"Buscas ({ref_nome})", disabled=True),
        col_buscas_atual: st.column_config.NumberColumn("Buscas Atual", disabled=True),
        col_pax_atual: st.column_config.NumberColumn("PAX Atual", disabled=True),
        "capacidade_atual": st.column_config.NumberColumn("Capacidade", disabled=True),
        "vagas_restantes": st.column_config.NumberColumn("↑ Vagas", disabled=True),
        "ocupacao_a_fmt": st.column_config.TextColumn("Ocupação", disabled=True), # NOVA COLUNA
        "lf_ref_fmt": st.column_config.TextColumn(f"LF ({ref_nome})", disabled=True),
        "lf_a_fmt": st.column_config.TextColumn("LF Atual", disabled=True),
        "ratio_ref_fmt": st.column_config.TextColumn(f"Ratio LF ({ref_nome})", disabled=True),
        "price_cc": st.column_config.NumberColumn("Price CC", disabled=True, format="R$ %.0f"),
        col_tkm_ref: st.column_config.NumberColumn(f"TKM ({ref_nome})", disabled=True, format="R$ %.0f"),
        "tkm_atual": st.column_config.NumberColumn("TKM Atual", disabled=True, format="R$ %.0f"),
        "mult_atual_aplicado": st.column_config.NumberColumn("Mult Final", disabled=True, format="%.3fx"),
        "preco_cenario_atual": st.column_config.NumberColumn("Preço Cenario", disabled=True, format="R$ %.2f"),
        "mult_flutuacao": st.column_config.NumberColumn("Mult Flutuação", disabled=True, format="%.2fx"),
        "preco_flutuacao": st.column_config.NumberColumn("Preço Flutuação", disabled=True, format="R$ %.2f"),
        "preco_maximo_feriado": st.column_config.NumberColumn("Teto Flutuação", disabled=True, format="R$ %.2f"),
        "data_atualizacao": st.column_config.TextColumn("Data Atualização", disabled=True), 
        "Preco novo": st.column_config.NumberColumn("Preço Novo", min_value=0.0, format="R$ %.2f"),
    }

    st.markdown('<div class="section-label">Planilha de Edição</div>', unsafe_allow_html=True)
    edited = st.data_editor(
        df_show, use_container_width=True, hide_index=True, column_config=col_config,
        num_rows="fixed", key=f"{tab_key}_editor_{st.session_state[key_version]}"
    )

    for r_id, row in edited.iterrows():
        preco = row.get("Preco novo")
        inc = row.get("incluir")

        if pd.notna(preco):
            st.session_state[dict_key][r_id] = {
                "Preco novo": preco,
                "incluir": inc if pd.notna(inc) else True
            }
        else:
            if r_id in st.session_state[dict_key]:
                del st.session_state[dict_key][r_id]

    if st.session_state[dict_key]:
        st.markdown('<div class="section-label">Pronto para Enviar (Carrinho)</div>', unsafe_allow_html=True)
        
        edited_ids = list(st.session_state[dict_key].keys())
        df_todas_edicoes = df_raw[df_raw["row_id"].isin(edited_ids)].copy()
        
        df_todas_edicoes["Preco novo"] = df_todas_edicoes["row_id"].map(lambda x: st.session_state[dict_key][x]["Preco novo"])
        df_todas_edicoes["incluir"] = df_todas_edicoes["row_id"].map(lambda x: st.session_state[dict_key][x]["incluir"])
        
        df_editado = df_todas_edicoes[df_todas_edicoes["incluir"] == True].copy()
        n_excluidas = len(df_todas_edicoes) - len(df_editado)

        if not df_editado.empty:
            p_flut = df_editado["preco_flutuacao"].astype(float) if "preco_flutuacao" in df_editado.columns else pd.Series(np.nan, index=df_editado.index)
            m_split = df_editado["max_split"].astype(float) if "max_split" in df_editado.columns else pd.Series(np.nan, index=df_editado.index)
            
            base_vals = p_flut.replace(0.0, np.nan).fillna(m_split)
            
            df_editado["_base_calc"] = base_vals
            df_editado["_mult_novo"] = (df_editado["Preco novo"] / df_editado["_base_calc"]).round(6)

            df_editado["data_fmt"] = pd.to_datetime(df_editado["data_atual"]).dt.strftime("%d/%m/%Y")
            df_acionamento = pd.DataFrame({
                "row_id": df_editado["row_id"].values,
                "data": pd.to_datetime(df_editado["data_fmt"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d"),
                "turno": df_editado["turno"].str.title().values,
                "rota_principal": df_editado["rota_principal"].values,
                "sentido": df_editado["sentido"].str.replace("-", ">").values,
                "mult": df_editado["_mult_novo"].values,
                "max_split_antigo": df_editado["_base_calc"].values,
                "max_split_novo": df_editado["Preco novo"].values
            })

            n_edit = len(df_acionamento)
            excl_str = f" ({n_excluidas} ignoradas no envio)" if n_excluidas > 0 else ""
            st.markdown(f'<div class="acion-banner"><span class="acion-txt"> {n_edit} linha(s) no acionamento{excl_str}</span></div>', unsafe_allow_html=True)
            
            df_export = df_acionamento.drop(columns=["row_id", "max_split_antigo", "max_split_novo"], errors='ignore')
            st.dataframe(df_export, use_container_width=True, hide_index=True)

            col_b1, col_b2, col_b3, _ = st.columns([1.5, 1.5, 1, 3])
            csv_bytes = df_export.to_csv(index=False).encode("utf-8")

            def mark_as_sent():
                df_hist_new = df_export.copy()
                df_hist_new["Data Alteração"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                st.session_state['history_df'] = pd.concat([st.session_state['history_df'], df_hist_new], ignore_index=True)
                st.session_state['history_df'].to_csv(ARQUIVO_HISTORICO, index=False)

                for r_id in df_acionamento["row_id"]:
                    st.session_state[key_enviadas].add(r_id)
                    if r_id in st.session_state[dict_key]: del st.session_state[dict_key][r_id]
                st.session_state[key_version] += 1

            with col_b1:
                if st.download_button("Baixar como CSV", data=csv_bytes, file_name=f"pricing_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv", use_container_width=True):
                    mark_as_sent()
                    st.rerun()

            with col_b2:
                if st.button("Enviar pro GitHub", use_container_width=True, type="primary"):
                    gh_token = st.session_state.get(f"t3_gh_token", "")
                    if not gh_token: 
                        st.warning("Atenção: Cole seu token no campo abaixo primeiro.")
                    else:
                        repo = "laviniateixeira-dev/Pricing-Feriados"
                        path = f"data/alteracoes_{feriado_atual}.csv"
                        r_gh = requests.put(f"https://api.github.com/repos/{repo}/contents/{path}", 
                                            headers={"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"},
                                            data=json.dumps({"message": f"pricing: {path}", "content": base64.b64encode(csv_bytes).decode("utf-8"), "branch": "main"}))
                        if r_gh.status_code in (200, 201):
                            mark_as_sent()
                            st.success("Tudo certo! Arquivo enviado com sucesso.")
                            st.rerun()
                        else: st.error(f"Erro ao enviar: {r_gh.status_code}")

            with col_b3:
                if st.button("Limpar Edições", use_container_width=True):
                    st.session_state[key_version] += 1
                    st.session_state[key_enviadas] = set()
                    st.session_state[dict_key] = {}
                    st.rerun()

            st.text_input("Token de Acesso do GitHub (Apenas Sessão):", type="password", key=f"t3_gh_token")
    else:
        st.markdown('<div style="padding:15px 20px; background:var(--secondary-background-color); border:1px dashed var(--buser-pink); border-radius:8px; margin-top:20px; text-align:center; color:var(--text-color); font-weight: 500;">Nenhum preço alterado ainda. Preencha a coluna <b>Preço Novo</b> na tabela acima.</div>', unsafe_allow_html=True)
        if st.button("Limpar Tudo", key=f"t3_reset_empty"):
            st.session_state[key_version] += 1
            st.session_state[key_enviadas] = set()
            st.session_state[dict_key] = {}
            st.rerun()

    st.markdown(f'<div class="footer"><span class="ftxt">{len(df_cv_editor)} linhas exibidas | {n_ocultas} ocultas</span><span class="ftxt">Cálculo: Mult = Preço Novo / COALESCE(Preço Flutuação, Max Split)</span></div>', unsafe_allow_html=True)

# ── FUNÇÃO 2: HISTÓRICO DE ALTERAÇÕES ─────────────────────────────────────────
def render_historico():
    st.markdown("""
    <div class="pg-header">
      <div>
        <div class="pg-eyebrow">Acompanhamento</div>
        <div class="pg-title"><span class="live-dot"></span>Histórico de Alterações (Envios Próprios)</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_hist_1, col_hist_2 = st.columns([3, 1])
    
    with col_hist_2:
        st.markdown('<div class="section-label" style="margin-top:0;">Importar CSV Existente</div>', unsafe_allow_html=True)
        with st.form("upload_form"):
            uploaded_file = st.file_uploader("Selecione um arquivo", type=["csv"], label_visibility="collapsed")
            if st.form_submit_button("Adicionar Arquivo", use_container_width=True):
                if uploaded_file is not None:
                    try:
                        df_up = pd.read_csv(uploaded_file)
                        df_up["Data Alteração"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        st.session_state['history_df'] = pd.concat([st.session_state['history_df'], df_up], ignore_index=True)
                        st.session_state['history_df'].to_csv(ARQUIVO_HISTORICO, index=False)
                        st.success("Tudo certo! Adicionado à tabela.")
                        st.rerun()
                    except Exception as e:
                        st.error("Erro ao ler o arquivo CSV.")
                else:
                    st.warning("Selecione um arquivo primeiro.")
                    
    with col_hist_1:
        st.markdown('<div class="section-label" style="margin-top:0;">Filtros de Pesquisa</div>', unsafe_allow_html=True)
        
        df_hist = st.session_state['history_df'].copy()
        
        if not df_hist.empty:
            col_fh1, col_fh2, col_fh3 = st.columns(3)
            
            with col_fh1:
                if 'rota_principal' in df_hist.columns:
                    rotas_h = ["Todas"] + sorted(df_hist['rota_principal'].dropna().unique().tolist())
                    rota_h_sel = st.selectbox("Rota", rotas_h, key="hist_rota")
                    if rota_h_sel != "Todas":
                        df_hist = df_hist[df_hist['rota_principal'] == rota_h_sel]
                        
            with col_fh2:
                if 'sentido' in df_hist.columns:
                    sentidos_h = ["Todos"] + sorted(df_hist['sentido'].dropna().unique().tolist())
                    sentido_h_sel = st.selectbox("Sentido", sentidos_h, key="hist_sentido")
                    if sentido_h_sel != "Todos":
                        df_hist = df_hist[df_hist['sentido'] == sentido_h_sel]
                        
            with col_fh3:
                busca_livre = st.text_input("Busca Livre", placeholder="Pesquise por qualquer termo...")
                if busca_livre:
                    mask = df_hist.astype(str).apply(lambda x: x.str.contains(busca_livre, case=False, na=False)).any(axis=1)
                    df_hist = df_hist[mask]
            
            st.markdown('<div class="section-label" style="margin-top: 1.5rem;">Tabela de Ações (Permanente)</div>', unsafe_allow_html=True)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma alteração de preço registrada no histórico ainda. Suas alterações na aba 'Editor de Preços' aparecerão aqui.")

# ── RENDERIZAÇÃO FINAL DAS ABAS ─────────────────────────
with tab1: render_editor(df_editor_raw, tab_key="t3", titulo="Editor de Preços")
with tab2: render_historico()
