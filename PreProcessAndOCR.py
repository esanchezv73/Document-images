#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 09:50:07 2024

@author: seretur
"""

import cv2
# import imutils
import numpy as np
from tkinter import *
from tkinter import filedialog
import easyocr
import csv
import os


def elegir_ruta():
    raiz=Tk()
    raiz.withdraw
    global ruta;
    ruta_archivo = filedialog.askopenfilename(
        title="Seleccionar imagen JPG",
        filetypes=[("Archivos PNG", "*.png")])
    ruta=ruta_archivo
    raiz.destroy()

def ocr_stat(imagen):
    global lector
    resultado=lector.readtext(imagen,paragraph=False)
    sumaTasa=0
    nfilas=0
    for renglon in resultado:
        sumaTasa += renglon[2]
        nfilas+=1
    promedio=sumaTasa/nfilas
    if nfilas==0 :
        nfilas=1
    print ("Suma de las tasas: ",sumaTasa)
    print("tasa promedio: ",sumaTasa/nfilas)
    return promedio

ruta=None
os.chdir("/home/seretur/Documentos")
elegir_ruta()
lector=easyocr.Reader(["es"],gpu=False)

# cargar la imagen a tratar
imagen=cv2.imread(ruta,cv2.IMREAD_GRAYSCALE)

# OCR inicial. 
print("Valores iniciales: ")
promedioInicial=ocr_stat(imagen)

# Aplicar CLAHE, queda en imagen2
clahe=cv2.createCLAHE(clipLimit=5)
imagen2=clahe.apply(imagen)

print("Aplicando CLAHE")
promeCLAHE=ocr_stat(imagen2)

# máscara de desenfoque sobre imagen2, queda en sharpened

kernel = np.array([[0, -1, 0],[-1, 5, -1],[0, -1, 0]])
sharpened = cv2.filter2D(imagen2, -1, kernel)

print("Aplicando máscara de desenfoque")
promeSharpening=ocr_stat(sharpened)

# Binarización Otsu

gaussiano=cv2.GaussianBlur(sharpened, (5,5),0)
ret,binarizado=cv2.threshold(gaussiano,0,255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

#OCR final
print("Aplicando binarización OTSU")
promefinal= ocr_stat(binarizado)

#agregar valores a evolOCR.csv
with open('tasasOCR.csv',mode="a") as arcsv:
    #renglon=ruta+','+str(promedioInicial)+','+str(promeCLAHE)+','+str(promeSharpening)+','+str(promefinal)
    fila=[ruta,str(promedioInicial),str(promeCLAHE),str(promeSharpening),str(promefinal)]
    escritor=csv.writer(arcsv)
    escritor.writerow(fila)

ultima=binarizado
# definir el nombre de archivo a guardar
pospunto=ruta.find('.')
nombre=ruta[:pospunto]+'2.png'

# Juntar la imagen original y la última y guardarlas
res=np.hstack((imagen,ultima))
cv2.imwrite(nombre,res)
cv2.waitKey()
cv2.destroyAllWindows()

