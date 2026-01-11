import streamlit as st
import requests
import pandas as pd
from datetime import date

st.set_page_config(page_title="LICITA360", layout="wide")

st.title("📊 LICITA360 – Monitoramento de Licitações (PNCP)")

menu = st.sidebar.radio(
    "Menu",
    ["Buscar Licitações PNCP", "Painel"]
)

# ================= PNCP ==================
def buscar_pncp(data_inicial, data_final):
    url = "https://pncp.gov.br/api/pncp/v1/contratacoes/publicacao"
    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "pagina": 1,
        "tamanhoPagina": 50
    }

    response = requests.get(url, params=params, timeout=30)

    if response.status_code == 200:
        dados = response.json()
        return dados.get("data", [])
    else:
        return []

# ================= MENU ==================
if menu == "Buscar Licitações PNCP":
    st.header("🔍 Buscar Licitações Reais do PNCP")

    col1, col2 = st.columns(2)
    data_inicial = col1.date_input("Data inicial", value=date.today())
    data_final = col2.date_input("Data final", value=date.today())

    if st.button("🔎 Buscar no PNCP"):
        with st.spinner("Consultando dados oficiais do PNCP..."):
            resultados = buscar_pncp(
                data_inicial.strftime("%Y-%m-%d"),
                data_final.strftime("%Y-%m-%d")
            )

        if resultados:
            df = pd.DataFrame(resultados)
            st.success(f"{len(df)} licitações encontradas")
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "⬇️ Baixar Excel",
                df.to_csv(index=False),
                "licitacoes_pncp.csv",
                "text/csv"
            )
        else:
            st.warning("Nenhuma licitação encontrada nesse período.")

elif menu == "Painel":
    st.header("📈 Painel LICITA360")
    st.info("Painel pronto para próxima fase (filtros, alertas e favoritos)")
