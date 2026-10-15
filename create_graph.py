import matplotlib.pyplot as plt
from platformdirs import user_desktop_dir
from pathlib import Path
from date import pegar_data_no_relatorio


def criar_grafico_produtos_rupturados(df):
    desktop = user_desktop_dir()
    caminho_graficos = Path(desktop) / "Arquivos Ruptura" / "Gráficos Rupturas"

    fig, ax = plt.subplots(figsize=(10,6))
    contagem = df['Colaborador'].value_counts()
    maior_valor = contagem.values.max()

    ax.bar(contagem.index, contagem.values)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.set_ylabel('Quantidade de Produtos Rupturadas')
    ax.set_xlabel('Colaborador')
    ax.set_yticks(range(0,maior_valor+2, 2))
    plt.savefig(f"{caminho_graficos}/Gráfico de Produtos Rupturados_{pegar_data_no_relatorio(df)}.png", dpi=300)
    plt.close(fig)

def criar_grafico_valor_rupturados(df):
    desktop = user_desktop_dir()
    caminho_graficos = Path(desktop) / "Arquivos Ruptura" / "Gráficos Rupturas"

    fig, ax = plt.subplots(figsize=(10,6))
    agrupar = df.groupby('Colaborador')['preço total'].sum().reset_index().sort_values(by='preço total', ascending=False)
    
    ax.bar(agrupar['Colaborador'], agrupar['preço total'])
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.set_xlabel('Colaborador')
    ax.set_ylabel('Preço Total')

    plt.savefig(f"{caminho_graficos}/Gráfico de Valor Rupturados_{pegar_data_no_relatorio(df)}.png", dpi=300)
    plt.close(fig)