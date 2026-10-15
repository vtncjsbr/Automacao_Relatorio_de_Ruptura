import pandas as pd
from pathlib import Path
from img_to_text import imagem_para_texto
from date import pegar_data_no_relatorio


def extract_transform_load(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo)
    df['Informou_no_grupo'] = ''
    df['preço total'] = df['preço'] * df['Quantidade Rupturada']
    df = df[['Data','job_number','produto_original','sku_original','preço', 'Quantidade Rupturada','preço total','Colaborador','Informou_no_grupo']]
 
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

    soma_total = df['preço total'].sum()
    soma_formatada = (f'R${soma_total:,.2f} perdidos')

    porcentagem_informou_sim = '=TEXT(COUNTIF(I2:I{}, "sim")/COUNTA(I2:I{}), "0%")'.format(len(df)+1, len(df)+1)
    porcentagem_informou_nao = '=TEXT(COUNTIF(I2:I{}, "não")/COUNTA(I2:I{}), "0%")'.format(len(df)+1, len(df)+1)

    nova_linha_soma = pd.DataFrame([{
        'sku_original':'Total',
        'preço' : soma_formatada,
        'Colaborador':'Informaram',
        'Informou_no_grupo': porcentagem_informou_sim
    }])
    nova_linha_informaram = pd.DataFrame([{
        'Colaborador':'Não informaram',
        'Informou_no_grupo': porcentagem_informou_nao
    }])

    df = pd.concat([df, nova_linha_soma, nova_linha_informaram], ignore_index=True)

    caminho_downloads = Path.home() / 'Downloads'
    nome_do_arquivo = caminho_downloads / f'Relatório_de_Ruptura_{pegar_data_no_relatorio(df)}.xlsx'


    lista_sku = imagem_para_texto()
    contagem_sku_df = df['sku_original'].value_counts()
    aux_informou = {}

    for sku, qtd in contagem_sku_df.items():
        if sku not in lista_sku:
            aux_informou[sku] = 'não'
        
        elif lista_sku[sku] == qtd:
            aux_informou[sku] = 'sim'
        
        elif lista_sku[sku] < qtd:
            aux_informou[sku] = 'VERIFICAR QUEM ENVIOU'

    df.loc[df.index[:-2], 'Informou_no_grupo'] = (
    df.loc[df.index[:-2], 'sku_original'].map(aux_informou))

    return df, nome_do_arquivo


def style(df, nome_do_arquivo):
    with pd.ExcelWriter(nome_do_arquivo, engine='xlsxwriter') as writer:
    
        df.to_excel(writer, sheet_name='Planilha', index=False)

        workbook = writer.book
        worksheet = writer.sheets['Planilha']

        formato_cabecalho = workbook.add_format({
            'bg_color': '#729fcf',     
            'font_color': "#000000",     
            'bold': True,  
            'align': 'center', 
            'valign': 'vcenter', 
            'border': 1 
        })
        
        formato_planilha = workbook.add_format({
            'border': 1,
            'valign': 'vcenter',
            'align': 'left',
        }) 

        worksheet.set_column(
            0, 
            len(df.columns)-1, 
            None, 
            formato_planilha 
        )

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, formato_cabecalho)

        impar = workbook.add_format({'bg_color':'#729fcf'})
        par = workbook.add_format({'bg_color':'#ffffff'})
        
        worksheet.conditional_format(
            1,
            0, 
            len(df), 
            len(df.columns)-1, 
        {
            'type': 'formula',
            'criteria': '=MOD(ROW(),2)=0',
            'format': par
        })
    
        worksheet.conditional_format(
            1, 
            0, 
            len(df), 
            len(df.columns)-1, 
        {
            'type': 'formula', 
            'criteria': '=MOD(ROW(),2)=1', 
            'format': impar
        })