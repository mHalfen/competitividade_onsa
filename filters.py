import streamlit as st

def date():
    select_date = st.date_input("Periodo da análise", [])
        
    return select_date

def date_scan():
    date = df_merged_scan['data'].unique() if not df_merged_scan.empty else []
    selected = st.multiselect('Data de análise - Scanntech', date)
    if selected:
        df_merged_scan = df_merged_scan[df_merged_scan['data'].isin(selected)]

    return df_merged_scan

def apply_filter_desemp(df):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        deptos = df['Depto'].unique() if not df.empty else []
        selected_deptos = st.multiselect('Departamento:', deptos)
        if selected_deptos:
            df = df[df['Depto'].isin(selected_deptos)]

    with col2:
        sections = df['Secao'].unique() if not df.empty else []
        selected_section = st.multiselect('Seção:', sections)
        if selected_section:
            df = df[df['Secao'].isin(selected_section)]

    with col3:
        groups = df['Grupo'].unique() if not df.empty else []
        selected_group = st.multiselect('Grupo:', groups)
        if selected_group:
            df = df[df['Grupo'].isin(selected_group)]

    with col4:
        subgroups = df['Subgrupo'].unique() if not df.empty else []
        selected_subgroup = st.multiselect('Subgrupo:', subgroups)
        if selected_subgroup:
            df = df[df['Subgrupo'].isin(selected_subgroup)]

    with col5:
        ofert = st.multiselect("Em oferta?:", options=['S', 'N'], default=['S', 'N'], key='ofert_filter')
        if ofert:
            df = df[df['Oferta'].isin(ofert)]

    return df

def apply_filter_clicksuper(df_merged):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        loja = df_merged['Loja'].unique() if not df_merged.empty else []
        selected_loja = st.multiselect('Loja', loja)
        if selected_loja:
            df_merged = df_merged[df_merged['Loja'].isin(selected_loja)]

    with col2:
        conc = df_merged['Conc'].unique() if not df_merged.empty else []
        selected_conc = st.multiselect('Concorrente', conc)
        if selected_conc:
            df_merged = df_merged[df_merged['Conc'].isin(selected_conc)]

    with col3:
        ofert = df_merged['Oferta'].unique() if not df_merged.empty else []
        selected_ofert = st.multiselect('Em oferta?', ofert)
        if selected_ofert:
            df_merged = df_merged[df_merged['Oferta'].isin(selected_ofert)]

    with col4:
        forneced = df_merged['Fornecedor'].unique() if not df_merged.empty else []
        selected_forneced = st.multiselect('Fornecedor', forneced)
        if selected_forneced:
            df_merged = df_merged[df_merged['Fornecedor'].isin(selected_forneced)]

    col6, col7, col8, col9 = st.columns(4)
    with col6:
        deptos = df_merged['Depto'].unique() if not df_merged.empty else []
        selected_deptos = st.multiselect('Departamentos', deptos)
        if selected_deptos:
            df_merged = df_merged[df_merged['Depto'].isin(selected_deptos)]

    with col7:
        secoes = df_merged['Secao'].unique() if not df_merged.empty else []
        selected_secao = st.multiselect('Secao', secoes)
        if selected_secao:
            df_merged = df_merged[df_merged['Secao'].isin(selected_secao)]

    with col8:
        gps = df_merged['Grupo'].unique() if not df_merged.empty else []
        selected_gp = st.multiselect('Grupos', gps)
        if selected_gp:
            df_merged = df_merged[df_merged['Grupo'].isin(selected_gp)]

    with col9:
        subgp = df_merged['Subgrupo'].unique() if not df_merged.empty else []
        selected_subgp = st.multiselect('Subgrupos', subgp)
        if selected_subgp:
            df_merged = df_merged[df_merged['Subgrupo'].isin(selected_subgp)]

    return df_merged

def apply_filter_scann(df_merged_scan):
    col1, col2, col3 = st.columns(3)

    with col1:
        date = df_merged_scan['data'].unique() if not df_merged_scan.empty else []
        selected = st.multiselect('Data de análise:', date)
        if selected:
            df_merged_scan = df_merged_scan[df_merged_scan['data'].isin(selected)]

    with col2:
        depto = df_merged_scan['Depto'].unique() if not df_merged_scan.empty else []
        selected = st.multiselect('Departamento:', depto)
        if selected:
            df_merged_scan = df_merged_scan[df_merged_scan['Depto'].isin(selected)]

    with col3:
        sub_categoria = df_merged_scan['sku_sub_categoria'].unique() if not df_merged_scan.empty else []
        selected = st.multiselect('Categoria:', sub_categoria)
        if selected:
            df_merged_scan = df_merged_scan[df_merged_scan['sku_sub_categoria'].isin(selected)]

    col1, col2 = st.columns(2)

    with col1:
        forneced = df_merged_scan['Fornecedor'].unique() if not df_merged_scan.empty else []
        selected = st.multiselect('Fornecedor:', forneced)
        if selected:
            df_merged_scan = df_merged_scan[df_merged_scan['Fornecedor'].isin(selected)]

    with col2:
        produto = df_merged_scan['produto'].unique() if not df_merged_scan.empty else []
        selected = st.multiselect('Produto:', produto)
        if selected:
            df_merged_scan = df_merged_scan[df_merged_scan['produto'].isin(selected)]

    return df_merged_scan