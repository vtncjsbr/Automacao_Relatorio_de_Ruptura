import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilename
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image
import pytesseract 
import cv2
import sqlite3
from platformdirs import user_desktop_dir
########################################### Criar pastas ###########################################

def pasta_principal():
    desktop = user_desktop_dir()
    main = Path(desktop) / "Arquivos Ruptura"
    Path(main).mkdir(parents=True, exist_ok=True)
    return main
caminho_padrao = pasta_principal()

def criar_pasta_whatsapp_imagem(pasta = caminho_padrao):
    img = pasta / 'Imagens whatsapp'
    Path(img).mkdir(parents=True, exist_ok=True)
    return img
img = criar_pasta_whatsapp_imagem()

def criar_pasta_graficos(destino = caminho_padrao):
    destino_pasta = destino / 'Gráficos Rupturas'
    Path(destino_pasta).mkdir(parents=True, exist_ok=True)
    return destino_pasta
destino_pasta = criar_pasta_graficos()

########################################### Criar Planilha ###########################################

def criar_relatorio():
    caminho_arquivo = askopenfilename(title='Selecione o arquivo de Ruptura', filetypes=[('Arquivo XLSX', '*.xlsx')])

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

    ########################################### Extrair texto com pytesseract ###########################################

    def imagem_para_texto(pasta_prints = img): 
        caminho = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        # caminho = Path.cwd() / 'Tesseract-OCR' / 'tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = caminho

        lista_sku = {}

        for foto in pasta_prints.iterdir():
            foto = cv2.imread(foto)
            texto = pytesseract.image_to_string(foto)
            texto_formatado = texto.split(' ')
            texto_formatado = [item.replace('\n', ' ') for item in texto_formatado]
            texto_formatado = " ".join(texto_formatado).split(' ')

            for item in texto_formatado:
                try:
                    item = int(item)
                    if len(str(item)) >=3 and len(str(item)) <= 6:
                        lista_sku[item] = lista_sku.get(item,0) + 1
                        break
                except:
                    pass
        return lista_sku
    lista_sku = imagem_para_texto()

    ########################################### Preencher a coluna ['Informou_no_grupo'] se informou ou não ###########################################

    def preencher_coluna_informou(df_sql = df):

        contagem_sku_df = df_sql['sku_original'].value_counts()
        aux_informou = {}

        for sku, qtd in contagem_sku_df.items():
            if sku not in lista_sku:
                aux_informou[sku] = 'não'
            
            elif lista_sku[sku] == qtd:
                aux_informou[sku] = 'sim'
            
            elif lista_sku[sku] < qtd:
                aux_informou[sku] = 'VERIFICAR QUEM ENVIOU'
                
        df_sql['Informou_no_grupo'] = df_sql['sku_original'].map(aux_informou)
        return df_sql
    df_sql = preencher_coluna_informou()
    df = df.drop(columns=["Informou_no_grupo"])

    df = df.merge(
        df_sql[["Data","Informou_no_grupo"]],
        on='Data',
        how='left'
    )

    ########################################### Relatório antes de Estilizar ###########################################

    def relatorio_sem_estilização(df):
        df['preço total'] = df['preço'] * df['Quantidade Rupturada']
        df_sql = df
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
        return df, df_sql
    df, df_sql = relatorio_sem_estilização(df)

    def pegar_data_no_relatorio(df):
        data_texto = df['Data'].iloc[1].date()  
        dia = data_texto.day
        mes = data_texto.month
        ano = data_texto.year
        data_formatada = (f"{dia}-{mes}-{ano}")
        return data_formatada

    ########################################### Criar Gráficos ###########################################

    def criar_grafico_produtos_rupturados(df_sql, caminho_pasta = destino_pasta):
        fig, ax = plt.subplots(figsize=(10,6))
        contagem = df_sql['Colaborador'].value_counts()
        maior_valor = contagem.values.max()

        ax.bar(contagem.index, contagem.values)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.set_ylabel('Quantidade de Produtos Rupturadas')
        ax.set_xlabel('Colaborador')
        ax.set_yticks(range(0,maior_valor+2, 2))
        plt.savefig(f"{caminho_pasta}\Gráfico de Produtos Rupturados_{pegar_data_no_relatorio(df)}.png", dpi=300)
        plt.close(fig)

    def criar_grafico_valor_rupturados(df_sql, caminho_pasta = destino_pasta):
        fig, ax = plt.subplots(figsize=(10,6))
        agrupar = df_sql.groupby('Colaborador')['preço total'].sum().reset_index().sort_values(by='preço total', ascending=False)
        
        ax.bar(agrupar['Colaborador'], agrupar['preço total'])
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.set_xlabel('Colaborador')
        ax.set_ylabel('Preço Total')

        plt.savefig(f"{caminho_pasta}\Gráfico de Valor Rupturados_{pegar_data_no_relatorio(df)}.png", dpi=300)
        plt.close(fig)

    criar_grafico_produtos_rupturados(df_sql)
    criar_grafico_valor_rupturados(df_sql)

    ########################################### Estilizar Relatório ###########################################

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
    

########################################### Criar banco de dados sql ###########################################

def criar_banco(caminho = caminho_padrao):

    df_sql = askopenfilename(title='Selecione a ruptura finalizada', filetypes=[('Arquivo XLSX', '*.xlsx')])
    df_sql = pd.read_excel(df_sql)
    df_sql = df_sql.iloc[:-2]

    caminho_banco = caminho / 'Rupturas.db'
    conexao = sqlite3.connect(caminho_banco)

    df_sql.to_sql(
        name='Rupturas',
        con=conexao,
        if_exists='append', 
        index=False
    )

    conexao.close()

########################################### Criar janela ###########################################

janela = tk.Tk()
janela.title("Criar Ruptura")
janela.resizable(False, False)

mensagem = tk.Label(
    text='''Antes de Procurar Arquivo, coloque as imagens dos produtos na pasta: 
    (Arquivos Ruptura/Imagens whatsapp) que ja foi criada na área de trabalho''', font=('Arial', 14)
)
mensagem.grid(row=0, column=0, columnspan=2 ,sticky="nsew", pady=(5,5), padx=(5,5))

botao = tk.Button(text="Procurar Arquivo", command=criar_relatorio, font=('Arial', 14), background='#d1d1d1')
botao.grid(row=1,column=0,  pady=(5, 5))

botao_sql = tk.Button(text='Adicionar Banco de Dados',command=criar_banco, font=('Arial', 14), background='#d1d1d1')
botao_sql.grid(row=1, column=1)

janela.mainloop()