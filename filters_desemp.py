import streamlit as st

def date():
    select_date = st.date_input("Periodo da análise", [])
        
    return select_date

def depto(df):
    deptos = df['Depto'].unique() if not df.empty else []
    selected_deptos = st.multiselect('Departamento:', deptos)

    if selected_deptos:
        df = df[df['Depto'].isin(selected_deptos)]
    else:
        df = df

    return df

def ofert(df):
    ofert = st.multiselect("Em oferta?:", options=['S', 'N'], default=['S', 'N'], key='ofert_filter')
    df = df[df['Oferta'].isin(ofert)]

    return df

def section(df):
    sections = df['Secao'].unique() if not df.empty else []
    selected_section = st.multiselect('Secao:', sections)

    if selected_section:
        df = df[df['Secao'].isin(selected_section)]
    else:
        df = df

    return df

def group(df):
    groups = df['Grupo'].unique() if not df.empty else []
    selected_group = st.multiselect('Grupo:', groups)

    if selected_group:
        df = df[df['Grupo'].isin(selected_group)]
    else:
        df = df

    return df

def subgroup(df):
    subgroups = df['Subgrupo'].unique() if not df.empty else []
    selected_subgroup = st.multiselect('Subgrupo:', subgroups)

    if selected_subgroup:
        df = df[df['Subgrupo'].isin(selected_subgroup)]
    else:
        df = df

    return df
