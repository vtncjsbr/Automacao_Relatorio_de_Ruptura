def pegar_data_no_relatorio(df):
    data_texto = df['Data'].iloc[1].date()  
    dia = data_texto.day
    mes = data_texto.month
    ano = data_texto.year
    data_formatada = (f"{dia}-{mes}-{ano}")
    return data_formatada