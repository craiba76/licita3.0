import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

st.set_page_config(page_title="LICITA360", layout="wide")

conn = sqlite3.connect("licita360.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    senha TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS licitacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orgao TEXT,
    uasg TEXT,
    processo TEXT,
    produto TEXT,
    valor REAL,
    data_abertura TEXT,
    status TEXT
)
""")
conn.commit()

def login():
    st.title("🔐 LICITA360")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
        if c.fetchone():
            st.session_state["logado"] = True
        else:
            st.error("Usuário ou senha inválidos")

    if st.button("Criar conta"):
        try:
            c.execute("INSERT INTO usuarios (email, senha) VALUES (?,?)", (email, senha))
            conn.commit()
            st.success("Conta criada! Faça login.")
        except:
            st.error("E-mail já cadastrado")

def sistema():
    st.sidebar.title("📌 LICITA360")
    menu = st.sidebar.radio("Menu", ["Cadastrar Licitação", "Minhas Licitações", "Dashboard"])

    if menu == "Cadastrar Licitação":
        st.header("➕ Nova Licitação")
        orgao = st.text_input("Órgão")
        uasg = st.text_input("UASG")
        processo = st.text_input("Nº do Processo")
        produto = st.text_input("Produto")
        valor = st.number_input("Valor Estimado", min_value=0.0)
        data_abertura = st.date_input("Data de Abertura", value=date.today())
        status = st.selectbox("Status", ["A participar", "Participou", "Ganhou", "Perdeu"])

        if st.button("Salvar"):
            c.execute("""
                INSERT INTO licitacoes (orgao, uasg, processo, produto, valor, data_abertura, status)
                VALUES (?,?,?,?,?,?,?)
            """, (orgao, uasg, processo, produto, valor, data_abertura, status))
            conn.commit()
            st.success("Licitação cadastrada!")

    elif menu == "Minhas Licitações":
        st.header("📋 Licitações")
        df = pd.read_sql("SELECT * FROM licitacoes", conn)
        st.dataframe(df, use_container_width=True)

    elif menu == "Dashboard":
        st.header("📊 Dashboard")
        df = pd.read_sql("SELECT * FROM licitacoes", conn)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", len(df))
        col2.metric("A Participar", len(df[df.status == "A participar"]))
        col3.metric("Ganhou", len(df[df.status == "Ganhou"]))
        col4.metric("Perdeu", len(df[df.status == "Perdeu"]))

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    login()
else:
    sistema()
