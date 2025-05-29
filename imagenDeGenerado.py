from gpt4all import GPT4All
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

# Generar texto via LLM
model = GPT4All("Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf") # downloads / loads a LLM
texto=""
with model.chat_session():
    # print(model.generate("Escribe un resumen en español de hasta 400 palabras sobre los umbrales climàticos que no deberían superarse para que el calentamiento global no sea irreversible", max_tokens=1024))
    texto=model.generate("genera un texto descriptivo acerca del campo climático en el mundo, señalando posibles umbrales de temperatura", temp=0.8,max_tokens=860)

print("generando...")
print(texto)

# Crear el nombre de la carpeta
nombre_carpeta = texto[:3] + texto[-5:-1]

# Crear la carpeta si no existe
os.makedirs(nombre_carpeta, exist_ok=True)

# Configurar dimensiones y estilo de la imagen
ancho_imagen, alto_imagen = 1024, 1314
color_fondo = (255, 255, 255)
color_texto = (0, 0, 0)
margen=15 #espacio que dejarà a cada lado del texto
ruta_fuente = None  # Usa fuente predeterminada

# Crear una imagen en blanco
imagen = Image.new('RGB', (ancho_imagen, alto_imagen), color_fondo)
dibujo = ImageDraw.Draw(imagen)

# Fuente y tamaño
try:
    fuente = ImageFont.truetype("arial.ttf", 20)  # Arial es suficientemente común
except:
    fuente = ImageFont.load_default()

# Calcular altura de línea
linea_altura = fuente.getbbox("Ay")[3]  # Altura aproximada de una línea

# Área útil para texto
area_ancho = ancho_imagen - 2 * margen
lineas = textwrap.wrap(texto, width=int(area_ancho / fuente.getlength("a")))

# Posición inicial (margen superior e izquierdo)
pos_y = 3*margen #Margen superior

for linea in lineas:
    dibujo.text((margen, pos_y), linea, font=fuente, fill=color_texto)
    pos_y += linea_altura  # Avanzar a la siguiente línea

# Guardar imagen
ruta_archivo = os.path.join(nombre_carpeta, nombre_carpeta + ".png")
imagen.save(ruta_archivo)

print(f"Imagen guardada en: {ruta_archivo}")