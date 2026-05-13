from tkinter.filedialog import askopenfilename
import pandas as pd
from pathlib import Path

caminho_arquivo = askopenfilename(title='Selecione o arquivo de Ruptura')

arquivo = pd.read_excel(caminho_arquivo)
filtrar = arquivo[['Data','job_number','produto_original','sku_original','preço', 'Quantidade Rupturada','Colaborador']].copy()

filtrar['preço'] = pd.to_numeric(filtrar['preço'], errors='coerce')

filtrar['preço'] = filtrar['preço'] * filtrar['Quantidade Rupturada']

soma_total = filtrar['preço'].sum()
soma_formatada = (f'R${soma_total:,.2f} perdidos')

filtrar['Informou_no_grupo'] = ''

porcentagem_informou_sim = ('=TEXTO(CONT.SE(H2:H{};"sim")/CONT.VALORES(H2:H{});"0%")'.format(len(filtrar)+1, len(filtrar)+1))
porcentagem_informou_nao = ('=TEXTO(CONT.SE(H2:H{};"não")/CONT.VALORES(H2:H{});"0%")'.format(len(filtrar)+1, len(filtrar)+1))

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

resultado_final = pd.concat([filtrar, nova_linha_soma, nova_linha_informaram], ignore_index=True)

def pegar_data_no_relatorio():
    coleta_data = filtrar
    coleta_data["Data"] = pd.to_datetime(coleta_data["Data"]) 
    data_texto = coleta_data['Data'].iloc[0].date()  
    dia = data_texto.day
    mes = data_texto.month
    ano = data_texto.year
    data_formatada = (f"{dia}-{mes}-{ano}")
    return data_formatada

df = resultado_final

caminho_downloads = Path.home() / 'Downloads'
nome_do_arquivo = caminho_downloads / f'Relatório_de_Ruptura_{pegar_data_no_relatorio()}.xlsx'

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