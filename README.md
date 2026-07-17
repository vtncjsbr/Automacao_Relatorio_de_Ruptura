# Projeto Ruptura
## Objetivo
Economizar tempo na criação de relatório de rupturas de produtos que tinha que ser feito diariamente.

## Observações
Automação em python para gerar relatório de ruptura formatados em Excel.<br>
Arquivo "Ruptura_exemplo.xlsx" é a planilha que será usada como teste do código.<br>
A pasta **imagens_produtos** contém prints dos produtos cancelados que foram avisados em mensagens de whatsapp, elas devem ser armazenadas na pasta **Arquivos Ruptura/Imagens whatsapp** na área de trabalho que será criada ao executar o código a primeira vez. As imagens serão analisadas pelo **pytesseract** para serem extraídas os SKU que serão preenchidas automaticamente na coluna "Informou_no_grupo" com "sim" caso o SKU seja o mesmo da coluna "sku_original". Caso os SKU das prints acabem e tenha espaços vazios na coluna "Informou_no_grupo" é considerado que não foi informado no grupo e será marcado como "não". Será preenchido com "VERIFICAR QUEM ENVIOU" por exemplo: 2 prints do mesmo SKU na pasta, porém contém 3 SKU do mesmo produto na tabela, nesse caso, deve-se verificar qual dos colaboradores de fato não informou.  

## Ferramentas Principais
- pandas
- pytesseract
- tkinter
- matplotlib