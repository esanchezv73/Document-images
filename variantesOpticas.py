import sys
import os
from PIL import Image, ImageEnhance

def procesar_imagen(ruta_png):
    try:
        # Cargar la imagen original
        img = Image.open(ruta_png)
        if img.format != "PNG":
            print("El archivo no es una imagen PNG.")
            return

        nombre_base, _ = os.path.splitext(os.path.basename(ruta_png))
        directorio = os.path.dirname(ruta_png)

        # 1. Guardar JPG con sufijo 'Iluminacion' y calidad 75%
        img_rgb = img.convert("RGB")
        ruta_jpg = os.path.join(directorio, f"{nombre_base}Formato.jpg")
        img_rgb.save(ruta_jpg, "JPEG", quality=75)
        print(f"[+] Imagen JPG guardada: {ruta_jpg}")

        # 2. Ajustar brillo y guardar como PNG con el mismo nombre
        enhancer = ImageEnhance.Brightness(img)
        img_sombra = enhancer.enhance(0.6)  # Brillo al 60%
        ruta_png_sombra = os.path.join(directorio, f"{nombre_base}Iluminacion.png")
        img_sombra.save(ruta_png_sombra)
        print(f"[+] Imagen PNG con menor iluminación guardada: {ruta_png_sombra}")

    except FileNotFoundError:
        print("[-] Archivo no encontrado.")
    except Exception as e:
        print(f"[-] Ocurrió un error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python convertir_imagen.py <archivo.png>")
    else:
        archivo_png = sys.argv[1]
        procesar_imagen(archivo_png)