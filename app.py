import streamlit as st
import pandas as pd
import plotly.express as px

pd.set_option("styler.render.max_elements", 2_000_000)

st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="🚀",
    layout="wide",
)

@st.cache_data
def carregar_dados(url):
    return pd.read_csv(url)

df = carregar_dados("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# Sidebar filtros
st.sidebar.header("Filtros de análise")
anos = sorted(df['ano'].unique())
senioridades = sorted(df['senioridade'].unique())
contratos = sorted(df['contrato'].unique())
tamanhos = sorted(df['tamanho_empresa'].unique())

anos_sel = st.sidebar.multiselect("Ano", anos, default=anos)
senioridades_sel = st.sidebar.multiselect("Senioridade", senioridades, default=senioridades)
contratos_sel = st.sidebar.multiselect("Tipo de Contrato", contratos, default=contratos)
tamanhos_sel = st.sidebar.multiselect("Tamanho da Empresa", tamanhos, default=tamanhos)

df_filtrado = df[
    (df['ano'].isin(anos_sel)) &
    (df['senioridade'].isin(senioridades_sel)) &
    (df['contrato'].isin(contratos_sel)) &
    (df['tamanho_empresa'].isin(tamanhos_sel))
]

# Cabeçalho com tamanho normal e alinhado
st.markdown(
    """
    <h1 style="text-align:center; font-weight:600; font-size:2.4rem; margin-bottom:0.25rem;">🚀 Dashboard de Análise de Salários na Área de Dados</h1>
    <p style="text-align:center; font-size:1rem; color:#555; margin-top:0; margin-bottom:1.5rem;">
    Explore os dados salariais nos últimos anos usando os filtros ao lado para ajustar sua análise.
    </p>
    """,
    unsafe_allow_html=True
)

# KPIs organizados
st.subheader("📊 Resumo dos Dados")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros filtrados", f"{len(df_filtrado):,}")
col2.metric("Salário médio (USD)", f"${df_filtrado['usd'].mean():,.2f}" if len(df_filtrado) else "N/A")
col3.metric("Cargos distintos", df_filtrado['cargo'].nunique())
col4.metric("Tamanhos empresa", df_filtrado['tamanho_empresa'].nunique())

st.markdown("---")

# Função para criar contêiner com borda leve e espaçamento
def grafico_box(titulo, func):
    st.markdown(
        f"""
        <div style="
            background-color: #fff;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 3px 8px rgb(0 0 0 / 0.12);
            margin-bottom: 1.5rem;
        ">
            <h3 style="margin-top:0; margin-bottom:0.75rem; font-weight:600;">{titulo}</h3>
        """, unsafe_allow_html=True)
    func()
    st.markdown("</div>", unsafe_allow_html=True)

# Gráficos
def graf_top_cargos():
    top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values().reset_index()
    fig = px.bar(top_cargos, x='usd', y='cargo', orientation='h', labels={'usd': 'Média Salarial (USD)', 'cargo': ''})
    fig.update_layout(margin=dict(l=80, r=20, t=10, b=40), height=380)
    st.plotly_chart(fig, use_container_width=True)

def graf_dist_salarios():
    fig = px.histogram(df_filtrado, x='usd', nbins=30, labels={'usd': 'Faixa Salarial (USD)'})
    fig.update_layout(margin=dict(l=40, r=20, t=10, b=40), height=380)
    st.plotly_chart(fig, use_container_width=True)

def graf_proporcao_remoto():
    remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
    remoto_contagem.columns = ['Tipo Trabalho', 'Quantidade']
    fig = px.pie(remoto_contagem, names='Tipo Trabalho', values='Quantidade', hole=0.5)
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(margin=dict(l=30, r=30, t=10, b=30), height=380)
    st.plotly_chart(fig, use_container_width=True)

def graf_salario_paises():
    df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
    if df_ds.empty:
        st.warning("Nenhum dado de Cientista de Dados no filtro atual.")
        return
    media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
    fig = px.choropleth(media_ds_pais, locations='residencia_iso3', color='usd', color_continuous_scale='rdylgn',
                        labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=380)
    st.plotly_chart(fig, use_container_width=True)

# Layout dos gráficos em colunas
st.subheader("Visualizações")
col1, col2 = st.columns(2)
with col1:
    grafico_box("Top 10 Cargos por Salário Médio", graf_top_cargos)
with col2:
    grafico_box("Distribuição de Salários", graf_dist_salarios)

col3, col4 = st.columns(2)
with col3:
    grafico_box("Proporção dos Tipos de Trabalho", graf_proporcao_remoto)
with col4:
    grafico_box("Salário Médio de Cientista de Dados por País", graf_salario_paises)

# Botão de download
st.markdown("---")
st.subheader("Exportar Dados Filtrados")
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Baixar CSV dos Dados Filtrados",
    data=csv,
    file_name="dados_filtrados.csv",
    mime="text/csv",
    use_container_width=True,
)

# Tabela detalhada com scroll e altura fixa
st.markdown("---")
st.subheader("Dados Detalhados")

st.dataframe(df_filtrado, height=400, use_container_width=True)
