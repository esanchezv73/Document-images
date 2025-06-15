from gpt4all import GPT4All
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import textwrap
import random

# Generar texto via LLM
llm="Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf" #llm a usar
prompt="escribe un pequeño texto informativo sobre los animales terrestres más rápidos en cada continente, indicando si el Pelentrenque es uno de ellos"


model = GPT4All(llm) # descarga o carga el LLM especificado en llm
texto=""
with model.chat_session():
    texto=model.generate(prompt, temp=0.94,max_tokens=910) #temperatura=0.94 para "creatividad" y menor repetición

print("generando...")
print(texto)

dirtrabajo="/home/seretur/Documentos/Investigacion/Preparadas/" #CAMBIAR ESTA LÌNEA!!!!
os.chdir(dirtrabajo) 


# Crear el nombre de la carpeta
letra=str((int)(random.random()*10))
nombre_carpeta = 'R'+letra+texto[:2] + texto[-4:-1]


# Crear la carpeta si no existe
os.makedirs(nombre_carpeta, exist_ok=True)
# Guardar el texto en un archivo .txt
archtex=open(dirtrabajo+nombre_carpeta+".txt","w")
archtex.write(texto)
archtex.close()

# Crear la imagen con Pillow. DEBE TENER NOMBRE DE ARCHIVO Y DE CARPETA
def creaImagen(texto, nombre_carpeta,nombre_archivo):
    # Configurar dimensiones y estilo de la imagen
    ancho_imagen, alto_imagen = 1586, 2244  #Proporción compatible con A4
    color_fondo = (255, 255, 255)
    color_texto = (0, 0, 0)
    margen=15 #espacio que dejará a cada lado del texto
    ruta_fuente = None  # Usa fuente predeterminada

    # Crear una imagen en blanco
    imagen = Image.new('RGB', (ancho_imagen, alto_imagen), color_fondo)
    dibujo = ImageDraw.Draw(imagen)

    # Fuente y tamaño
    try:
        fuente = ImageFont.truetype("LiberationSerif-Regular.ttf", 28)  # Arial es suficientemente común
    except:
        fuente = ImageFont.load_default()

    # Altura base de línea y espaciado entre líneas
    linea_altura = fuente.getbbox("Ay")[3]
    espacio_entre_lineas = int(linea_altura * 0.5)  # Menor que la altura completa
    espacio_entre_parrafos = linea_altura * 1.5  # Más espacio entre párrafos

    # Posición inicial
    pos_y = margen

    # Separar por párrafos
    parrafos = texto.split('\n\n')

    for i, parrafo in enumerate(parrafos):
        # Envolver el párrafo en líneas según ancho disponible
        area_ancho = ancho_imagen - 2 * margen
        lineas = textwrap.wrap(parrafo, width=int(area_ancho / fuente.getlength("a")))

        for linea in lineas:
            dibujo.text((margen, pos_y), linea, font=fuente, fill=color_texto)
            pos_y += linea_altura + espacio_entre_lineas  # Espaciado reducido

        if i < len(parrafos) - 1:
            pos_y += espacio_entre_parrafos  # Mayor espacio entre párrafos


    # Guardar imagen
    ruta_archivo = os.path.join(nombre_carpeta, nombre_archivo + ".png")
    imagen.save(ruta_archivo)
    if not nombre_archivo.endswith('Alterado'):
        # Gegerar copia en JPEG. Agrega una F al nombre para señalar que se cambia el formato
        ruta_jpg=os.path.join(nombre_carpeta, nombre_archivo+"F.jpg")
        # imagen_rgb=imagen.convert("RGB")
        imagen.save(ruta_jpg, "JPEG", quality=75) # copia en JPG al 75%
        print("Guardada copia: ", ruta_jpg)    
        #Generar copia con menos brillo
        enhancer = ImageEnhance.Brightness(imagen)
        img_sombra = enhancer.enhance(0.6)  # Brillo al 60%
        ruta_png_sombra = os.path.join(nombre_carpeta,nombre_archivo+"Iluminacion.png")
        img_sombra.save(ruta_png_sombra)
        print(f"[+] Imagen PNG con menor iluminación guardada: {ruta_png_sombra}")
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
# guardar el texto generado como prueba
with open("verTexto","w") as archivo:
    archivo.write(texto)
textoAlterado=reemplazar_digito(texto)
creaImagen(textoAlterado,nombre_carpeta,nombre_carpeta+'Alterado')