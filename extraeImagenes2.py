import fitz

from tkinter import *
from tkinter import filedialog
import os

#elegir_ruta cuadro de diálogo para seleccionar el pdf cuyas imágenes se van a sacar
def elegir_ruta():
    raiz=Tk()
    raiz.withdraw
    global ruta;
    ruta_archivo = filedialog.askopenfilename(
        title="Seleccionar imagen pdf",
        filetypes=[("Archivos PDF", "*.pdf")])
    ruta=ruta_archivo
    raiz.destroy()

# Ruta a las imágenes
os.chdir("/home/seretur/Documentos")
ruta=os.getcwd()
elegir_ruta()



archivoBase=ruta
doc=fitz.open(archivoBase)

# directorio donde se escribirán las imágenes
rutaPura,nombreArchivo=os.path.split(ruta)
# cantImagenes=len(pdf_images)
nomDir=nombreArchivo[0:-4]
caminac=os.chdir(rutaPura)
if not os.path.exists(nomDir):
    os.mkdir(nomDir)
os.chdir(nomDir)

for numpagina in range(len(doc)):
    pagina=doc[numpagina]
    lista_imagenes=pagina.get_images()
    for image_index, img in enumerate(lista_imagenes, start=1): # Enumeramos páginas
        xref = img[0] # XREF de la imagen
        pix = fitz.Pixmap(doc, xref)
        if pix.n - pix.alpha > 3: # CMYK: convertimos a RGB
            pix = fitz.Pixmap(fitz.csRGB, pix)

        pix.save("page_%s-image_%s.png" % (numpagina, image_index)) # guardamos
        pix = None



print("analizada ruta: ",ruta)
print("Ruta normalizada: ",rutaPura, " archivo:",nombreArchivo)
print("Successfully converted PDF to images")