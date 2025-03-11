import streamlit as st

def depto_pond(df_merged):
    deptos = df_merged['Depto'].unique() if not df_merged.empty else []
    selected_deptos = st.multiselect('Departamentos', deptos)

    if selected_deptos:
        df_merged = df_merged[df_merged['Depto'].isin(selected_deptos)]
    else:
        df_merged = df_merged

    return df_merged

def section_pond(df_merged):
    secoes = df_merged['Secao'].unique() if not df_merged.empty else []
    selected_secao = st.multiselect('Secao', secoes)

    if selected_secao:
        df_merged = df_merged[df_merged['Secao'].isin(selected_secao)]

    else:
        df_merged = df_merged

    return df_merged

def group_pond(df_merged):
    gps = df_merged['Grupo'].unique() if not df_merged.empty else []
    selected_gp = st.multiselect('Grupos', gps)

    if selected_gp:
        df_merged = df_merged[df_merged['Grupo'].isin(selected_gp)]
    else:
        df_merged = df_merged

    return df_merged

def subgroup_pond(df_merged):
    subgp = df_merged['Subgrupo'].unique() if not df_merged.empty else []
    selected_subgp = st.multiselect('Subgrupos', subgp)

    if selected_subgp:
        df_merged = df_merged[df_merged['Subgrupo'].isin(selected_subgp)]
    else:
        df_merged = df_merged

    return df_merged

def forneced_pond(df_merged):
    forneced = df_merged['Fornecedor'].unique() if not df_merged.empty else []
    selected_forneced = st.multiselect('Fornecedor', forneced)

    if selected_forneced:
        df_merged = df_merged[df_merged['Fornecedor'].isin(selected_forneced)]
    else:
        df_merged = df_merged

    return df_merged

def loja_pond(df_merged):
    loja = df_merged['Loja'].unique() if not df_merged.empty else []
    selected_loja = st.multiselect('Loja', loja)

    if selected_loja:
        df_merged = df_merged[df_merged['Loja'].isin(selected_loja)]
    else:
        df_merged = df_merged

    return df_merged

def conc_pond(df_merged):
    conc = df_merged['Conc'].unique() if not df_merged.empty else []
    selected_conc = st.multiselect('Conc', conc)

    if selected_conc:
        df_merged = df_merged[df_merged['Conc'].isin(selected_conc)]
    else:
        df_merged = df_merged

    return df_merged

def ofert_pond(df_merged):
    ofert = df_merged['Oferta'].unique() if not df_merged.empty else []
    selected_ofert = st.multiselect('Em oferta?', ofert)

    if selected_ofert:
        df_merged = df_merged[df_merged['Oferta'].isin(selected_ofert)]
    else:
        df_merged = df_merged

    return df_merged