# Automação do Relatório de Ruptura

Aplicação desktop (Windows) em Python que **automatiza o relatório diário de rupturas de produtos**: lê a planilha de rupturas, confere por OCR quais produtos foram avisados no grupo de WhatsApp, gera gráficos e um relatório Excel formatado, e ainda guarda o histórico em um banco de dados.

## Por que este projeto existe

Todo dia era preciso montar o relatório de rupturas na mão: somar o valor perdido, descobrir quais colaboradores avisaram o grupo sobre cada produto e montar gráficos. Este projeto reduz esse trabalho a **dois cliques**.

## O que ele faz

- Lê a planilha de ruptura (`.xlsx`) escolhida pelo usuário.
- Extrai o SKU dos prints do WhatsApp usando OCR (**Tesseract**) e preenche a coluna `Informou_no_grupo`.
- Calcula o `preço total` de cada ruptura (`preço × Quantidade Rupturada`).
- Adiciona ao final do relatório o **total perdido** e a **porcentagem** de quem informou e de quem não informou.
- Gera dois gráficos por colaborador: quantidade de produtos rupturados e valor perdido.
- Salva o relatório com formatação (cabeçalho colorido, bordas e linhas zebradas).
- Guarda o relatório finalizado em um banco **SQLite** para consultas futuras.

## Como funciona a coluna `Informou_no_grupo`

O código conta quantos prints de cada SKU existem na pasta de imagens e compara com quantas vezes o SKU aparece na planilha:

| Situação | Resultado |
|---|---|
| SKU não aparece em nenhum print | `não` |
| Nº de prints do SKU **=** nº de linhas do SKU na planilha | `sim` |
| Nº de prints do SKU **<** nº de linhas do SKU na planilha | `VERIFICAR QUEM ENVIOU` |

**Exemplo:** há 2 prints do SKU `12345`, mas a planilha tem 3 linhas desse SKU. Não dá para saber qual colaborador deixou de avisar, então essas linhas ficam marcadas com `VERIFICAR QUEM ENVIOU` para conferência manual.

> **Como o OCR lê o SKU:** em cada imagem, o programa pega o **primeiro número com 3 a 6 dígitos** encontrado no texto. Por isso, prints nítidos e recortados no produto funcionam melhor.

## Requisitos

- Windows
- Para o OCR funcionar, o **Tesseract-OCR** precisa estar baixado (veja o link em *Instalação*) e instalado **no mesmo caminho do arquivo `main.py`**, ou seja, a pasta `Tesseract-OCR` deve ficar ao lado do script.

## Instalação

- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

## Como usar

1. Execute o programa `main.py`. Na primeira execução, a pasta **`Arquivos Ruptura`** é criada na sua área de trabalho, com duas subpastas:
   - `Imagens whatsapp`: coloque aqui os prints dos produtos avisados no grupo.
   - `Gráficos Rupturas`: onde os gráficos serão salvos.
2. Copie os prints do WhatsApp para `Arquivos Ruptura/Imagens whatsapp`.
3. Clique em **Procurar Arquivo** e selecione a planilha de ruptura do dia.
4. Pegue o relatório gerado na pasta **Downloads**.
5. Confira as linhas marcadas com `VERIFICAR QUEM ENVIOU` e corrija à mão, se houver.
6. Com o relatório já revisado, clique em **Adicionar Banco de Dados** e selecione esse arquivo para salvá-lo no histórico.

## Planilha de entrada

A planilha precisa ter estas colunas (com estes nomes):

| Coluna | Descrição |
|---|---|
| `Data` | Data da ruptura |
| `job_number` | Número do pedido/job |
| `produto_original` | Nome do produto |
| `sku_original` | Código SKU do produto |
| `preço` | Preço unitário |
| `Quantidade Rupturada` | Quantidade que faltou |
| `Colaborador` | Quem registrou a ruptura |

Um exemplo está em `Ruptura_exemplo.xlsx`, e a pasta `imagens_produtos` traz prints de teste.

## O que é gerado

| Saída | Onde fica |
|---|---|
| Relatório Excel (`Relatório_de_Ruptura_<dia-mês-ano>.xlsx`) | Pasta **Downloads** |
| Gráfico de produtos rupturados por colaborador | `Arquivos Ruptura/Gráficos Rupturas` |
| Gráfico de valor rupturado por colaborador | `Arquivos Ruptura/Gráficos Rupturas` |
| Banco de dados `Rupturas.db` (tabela `Rupturas`) | `Arquivos Ruptura` |

> Ao adicionar ao banco, as **2 últimas linhas** do relatório (totais e porcentagens) são descartadas, pois não são registros de ruptura.

## Tecnologias

- **pandas**: leitura e tratamento da planilha
- **pytesseract + OpenCV**: OCR dos prints
- **tkinter**: interface gráfica
- **matplotlib**: gráficos
- **xlsxwriter**: formatação do relatório Excel
- **SQLite**: histórico das rupturas

## Limitações conhecidas

- Funciona apenas no Windows (caminhos e executável do Tesseract).
- O OCR pode errar em prints borrados ou com vários números; sempre revise o resultado.
- Registros são adicionados ao banco com `append`: adicionar o mesmo relatório duas vezes gera linhas duplicadas.