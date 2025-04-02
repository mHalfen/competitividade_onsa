import pandas as pd
import streamlit as st
import plotly.express as px
import mysql.connector
import os
from queries import query_shopping, query_sales, query_regular_sale, query_skus_scan
from filters import apply_filter_desemp, apply_filter_clicksuper, apply_filter_scann
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(layout="wide")

def get_conn():
    return mysql.connector.connect(
        host = os.getenv('host'),
        user = os.getenv('user'),
        password = os.getenv('password'),
        database = os.getenv('database')
        )

def execute_query(query, conn):
    conn.ping(reconnect=True)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return pd.DataFrame(result)

@st.cache_data
def get_data(query):
    conn = get_conn()
    df = execute_query(query, conn)
    conn.close()
    return df

@st.cache_data
def get_data_scanntech():
    dataset_scan = os.getenv('export_data')
    dataset_parquet = 'scan.parquet'

    if os.path.exists(dataset_parquet):
        return pd.read_parquet(dataset_parquet)
    
    df_scan = pd.read_excel(dataset_scan, sheet_name='db_ata')
    df_scan.to_parquet(dataset_parquet)
    return df_scan

yesterday = (datetime.now() - timedelta(days=1)).date()
yesterday_formatted = yesterday.strftime("%d/%m/%Y")

col1, col2 = st.columns(2)
col1.title('Análise de Pricing')
select_date = col2.date_input("Periodo da anáise:", value=[yesterday, yesterday], format="DD/MM/YYYY")
if len(select_date) == 2:
    start_date, end_date = select_date
    df_query = query_shopping(start_date, end_date)
    df_sales_query = query_sales(start_date, end_date)
    df = get_data(df_query)
    df_sales = get_data(df_sales_query)
else:
    df_query = query_shopping(yesterday, yesterday)
    df_sales_query = query_sales(yesterday, yesterday)
    df = get_data(df_query)
    df_sales = get_data(df_sales_query)

tab1, tab2, tab3 = st.tabs(['Desempenho - Click Super', 'Competitividade (Click Super)', 'Competitividade (Scanntech)'])

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

    df = apply_filter_desemp(df)

    searched_items = df.groupby('Conc')['Codigo'].nunique().reset_index()
    searched_items.columns = ['Concorrente', 'Itens pesquisados']
    
    fig_search_items = px.bar(
        searched_items,
        x='Concorrente',
        y='Itens pesquisados',
        color='Concorrente',
        title='Itens pesquisados por concorrente:',
        text_auto=True)
    
    fig_search_items.update_layout(xaxis_title="Concorrente", yaxis_title="Itens pesquisados")

    st.plotly_chart(fig_search_items)

    col8, col9 = st.columns(2)
    with col8:
        searched_date = df.groupby('Data_coleta')['Codigo'].nunique().reset_index()
        searched_date.columns = ['Data_coleta', 'Itens pesquisados']

        fig_search_date = px.area(
            searched_date,
            x='Data_coleta',
            y='Itens pesquisados',
            title='Itens pesquisados no periodo:'
        )

        st.plotly_chart(fig_search_date)

    with col9:
        searched_deptos = df.groupby('Depto')['Codigo'].nunique().reset_index()
        searched_deptos.columns = ['Depto', 'Itens pesquisados']

        searched_total = searched_deptos['Itens pesquisados'].sum()

        searched_deptos['Peso'] = ((searched_deptos['Itens pesquisados'] / searched_total ) * 100).round(2)

        fig_search_depto = px.pie(
            searched_deptos, 
            values='Peso', 
            names='Depto',
            title='Divisão por departamento:')
        
        fig_search_depto.update_traces(textinfo='percent', textposition='inside')

        st.plotly_chart(fig_search_depto)

    st.subheader('Coleta detalhada:')
    st.dataframe(df, use_container_width=True)

with tab2:
    df_regular_sale = get_data(query_regular_sale())

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

        df_merged = df_merged.query(
            "(Conc == 'PERUZZO BAG' and Loja == '007') or "
            "(Conc == 'PERUZZO DP' and Loja == '008') or "
            "(Conc == 'PERUZZO PEL' and Loja == '010') or "
            "(Conc == 'PERUZZO CAP' and Loja == '014') or "
            "(Conc == 'PERUZZO SGB' and (Loja == '015' or Loja == '017')) or "
            "(Conc == 'GUANABARA PEL' and Loja == '010') or "
            "(Conc == 'STOK PEL' and Loja == '010') or "
            "(Conc == 'TRES LETRAS SGB' and (Loja == '015' or Loja == '017')) or "
            "(Conc == 'TREICHEL PEL' and Loja == '010')"
        )
        
        return df_merged
    
    df_merged = transform_merged(df_merged) #Retorno do shopping + preco de venda regular das lojas

    df_merged_filtered = apply_filter_clicksuper(df_merged)

    df_graph_praca = df_merged_filtered.groupby('Conc')['Index_comp'].mean().reset_index()
    df_graph_praca['Index_comp'] = df_graph_praca['Index_comp'].round(2)

    graph_praca = px.bar(df_graph_praca,
                        x='Conc',
                        y='Index_comp',
                        text='Index_comp',
                        color='Conc',
                        title='Indice por concorrente')

    df_graph_depto = df_merged_filtered.groupby('Depto')['Index_comp'].mean().reset_index()
    df_graph_depto['Index_comp'] = df_graph_depto['Index_comp'].round(2)

    graph_depto = px.bar(df_graph_depto, 
                    x="Depto", 
                    y="Index_comp",
                    text="Index_comp",
                    color="Depto",
                    title='Indice por departamento')
    
    st.plotly_chart(graph_depto, use_container_width=True)
    st.plotly_chart(graph_praca, use_container_width=True)

    df_rank_sec = df_merged_filtered.groupby('Secao')['Index_comp'].mean().reset_index()
    df_rank_sec['Index_comp'] = df_rank_sec['Index_comp'].round(2)

    df_rank_group = df_merged_filtered.groupby('Grupo')['Index_comp'].mean().reset_index()
    df_rank_group['Index_comp'] = df_rank_group['Index_comp'].round(2)

    df_rank_subgroup = df_merged_filtered.groupby('Subgrupo')['Index_comp'].mean().reset_index()
    df_rank_subgroup['Index_comp'] = df_rank_subgroup['Index_comp'].round(2)

    df_rank_forneced = df_merged_filtered.groupby('Fornecedor')['Index_comp'].mean().reset_index()
    df_rank_forneced['Index_comp'] = df_rank_forneced['Index_comp'].round(2)

    st.subheader('Ranking por seção mercadológica:')
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
    st.dataframe(df_merged_filtered, use_container_width=True)

with tab3:
    df_scan = get_data_scanntech()
    
    df_skus_query = query_skus_scan()
    df_skus = get_data(df_skus_query)

    def transform_scan_ata(df_scan):
        df_scan['data'] = pd.to_datetime(df_scan['data'], dayfirst=True, errors='coerce')
        df_scan['data'] = df_scan['data'].dt.strftime('%d/%m/%Y')
        df_scan['sku'] = df_scan['sku'].astype(str)
        df_scan['sku_desc'] = df_scan['sku_desc'].astype(str)
        df_scan['produto'] = (df_scan['sku'] + ' - ' + df_scan['sku_desc']).astype(str)
        df_scan['sku_fabric'] = df_scan['sku_fabric'].astype('category')
        df_scan['sku_marca'] = df_scan['sku_marca'].astype('category')
        df_scan['sku_cesta'] = df_scan['sku_cesta'].astype('category')
        df_scan['sku_categoria'] = df_scan['sku_categoria'].astype('category')
        df_scan['sku_sub_categoria'] = df_scan['sku_sub_categoria'].astype('category')
        df_scan['curva_grupo'] = df_scan['curva_grupo'].astype('category')
        df_scan['curva_mercado'] = df_scan['curva_mercado'].astype('category')
        df_scan['prc_moda_grupo'] = df_scan['prc_moda_grupo'].round(2)
        df_scan['giro_unit_grupo'] = df_scan['giro_unit_grupo'].round(2)
        df_scan['pdvs_grupo'] = (df_scan['pdvs_grupo'] * 100).round(2)
        df_scan['prc_moda_mercado'] = df_scan['prc_moda_mercado'].round(2)
        df_scan['giro_unit_mercado'] = df_scan['giro_unit_mercado'].round(2)
        df_scan['pdvs_mercado'] = (df_scan['pdvs_mercado'] * 100).round(2)
        df_scan['index_venda'] = (df_scan['index_venda'] * 100).round(2)
        df_scan['index_prc'] = (df_scan['index_prc'] * 100).round(2)

        return df_scan

    df_scan = transform_scan_ata(df_scan)

    df_merged_scan = pd.merge(df_skus, df_scan, on='sku')
    df_merged_scan = df_merged_scan[['data', 'Depto', 'tipo_loja', 'sku_marca', 'sku_sub_categoria', 'Fornecedor', 'produto', 
                                             'curva_grupo', 'curva_mercado', 'prc_moda_grupo', 'prc_moda_mercado', 'index_prc',
                                             'pdvs_grupo', 'pdvs_mercado', 'giro_unit_grupo', 'giro_unit_mercado']]
    
    df_merged_scan = apply_filter_scann(df_merged_scan)

    df_graph_prc = df_merged_scan.groupby(['Depto', 'tipo_loja'])['index_prc'].mean().reset_index()
    df_graph_prc['index_prc'] = df_graph_prc['index_prc'].round(2)

    df_scan_moda_ata = df_merged_scan[['produto', 'tipo_loja', 'prc_moda_grupo', 'prc_moda_mercado']]
    df_scan_moda_ata = df_scan_moda_ata[df_scan_moda_ata['tipo_loja'] == 'ATA']
    df_scan_moda_ata['index_moda'] = df_merged_scan['prc_moda_grupo']
    index_moda_ata = (df_scan_moda_ata['index_moda'].mean()).round(2)

    df_scan_giro_ata = df_merged_scan[['produto', 'tipo_loja', 'giro_unit_grupo', 'giro_unit_mercado']]
    df_scan_giro_ata = df_scan_giro_ata[df_scan_giro_ata['tipo_loja'] == 'ATA']
    df_scan_giro_ata['index_giro'] = ((df_merged_scan['giro_unit_grupo'] / df_merged_scan['giro_unit_mercado'] * 100)).round(2)
    index_giro_ata = (df_scan_giro_ata['index_giro'].mean()).round(2)

    df_scan_prc_ata = df_merged_scan[['produto', 'tipo_loja', 'index_prc']]
    df_scan_prc_ata = df_scan_prc_ata[df_scan_prc_ata['tipo_loja'] == 'ATA']
    index_prc_ata = (df_scan_prc_ata['index_prc'].mean()).round(2)

    df_scan_moda_var = df_merged_scan[['produto', 'tipo_loja', 'prc_moda_grupo', 'prc_moda_mercado']]
    df_scan_moda_var = df_scan_moda_var[df_scan_moda_var['tipo_loja'] == 'VAR']
    df_scan_moda_var['index_moda'] = df_merged_scan['prc_moda_grupo']
    index_moda_var = (df_scan_moda_var['index_moda'].mean()).round(2)

    df_scan_giro_var = df_merged_scan[['produto', 'tipo_loja', 'giro_unit_grupo', 'giro_unit_mercado']]
    df_scan_giro_var = df_scan_giro_var[df_scan_giro_var['tipo_loja'] == 'VAR']
    df_scan_giro_var['index_giro'] = ((df_merged_scan['giro_unit_grupo'] / df_merged_scan['giro_unit_mercado'] * 100)).round(2)
    index_giro_var = (df_scan_giro_var['index_giro'].mean()).round(2)

    df_scan_prc_var = df_merged_scan[['produto', 'tipo_loja', 'index_prc']]
    df_scan_prc_var = df_scan_prc_var[df_scan_prc_var['tipo_loja'] == 'VAR']
    index_prc_var = (df_scan_prc_var['index_prc'].mean()).round(2)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Indicadores - Atacado')
        m1, m2, m3 = st.columns(3)
        m1.metric(label='Indice médio de preço moda', value=index_moda_ata, border=True)
        m2.metric(label='Indice de giro', value=index_giro_ata, border=True)
        m3.metric(label='Indice de preço', value=index_prc_ata, border=True)

    with col2:
        st.subheader('Indicadores - Varejo')
        m4, m5, m6 = st.columns(3)
        m4.metric(label='Indice médio de preço moda', value=index_moda_var, border=True)
        m5.metric(label='Indice de giro', value=index_giro_var, border=True)
        m6.metric(label='Indice de preço', value=index_prc_var, border=True)

    graph_scan_prc = px.bar(df_graph_prc, 
                         x='Depto', 
                         y='index_prc',
                         text='index_prc',
                         color='tipo_loja',
                         title='Indice de competitividade:',
                         barmode='group')
    
    st.plotly_chart(graph_scan_prc, use_container_width=True)

    st.subheader('Coleta detalhada:')
    st.dataframe(df_merged_scan, use_container_width=True)

