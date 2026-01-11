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
body {
    background-color: #f4f8ff;
}
.stApp {
    background-color: #f4f8ff;
}
h1, h2, h3 {
    color: #0a2e5c;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.06);
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
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.title("LICITA360")
st.subheader("Plataforma Inteligente de Monitoramento de Licitações Públicas")
st.markdown("Dados oficiais do **Portal Nacional de Contratações Públicas (PNCP)**")
st.markdown("</div>", unsafe_allow_html=True)

# ================= FILTROS =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### 🔎 Filtros de Busca")

col1, col2, col3 = st.columns(3)

with col1:
    palavra = st.text_input("Palavra-chave do objeto", value="medicamento")

with col2:
    uf = st.selectbox(
        "UF",
        ["", "BA","SP","RJ","MG","RS","PR","SC","PE","CE","GO","DF"]
    )

with col3:
    modalidade = st.selectbox(
        "Modalidade",
        ["", "Pregão", "Concorrência", "Dispensa", "Inexigibilidade"]
    )

col4, col5 = st.columns(2)
with col4:
    data_inicio = st.date_input("Data inicial", value=date.today())
with col5:
    data_fim = st.date_input("Data final", value=date.today())

st.markdown("</div>", unsafe_allow_html=True)

# ================= FUNÇÃO PNCP (ENDPOINT ESTÁVEL) =================
def buscar_pncp(palavra, uf, modalidade, data_ini, data_fim):
    url = "https://pncp.gov.br/api/consulta/v1/contratacoes"

    params = {
        "pagina": 1,
        "tamanhoPagina": 50,
        "dataInicial": data_ini,
        "dataFinal": data_fim,
        "objeto": palavra
    }

    if uf:
        params["uf"] = uf
    if modalidade:
        params["modalidade"] = modalidade

    r = requests.get(url, params=params, timeout=30)

    if r.status_code != 200:
        st.error(f"Erro ao consultar PNCP ({r.status_code})")
        return pd.DataFrame()

    dados = r.json()

    if "data" not in dados or not dados["data"]:
        return pd.DataFrame()

    linhas = []
    for item in dados["data"]:
        linhas.append({
            "Órgão": item.get("orgaoEntidade", {}).get("razaoSocial", ""),
            "UF": item.get("orgaoEntidade", {}).get("uf", ""),
            "Modalidade": item.get("modalidadeNome", ""),
            "Número": item.get("numeroProcesso", ""),
            "Objeto": item.get("objeto", ""),
            "Valor Estimado (R$)": item.get("valorGlobal", ""),
            "Situação": item.get("situacaoNome", ""),
            "Publicação": item.get("dataPublicacao", ""),
            "Link PNCP": f"https://pncp.gov.br/app/contratacoes/{item.get('id')}"
        })

    return pd.DataFrame(linhas)

# ================= BUSCA =================
st.markdown("<div class='card'>", unsafe_allow_html=True)

if st.button("🔍 Buscar Licitações"):
    with st.spinner("Consultando base oficial do PNCP..."):
        df = buscar_pncp(
            palavra,
            uf,
            modalidade,
            data_inicio.strftime("%Y-%m-%d"),
            data_fim.strftime("%Y-%m-%d")
        )

    if df.empty:
        st.warning("Nenhuma licitação encontrada com esses filtros.")
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
    "<center><small>LICITA360 © 2026 | Plataforma profissional de licitações</small></center>",
    unsafe_allow_html=True
)

