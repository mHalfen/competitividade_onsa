import pandas as pd
import streamlit as st
import plotly.express as px
import mysql.connector
import os
from queries import query_shopping, query_sales, query_regular_sale
from filters_desemp import depto, section, group, subgroup, ofert
from filters_merged import depto_pond, section_pond, group_pond, subgroup_pond, forneced_pond, loja_pond, conc_pond, ofert_pond
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(layout="wide")

conn = mysql.connector.connect(
    host = os.getenv('host'),
    user = os.getenv('root'),
    password = os.getenv('password'),
    database = os.getenv('database'))

def execute_query(query, conn):
    conn.ping(reconnect=True)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return pd.DataFrame(result)

yesterday = (datetime.now() - timedelta(days=1)).date()
yesterday_formatted = yesterday.strftime("%d/%m/%Y")

col1, col2 = st.columns(2)
col1.title('Análise de Competitividade - ONSA')
select_date = col2.date_input("Periodo da análise:", [], format="DD/MM/YYYY")
if len(select_date) == 2:
    start_date, end_date = select_date
    df_query = query_shopping(start_date, end_date)
    df_sales_query = query_sales(start_date, end_date)
    df = execute_query(df_query, conn)
    df_sales = execute_query(df_sales_query, conn)
else:
    st.warning(f"Nenhum período selecionado. Dados carregados de ontem - {yesterday_formatted}.")
    df_query = query_shopping(yesterday, yesterday)
    df_sales_query = query_sales(yesterday, yesterday)
    df = execute_query(df_query, conn)
    df_sales = execute_query(df_sales_query, conn)

tab1, tab2 = st.tabs(['Desempenho - Click Super', 'Analise comercial - Geral'])

with tab1:
    def transform_shopping(df):
        df['Data_coleta'] = pd.to_datetime(df['Data_coleta'])
        df['Data_coleta'] = df['Data_coleta'].dt.strftime('%d/%m/%y')
        df['Secao'] = df['Secao_cod'].astype(str) + ' - ' + df['Secao_desc']
        df['Grupo'] = df['Grupo_cod'].astype(str) + ' - ' + df['Grupo_desc']
        df['Subgrupo'] = df['Subgrupo_cod'].astype(str) + ' - ' + df['Subgrupo_desc']
        df['Oferta'] = df['Oferta'].astype('category')
        df = df.drop(columns=['Secao_cod', 'Secao_desc', 'Grupo_cod', 'Grupo_desc', 'Subgrupo_cod', 'Subgrupo_desc'])

        map_conc = {
            '1': 'PERUZZO BAG',
            '2': 'PERUZZO DP',
            '3': 'PERUZZO PEL',
            '4': 'PERUZZO CAP',
            '5': 'PERUZZO SGB',
            '6': 'GUANABARA PEL',
            '7': 'STOK PEL',
            '8': 'TRES LETRAS SGB',
            '17': 'TREICHEL PEL' 
        }
        df['Conc'] = df['Conc'].astype(str).map(map_conc)

        df = df[['Data_coleta', 'Depto', 'Secao', 'Grupo', 'Subgrupo', 'Fornecedor', 'Codigo', 'Descricao', 'Conc', 'Conc_preco', 'Oferta']]

        return df

    df = transform_shopping(df)  #Retorno do shopping + modelagem
    
    col1, col2, col3, col4, col5  = st.columns(5)

    with col1:
        df = depto(df)
    with col2:
        df = section(df)
    with col3:
        df = group(df)
    with col4:
        df = subgroup(df)
    with col5:
        df = ofert(df)

    searched_items = df.groupby('Conc')['Codigo'].nunique().reset_index()
    searched_items.columns = ['Concorrente', 'Itens pesquisados']
    
    fig_search_items = px.bar(
        searched_items,
        x='Concorrente',
        y='Itens pesquisados',
        color='Concorrente',
        text_auto=True)
    fig_search_items.update_layout(xaxis_title="Concorrente", yaxis_title="Itens pesquisados")

    st.subheader('Itens pesquisados por concorrente')
    st.plotly_chart(fig_search_items)

    col8, col9 = st.columns(2)
    with col8:
        st.subheader('Coleta detalhada:')
        st.dataframe(df, use_container_width=True)
    with col9:
        searched_deptos = df.groupby('Depto')['Codigo'].nunique().reset_index()
        searched_deptos.columns = ['Depto', 'Itens pesquisados']

        searched_total = searched_deptos['Itens pesquisados'].sum()

        searched_deptos['Peso'] = ((searched_deptos['Itens pesquisados'] / searched_total ) * 100).round(2)

        st.subheader('Pesquisa por departamento:')

        fig_search_depto = px.pie(
            searched_deptos, 
            values='Peso', 
            names='Depto')
        fig_search_depto.update_traces(textinfo='percent', textposition='inside')

        st.plotly_chart(fig_search_depto)

with tab2:
    df_regular_sale = execute_query(query_regular_sale(), conn)
    #df_sales_2024 = execute_query(query_sales_2024(), conn)

    def transform_sales(df_sales):
        df_sales['Data_mov'] = pd.to_datetime(df_sales['Data_mov'])
        df_sales['Data_mov'] = df_sales['Data_mov'].dt.strftime('%d/%m/%y')
        df_sales = df_sales[df_sales['Promocao'].isna() | (df_sales['Promocao'] == '')]
        df_sales['True_sale'] = df_sales['Loja_capt'] == df_sales['Loja']
        df_sales = df_sales.loc[df_sales['True_sale']]

        return df_sales

    df_sales = transform_sales(df_sales)

    df_merged = pd.merge(df, df_sales, on='Codigo')
    
    def transform_merged(df_merged):
        df_merged = df_merged[['Data_coleta', 'Depto', 'Secao', 'Grupo', 'Subgrupo', 'Fornecedor',
                      'Codigo', 'Descricao', 'Conc', 'Conc_preco', 'Oferta',
                      'Loja', 'Loja_venda_reg']]
        
        df_merged['Index_comp'] = ((df_merged['Loja_venda_reg'] / df_merged['Conc_preco']) * 100).round(2)
        
        return df_merged
    
    df_merged = transform_merged(df_merged) #Retorno do shopping + preco de venda regular das lojas

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df_merged = loja_pond(df_merged)
    with col2:
        df_merged = conc_pond(df_merged)
    with col3:
        df_merged = ofert_pond(df_merged)
    with col4:
        df_merged = forneced_pond(df_merged)

    col6, col7, col8, col9 = st.columns(4)
    with col6:
        df_merged = depto_pond(df_merged)
    with col7:
        df_merged = section_pond(df_merged)
    with col8:
        df_merged = group_pond(df_merged)
    with col9:
        df_merged = subgroup_pond(df_merged)

    df_graph_praca = df_merged.groupby('Conc')['Index_comp'].mean().reset_index()
    df_graph_praca['Index_comp'] = df_graph_praca['Index_comp'].round(2)

    graph_praca = px.bar(df_graph_praca,
                        x='Conc',
                        y='Index_comp',
                        text='Index_comp',
                        color='Conc',
                        title='Indice por concorrente')

    df_graph_depto = df_merged.groupby('Depto')['Index_comp'].mean().reset_index()
    df_graph_depto['Index_comp'] = df_graph_depto['Index_comp'].round(2)

    graph_depto = px.bar(df_graph_depto, 
                    x="Depto", 
                    y="Index_comp",
                    text="Index_comp",
                    color="Depto",
                    title='Indice por departamento')
    
    st.plotly_chart(graph_depto, use_container_width=True)
    st.plotly_chart(graph_praca, use_container_width=True)

    df_rank_sec = df_merged.groupby('Secao')['Index_comp'].mean().reset_index()
    df_rank_sec['Index_comp'] = df_rank_sec['Index_comp'].round(2)

    df_rank_group = df_merged.groupby('Grupo')['Index_comp'].mean().reset_index()
    df_rank_group['Index_comp'] = df_rank_group['Index_comp'].round(2)

    df_rank_subgroup = df_merged.groupby('Subgrupo')['Index_comp'].mean().reset_index()
    df_rank_subgroup['Index_comp'] = df_rank_subgroup['Index_comp'].round(2)

    df_rank_forneced = df_merged.groupby('Fornecedor')['Index_comp'].mean().reset_index()
    df_rank_forneced['Index_comp'] = df_rank_forneced['Index_comp'].round(2)

    st.subheader('Rankings')
    col10, col11, col12, col13 = st.columns(4)

    col10.markdown('Secao')
    col10.dataframe(df_rank_sec, use_container_width=True)

    col11.markdown('Grupo')
    col11.dataframe(df_rank_group, use_container_width=True)
    
    col12.markdown('Subgrupo')
    col12.dataframe(df_rank_subgroup, use_container_width=True)

    col13.markdown('Fornecedor')
    col13.dataframe(df_rank_forneced, use_container_width=True)

    st.subheader('Detalhada completa:')
    st.dataframe(df_merged, use_container_width=True)