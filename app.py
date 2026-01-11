import streamlit as st
import pandas as pd
import requests
from datetime import date

st.set_page_config(page_title="LICITA360", layout="wide")

st.title("📊 LICITA360 – Licitações Oficiais do PNCP")

def buscar_pncp(data_inicial, data_final):
    url = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "pagina": 1,
        "tamanhoPagina": 50
    }

    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, params=params, headers=headers, timeout=30)

    if response.status_code != 200:
        st.error(f"Erro PNCP: {response.status_code}")
        return pd.DataFrame()

    dados = response.json()

    if not dados or "data" not in dados or len(dados["data"]) == 0:
        return pd.DataFrame()

    linhas = []

    for item in dados["data"]:
        linhas.append({
            "Órgão": item.get("orgaoEntidade", {}).get("razaoSocial", ""),
            "UF": item.get("orgaoEntidade", {}).get("uf", ""),
            "Modalidade": item.get("modalidadeNome", ""),
            "Objeto": item.get("objeto", ""),
            "Valor Estimado (R$)": item.get("valorGlobal", ""),
            "Data Publicação": item.get("dataPublicacao", ""),
            "Link PNCP": f"https://pncp.gov.br/app/contratacoes/{item.get('id')}"
        })

    return pd.DataFrame(linhas)


data_inicial = st.date_input(
    "📅 Data inicial",
    value=date.today()
)

data_final = st.date_input(
    "📅 Data final",
    value=date.today()
)

if st.button("🔍 Buscar Licitações no PNCP"):
    with st.spinner("Consultando base oficial do governo (PNCP)..."):
        df = buscar_pncp(
            data_inicial.strftime("%Y-%m-%d"),
            data_final.strftime("%Y-%m-%d")
        )

    if df.empty:
        st.warning("Nenhuma licitação encontrada neste período.")
    else:
        st.success(f"✅ {len(df)} licitações encontradas")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "📥 Baixar Excel",
            df.to_csv(index=False, sep=";").encode("utf-8"),
            file_name="licitacoes_pncp.csv"
        )

