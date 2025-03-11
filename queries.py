def query_shopping(start_date, end_date): 
    return f"""
    SELECT 
        cad_secaooper.Departamento AS Depto, 
        cad_secaooper.SecaoOper AS Secao_cod, 
        cad_secaooper.Descricao AS Secao_desc, 
        cad_grupos.GRUPO AS Grupo_cod, 
        cad_grupos.DESCRICAO AS Grupo_desc, 
        cad_subgrupo.SUBGRUPO AS Subgrupo_cod, 
        cad_subgrupo.DESCRICAO AS Subgrupo_desc, 
        cad_mercador.ltMix AS Mix, 
        for_forneced.RAZAOSOCIA AS Fornecedor, 
        cad_mercador.CODIGOINT AS Codigo, 
        cad_mercador.DESCRICAO AS Descricao, 
        for_shopping.codconcorr AS Conc, 
        for_shopping.preco AS Conc_preco, 
        for_shopping.datacoleta AS Data_coleta, 
        for_shopping.em_promocao AS Oferta
    FROM cad_mercador
    INNER JOIN cad_subgrupo 
        ON cad_mercador.CHAVESUBGRUPO = cad_subgrupo.CHAVESUBGRUPO
    INNER JOIN cad_secaooper 
        ON cad_secaooper.SecaoOper = cad_mercador.SECAOOPE
    INNER JOIN cad_grupos 
        ON cad_grupos.GRUPO = cad_mercador.GRUPOMERC
    INNER JOIN for_shopping 
        ON for_shopping.codigoint = cad_mercador.CODIGOINT
    INNER JOIN for_forneced 
        ON for_forneced.Codigo = cad_mercador.codfornprincipal
    WHERE for_shopping.datacoleta BETWEEN '{start_date}' AND '{end_date}';
    """

def query_sales(start_date, end_date): 
    return f"""
    SELECT sig_captura.SiglaLoja AS Loja_capt,
    sig_captura.CODIGOINT AS Codigo,
	sig_captura.DtMovimento AS Data_mov, 
	sig_captura.codpromocao AS Promocao,
	cad_mercloja.LOJA AS Loja,
	cad_mercloja.VENDALOJA AS Loja_venda_reg
    FROM cad_mercador INNER JOIN sig_captura ON cad_mercador.CODIGOINT = sig_captura.CODIGOINT
	INNER JOIN cad_mercloja ON cad_mercador.CODIGOINT = cad_mercloja.CODIGOINT
    WHERE DtMovimento BETWEEN '{start_date}' AND '{end_date}'
    AND (cad_mercador.ltMix = 'A' OR cad_mercador.ltMix = 'S')
    AND SiglaLoja IN ("001", "007", "008", "010", "014", "015", "017")
    AND cad_mercloja.LOJA IN ("001", "007", "008", "010", "014", "015", "017");
    """



def query_regular_sale(): 
    return f"""
    SELECT cad_mercador.CODIGOINT, 
            cad_mercador.ltMix, 
            cad_mercador001.VENDALOJA AS Venda_001, 
            cad_mercador007.VENDALOJA AS Venda_007, 
            cad_mercador008.VENDALOJA AS Venda_008, 
            cad_mercador010.VENDALOJA AS Venda_010, 
            cad_mercador014.VENDALOJA AS Venda_014, 
            cad_mercador015.VENDALOJA AS Venda_015, 
            cad_mercador017.VENDALOJA AS Venda_017
    FROM cad_mercador017 INNER JOIN 
            (cad_mercador015 INNER JOIN 
            (cad_mercador014 INNER JOIN 
            (cad_mercador010 INNER JOIN 
            (cad_mercador008 INNER JOIN 
            (cad_mercador007 INNER JOIN 
            (cad_mercador001 INNER JOIN cad_mercador ON 
            cad_mercador001.CODIGOINT = cad_mercador.CODIGOINT) ON 
            cad_mercador007.CODIGOINT = cad_mercador.CODIGOINT) ON 
            cad_mercador008.CODIGOINT = cad_mercador.CODIGOINT) ON 
            cad_mercador010.CODIGOINT = cad_mercador.CODIGOINT) ON 
            cad_mercador014.CODIGOINT = cad_mercador.CODIGOINT) ON 
            cad_mercador015.CODIGOINT = cad_mercador.CODIGOINT) ON 
            cad_mercador017.CODIGOINT = cad_mercador.CODIGOINT
    """

#def query_sales_2024(): 
#    return f"""
#    SELECT 
#        CODIGOINT AS Codigo,
#        SUM(Quantidade) AS sum_qtde, 
#        SUM(Venda) AS sum_sale_value
#    FROM sig_captura AS cap
#    WHERE DtMovimento >= "2024-01-01" AND DtMovimento <= "2024-12-31"
#        AND SiglaLoja IN ("002", "003", "004", "005", "006", "007", "008", "009", "010", "012", "014", "015", "016")
#    GROUP BY CODIGOINT
#    """