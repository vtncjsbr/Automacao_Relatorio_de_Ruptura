from platformdirs import user_desktop_dir
from pathlib import Path
import pytesseract
import cv2


def imagem_para_texto(): 
    desktop = user_desktop_dir()
    caminho_prints = Path(desktop) / "Arquivos Ruptura" / "Imagens whatsapp"
    caminho_tesseract = Path.cwd() / 'Tesseract-OCR' / 'tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = caminho_tesseract

    lista_sku: dict[int, int] = {}

    for foto in caminho_prints.iterdir():
        imagem = cv2.imread(foto)
        texto = pytesseract.image_to_string(imagem)
        texto_formatado = texto.split(' ')
        texto_formatado = [item.replace('\n', ' ') for item in texto_formatado]
        texto_formatado = " ".join(texto_formatado).split(' ')

        for item in texto_formatado:
            try:
                numero = int(item)
                if len(str(numero)) >=3 and len(str(numero)) <= 6:
                    lista_sku[numero] = lista_sku.get(numero,0) + 1
                    break
            except:
                pass
    return lista_sku