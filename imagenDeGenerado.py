from gpt4all import GPT4All
from PIL import Image, ImageDraw, ImageFont
import os

# Generar texto via LLM
model = GPT4All("Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf") # downloads / loads a LLM
texto=""
with model.chat_session():
    # print(model.generate("Escribe un resumen en español sobre los umbrales climàticos que no deberían superarse para que el calentamiento global no sea irreversible", max_tokens=1024))
    texto=model.generate("genera un texto descriptivo acerca del campo climático en el mundo, señalando posibles umbrales de temperatura", temp=0.8,max_tokens=860)

print("generando...")
print(texto)

# Crear el nombre de la carpeta
nombre_carpeta = texto[:3] + texto[-4:]

# Crear la carpeta si no existe
os.makedirs(nombre_carpeta, exist_ok=True)

# Configurar dimensiones y estilo de la imagen
ancho, alto = 1024, 1314
color_fondo = (255, 255, 255)
color_texto = (0, 0, 0)
ruta_fuente = None  # Usa fuente predeterminada

# Crear una imagen en blanco
imagen = Image.new('RGB', (ancho, alto), color_fondo)
dibujo = ImageDraw.Draw(imagen)

# Fuente y tamaño
try:
    fuente = ImageFont.truetype("arial.ttf", 20)  # Puedes cambiar a otra fuente si la tienes
except:
    fuente = ImageFont.load_default()

# Posición del texto (centrado aproximadamente)
text_bbox = dibujo.textbbox((0, 0), texto, font=fuente)
text_ancho = text_bbox[2] - text_bbox[0]
pos_x = (ancho - text_ancho) // 2
pos_y = (alto - text_bbox[3]) // 2

# Dibujar el texto
dibujo.text((pos_x, pos_y), texto, fill=color_texto, font=fuente)

# Guardar la imagen en la nueva carpeta
ruta_archivo = os.path.join(nombre_carpeta, nombre_carpeta + ".png")
imagen.save(ruta_archivo)

print(f"Imagen guardada en: {ruta_archivo}")

