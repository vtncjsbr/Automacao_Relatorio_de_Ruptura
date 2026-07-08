from tkinter.filedialog import askopenfilename
import pandas as pd
from pathlib import Path

try:
    caminho_arquivo = askopenfilename(title='Selecione o arquivo de Ruptura')
    def preparar_dataframe(caminho_arquivo):
        df = pd.read_excel(caminho_arquivo)
        df['Informou_no_grupo'] = ''
        df['preço total'] = ''
        df = df[['Data','job_number','produto_original','sku_original','preço', 'Quantidade Rupturada','preço total','Colaborador','Informou_no_grupo']]
        return df

    df = preparar_dataframe(caminho_arquivo)

    def tratar_dados(df):
        df['preço'] = pd.to_numeric(df['preço'], errors='coerce')
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        return df

    df = tratar_dados(df)

    def relatorio_sem_estilização(df):
        df['preço total'] = df['preço'] * df['Quantidade Rupturada']
        soma_total = df['preço total'].sum()
        soma_formatada = (f'R${soma_total:,.2f} perdidos')

        # Texto que vai virar uma fórmula na ultima linha + 1
        # A fórmula serve para retornar a porcentagem que informaram sim e não
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
        return df

    df = relatorio_sem_estilização(df)

    def pegar_data_no_relatorio(df):
        data_texto = df['Data'].iloc[0].date()  
        dia = data_texto.day
        mes = data_texto.month
        ano = data_texto.year
        data_formatada = (f"{dia}-{mes}-{ano}")
        return data_formatada

    caminho_downloads = Path.home() / 'Downloads'
    nome_do_arquivo = caminho_downloads / f'Relatório_de_Ruptura_{pegar_data_no_relatorio(df)}.xlsx'

    def estilizar_relatorio(df):
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

    estilizar_relatorio(df)
except FileNotFoundError as error:
    print(f"System Error: {error}")