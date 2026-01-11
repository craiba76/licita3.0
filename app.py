
import streamlit as st
import pandas as pd
import requests
from datetime import date

# ================== CONFIGURAÇÃO VISUAL ==================
st.set_page_config(
    page_title="LICITA360",
    page_icon="📘",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #f5f9ff;
    }
    h1, h2, h3 {
        color: #0b3c68;
    }
    .stButton>button {
        background-color: #0b5ed7;
        color: white;
        border-radius: 8px;
        height: 45px;
        width: 100%;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ================== CABEÇALHO ==================
st.title("📘 LICITA360")
st.subheader("Consulta Oficial de Licitações – PNCP")

st.markdown("---")

# ================== FILTROS ==================
col1, col2, col3, col4 = st.columns(4)

with col1:
    palavra = st.text_input("🔎 Palavra-chave", value="medicamento")

with col2:
    uf = st.selectbox(
        "📍 UF",
        ["", "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS",
         "MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]
    )

with col3:
    data_inicial = st.date_input("📅 Data inicial", value=date.today())

with col4:
    data_final = st.date_input("📅 Data final", value=date.today())

# ================== FUNÇÃO PNCP ==================
def buscar_pncp(palavra, uf, data_ini, data_fim):
    url = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

    params = {
        "palavraChave": palavra,
        "dataInicial": data_ini,
        "dataFinal": data_fim,
        "pagina": 1,
        "tamanhoPagina": 50
    }

    if uf:
        params["uf"] = uf

    response = requests.get(url, params=params, timeout=30)

    if response.status_code != 200:
        st.error(f"❌ Erro PNCP: {response.status_code}")
        return pd.DataFrame()

    dados = response.json()

    if "data" not in dados or not dados["data"]:
        return pd.DataFrame()

    registros = []

    for item in dados["data"]:
        registros.append({
            "Órgão": item.get("orgaoEntidade", {}).get("razaoSocial", ""),
            "UF": item.get("orgaoEntidade", {}).get("uf", ""),
            "Modalidade": item.get("modalidadeNome", ""),
            "Nº Processo": item.get("numeroProcesso", ""),
            "Objeto": item.get("objeto", ""),
            "Valor Estimado (R$)": item.get("valorGlobal", ""),
            "Data Publicação": item.get("dataPublicacao", ""),
            "Situação": item.get("situacaoNome", ""),
            "Link PNCP": f"https://pncp.gov.br/app/contratacoes/{item.get('id')}"
        })

    return pd.DataFrame(registros)

# ================== BOTÃO BUSCAR ==================
st.markdown("##")

if st.button("🔍 Buscar Licitações no PNCP"):
    with st.spinner("Consultando base oficial do PNCP..."):
        df = buscar_pncp(
            palavra,
            uf,
            data_inicial.strftime("%Y-%m-%d"),
            data_final.strftime("%Y-%m-%d")
        )

    if df.empty:
        st.warning("⚠️ Nenhuma licitação encontrada.")
    else:
        st.success(f"✅ {len(df)} licitações encontradas")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "📥 Baixar Excel",
            df.to_csv(index=False, sep=";").encode("utf-8"),
            file_name="licitacoes_pncp.csv"
        )

# ================== RODAPÉ ==================
st.markdown("---")
st.markdown(
    "<center><small>LICITA360 © 2026 – Dados oficiais do PNCP</small></center>",
    unsafe_allow_html=True
)
