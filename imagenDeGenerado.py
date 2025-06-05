from gpt4all import GPT4All
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
import random

# Generar texto via LLM
llm="Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf" #llm a usar
prompt="genera un texto periodístico sobre las dimensiones de los campos de juego en los deportes de equipo más populares"


model = GPT4All(llm) # descarga o carga el LLM especificado en llm
texto=""
with model.chat_session():
    texto=model.generate(prompt, temp=0.94,max_tokens=860) #temperatura=0.94 para "creatividad" y menor repetición

print("generando...")
print(texto)

os.chdir("/home/seretur/Documentos/Investigacion/Preparadas/") #CAMBIAR ESTA LÌNEA!!!!

# Crear el nombre de la carpeta
nombre_carpeta = texto[:2] + texto[-6:-1]

# Crear la carpeta si no existe
os.makedirs(nombre_carpeta, exist_ok=True)

# Crear la imagen con Pillow. DEBE TENER NOMBRE DE ARCHIVO Y DE CARPETA
def creaImagen(texto, nombre_carpeta,nombre_archivo):
    # Configurar dimensiones y estilo de la imagen
    ancho_imagen, alto_imagen = 1586, 2244  #Proporción compatible con A4
    color_fondo = (255, 255, 255)
    color_texto = (0, 0, 0)
    margen=15 #espacio que dejarà a cada lado del texto
    ruta_fuente = None  # Usa fuente predeterminada

    # Crear una imagen en blanco
    imagen = Image.new('RGB', (ancho_imagen, alto_imagen), color_fondo)
    dibujo = ImageDraw.Draw(imagen)

    # Fuente y tamaño
    try:
        fuente = ImageFont.truetype("Arial.ttf", 28)  # Arial es suficientemente común
    except:
        fuente = ImageFont.load_default()

    # Calcular altura de línea para el interlineado
    linea_altura = fuente.getbbox("Ay")[3] # Altura aproximada de una línea

    # Área útil para texto
    area_ancho = ancho_imagen - 2 * margen
    lineas = textwrap.wrap(texto, width=int(area_ancho / fuente.getlength("a")))

    # Posición inicial (margen superior e izquierdo)
    pos_y = 3*margen #Margen superior

    for linea in lineas:
        dibujo.text((margen, pos_y), linea, font=fuente, fill=color_texto)
        pos_y += linea_altura+int(linea_altura*0.05)  # Avanzar a la siguiente línea

    # Guardar imagen
    ruta_archivo = os.path.join(nombre_carpeta, nombre_archivo + ".png")
    imagen.save(ruta_archivo)

    print(f"Imagen guardada en: {ruta_archivo}")
    
# función para devolver un texto con un dígito aleatorio modificado
def reemplazar_digito(texto):
    # Encontrar todas las posiciones donde hay dígitos
    posiciones_digitos = [i for i, c in enumerate(texto) if c.isdigit()]
    
    if not posiciones_digitos:
        return texto  # No hay dígitos para reemplazar
    
    # Elegir una posición al azar
    pos = random.choice(posiciones_digitos)
    digito_original = texto[pos]
    
    # Calcular el reemplazo
    if digito_original == '9':
        nuevo_digito = '0'
    else:
        nuevo_digito = str(int(digito_original) + 1)
    
    # Construir la nueva cadena
    texto_modificado = texto[:pos] + nuevo_digito + texto[pos+1:]
    
    return texto_modificado

creaImagen(texto,nombre_carpeta,nombre_carpeta)
textoAlterado=reemplazar_digito(texto)
creaImagen(textoAlterado,nombre_carpeta,nombre_carpeta+'Alterado')