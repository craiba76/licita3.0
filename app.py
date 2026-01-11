import streamlit as st
import pandas as pd
import requests
from datetime import date

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(
    page_title="LICITA360",
    page_icon="🔵",
    layout="wide"
)

# ================= ESTILO PROFISSIONAL =================
st.markdown("""
<style>
.stApp {
    background-color: #f4f8ff;
}
h1, h2, h3 {
    color: #0a2e5c;
}
.box {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}
.stButton>button {
    background-color: #0d6efd;
    color: white;
    border-radius: 10px;
    height: 46px;
    font-size: 16px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ================= CABEÇALHO =================
st.markdown("<div class='box'>", unsafe_allow_html=True)
st.title("LICITA360")
st.subheader("Consulta Oficial de Licitações Públicas")
st.markdown("Fonte: **Portal Nacional de Contratações Públicas (PNCP)**")
st.markdown("</div>", unsafe_allow_html=True)

# ================= FILTROS =================
st.markdown("<div class='box'>", unsafe_allow_html=True)
st.markdown("### 🔎 Filtros obrigatórios")

col1, col2, col3 = st.columns(3)

with col1:
    palavra = st.text_input("Palavra-chave do objeto", value="medicamento")

with col2:
    data_inicio = st.date_input("Data inicial", value=date.today())

with col3:
    data_fim = st.date_input("Data final", value=date.today())

st.markdown("</div>", unsafe_allow_html=True)

# ================= FUNÇÃO PNCP CORRETA =================
def buscar_pncp(palavra, data_ini, data_fim):
    url = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

    params = {
        "palavraChave": palavra,
        "dataInicial": data_ini,
        "dataFinal": data_fim,
        "pagina": 1,
        "tamanhoPagina": 50
    }

    response = requests.get(url, params=params, timeout=30)

    if response.status_code != 200:
        st.error(f"Erro PNCP ({response.status_code})")
        return pd.DataFrame()

    dados = response.json()

    if "data" not in dados or not dados["data"]:
        return pd.DataFrame()

    linhas = []
    for item in dados["data"]:
        linhas.append({
            "Órgão": item.get("orgaoEntidade", {}).get("razaoSocial", ""),
            "UF": item.get("orgaoEntidade", {}).get("uf", ""),
            "Modalidade": item.get("modalidadeNome", ""),
            "Processo": item.get("numeroProcesso", ""),
            "Objeto": item.get("objeto", ""),
            "Valor Estimado": item.get("valorGlobal", ""),
            "Situação": item.get("situacaoNome", ""),
            "Publicação": item.get("dataPublicacao", ""),
            "Link PNCP": f"https://pncp.gov.br/app/contratacoes/{item.get('id')}"
        })

    return pd.DataFrame(linhas)

# ================= BOTÃO BUSCAR =================
st.markdown("<div class='box'>", unsafe_allow_html=True)

if st.button("🔍 Buscar Licitações no PNCP"):
    with st.spinner("Consultando dados oficiais do PNCP..."):
        df = buscar_pncp(
            palavra,
            data_inicio.strftime("%Y-%m-%d"),
            data_fim.strftime("%Y-%m-%d")
        )

    if df.empty:
        st.warning("Nenhuma licitação encontrada para os filtros informados.")
    else:
        st.success(f"{len(df)} licitações encontradas")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "📥 Exportar Excel",
            df.to_csv(index=False, sep=";").encode("utf-8"),
            file_name="licitacoes_pncp.csv"
        )

st.markdown("</div>", unsafe_allow_html=True)

# ================= RODAPÉ =================
st.markdown(
    "<center><small>LICITA360 © 2026 – Dados oficiais do PNCP</small></center>",
    unsafe_allow_html=True
)

