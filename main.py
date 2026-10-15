from pathlib import Path
from platformdirs import user_desktop_dir
import tkinter as tk
from tkinter.filedialog import askopenfilename
from etl_and_style import extract_transform_load, style
from create_graph import criar_grafico_produtos_rupturados, criar_grafico_valor_rupturados
from create_db import criar_banco


def criar_pastas():
    desktop = user_desktop_dir()
    main = Path(desktop) / "Arquivos Ruptura"
    Path(main).mkdir(parents=True, exist_ok=True)

    caminho_img = main / 'Imagens whatsapp'
    Path(caminho_img).mkdir(parents=True, exist_ok=True)

    caminho_graficos = main / 'Gráficos Rupturas'
    Path(caminho_graficos).mkdir(parents=True, exist_ok=True)
criar_pastas()

def criar_relatorio():
    caminho_arquivo = askopenfilename(title='Selecione o arquivo de Ruptura', filetypes=[('Arquivo XLSX', '*.xlsx')])
    df, nome_do_arquivo = extract_transform_load(caminho_arquivo)
    style(df,nome_do_arquivo)
    criar_grafico_valor_rupturados(df.iloc[:-2])
    criar_grafico_produtos_rupturados(df.iloc[:-2])


################################################################# JANELA #################################################################

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