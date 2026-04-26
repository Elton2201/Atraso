# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Relatório de Atraso",
    layout="wide"
)

st.title("Dashboard - Relatório de Atraso")

# -------------------------------
# Upload seguro do arquivo
# -------------------------------
st.subheader("Enviar Planilha")

arquivo = st.file_uploader(
    "Faça upload do arquivo Excel (.xlsx)",
    type=["xlsx"]
)

if arquivo is not None:

    @st.cache_data
    def carregar_dados(file):
        df = pd.read_excel(file)

        # Remove espaços extras dos nomes das colunas
        df.columns = df.columns.str.strip()

        return df

    df = carregar_dados(arquivo)

    st.success("Arquivo carregado com sucesso!")

    # -------------------------------
    # Visualizar base
    # -------------------------------
    with st.expander("Visualizar base de dados"):
        st.dataframe(df, use_container_width=True)

    # -------------------------------
    # Sidebar - Filtros
    # -------------------------------
    st.sidebar.header("Filtros")

    fornecedor = st.sidebar.multiselect(
        "Fornecedor",
        options=sorted(df["DES_FORNECEDOR"].dropna().unique()),
        default=sorted(df["DES_FORNECEDOR"].dropna().unique())
    )

    nivel = st.sidebar.multiselect(
        "Nível",
        options=sorted(df["NIVEL"].dropna().unique()),
        default=sorted(df["NIVEL"].dropna().unique())
    )

    mes = st.sidebar.multiselect(
        "Mês",
        options=sorted(df["MÊS"].dropna().unique()),
        default=sorted(df["MÊS"].dropna().unique())
    )

    # -------------------------------
    # Aplicar filtros
    # -------------------------------
    df_filtrado = df[
        (df["DES_FORNECEDOR"].isin(fornecedor)) &
        (df["NIVEL"].isin(nivel)) &
        (df["MÊS"].isin(mes))
    ]

    # -------------------------------
    # KPIs
    # -------------------------------
    st.subheader("Resumo Geral")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total de Pedidos",
        df_filtrado["PEDIDO"].nunique()
    )

    col2.metric(
        "Total de Artigos",
        df_filtrado["ARTIGO"].nunique()
    )

    col3.metric(
        "Qtd Total Pedido",
        f'{df_filtrado["QTD PEDIDO"].sum():,.0f}'
    )

    # -------------------------------
    # GRÁFICO 1 - Pedidos por Mês
    # -------------------------------
    st.subheader("Pedidos por Mês")

    pedidos_mes = (
        df_filtrado.groupby("MÊS")["PEDIDO"]
        .nunique()
        .reset_index()
    )

    fig1, ax1 = plt.subplots()
    ax1.bar(
        pedidos_mes["MÊS"],
        pedidos_mes["PEDIDO"]
    )
    ax1.set_xlabel("Mês")
    ax1.set_ylabel("Quantidade de Pedidos")
    ax1.set_title("Pedidos por Mês")

    st.pyplot(fig1)

    # -------------------------------
    # GRÁFICO 2 - Top Fornecedores
    # -------------------------------
    st.subheader("Top 10 Fornecedores")

    fornecedor_qtd = (
        df_filtrado.groupby("DES_FORNECEDOR")["QTD PEDIDO"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    fornecedor_qtd.plot(
        kind="bar",
        ax=ax2
    )
    ax2.set_ylabel("Qtd Pedido")
    ax2.set_title("Top 10 Fornecedores")

    st.pyplot(fig2)

    # -------------------------------
    # Exportação
    # -------------------------------
    st.subheader("Exportar Dados Filtrados")

    csv = df_filtrado.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="ߓ堂aixar CSV",
        data=csv,
        file_name="relatorio_filtrado.csv",
        mime="text/csv"
    )

else:
    st.info("Faça o upload da planilha para visualizar o dashboard.")
