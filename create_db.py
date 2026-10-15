import pandas as pd
from tkinter.filedialog import askopenfilename
import sqlite3
from pathlib import Path
from platformdirs import user_desktop_dir


def criar_banco():
    desktop = user_desktop_dir()
    caminho_banco = Path(desktop) / "Arquivos Ruptura" / 'Rupturas.db'

    df = askopenfilename(title='Selecione a ruptura finalizada', filetypes=[('Arquivo XLSX', '*.xlsx')])
    df = pd.read_excel(df)
    df = df.iloc[:-2]

    conexao = sqlite3.connect(caminho_banco)

    df.to_sql(
        name='Rupturas',
        con=conexao,
        if_exists='append', 
        index=False
    )

    conexao.close()