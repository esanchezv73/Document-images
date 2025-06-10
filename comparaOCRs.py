import tkinter as tk
from tkinter import filedialog
from hashlib import sha256
from abc import ABC, abstractmethod
from easyocr import Reader
from PIL import Image
import os
import csv

# Patrón de diseño utilizado: Strategy

# -----------------------------
# Superclase Base: OCRProcessor
# -----------------------------
class OCRProcessor(ABC):
    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        """Método abstracto que debe ser implementado por subclases."""
        pass


# -----------------------------
# Implementación con EasyOCR
# -----------------------------
class EasyOCREngine(OCRProcessor):
    def __init__(self):
        self.reader = Reader(['en'])  # Puedes cambiar idioma si es necesario

    def extract_text(self, image_path: str) -> str:
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"No se encontró el archivo: {image_path}")
        
        result = self.reader.readtext(image_path, detail=0)
        return "\n".join(result)

# globales
directorio=os.chdir("/home/seretur/Documentos") # Cambia esto al directorio donde quieras trabajar

# -----------------------------
# Funciones auxiliares
# -----------------------------
def calcular_sha256(texto: str) -> str:
    return sha256(texto.encode('utf-8')).hexdigest()


def hamming_distance(hash1: str, hash2: str) -> int:
    """Calcula la distancia de Hamming entre dos hashes hexadecimales."""
    bin1 = bin(int(hash1, 16))[2:].zfill(256)
    bin2 = bin(int(hash2, 16))[2:].zfill(256)
    return sum(b1 != b2 for b1, b2 in zip(bin1, bin2))


def select_image_files(max_files=4):
    root = tk.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames(
        title="Selecciona hasta 4 imágenes",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
    )
    return list(files)[:max_files]


def guardar_resultados_csv(base_file, base_hash, distancias):
    filename = "hashesOCR.csv"
    fieldnames = ["ArchivoBase", "HashBase"] + [f"Distancia_{i+1}" for i in range(len(distancias))]

    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        row_data = {
            "ArchivoBase": os.path.basename(base_file),
            "HashBase": base_hash
        }

        for i, distancia in enumerate(distancias):
            row_data[f"Distancia_{i+1}"] = distancia

        writer.writerow(row_data)

    print(f"\n✅ Resultados guardados en '{filename}'")


# -----------------------------
# Función principal
# -----------------------------
def main():
    print("Selecciona las imágenes...")
    image_files = select_image_files(4)

    if not image_files:
        print("No se seleccionaron archivos.")
        return

    ocr_engine: OCRProcessor = EasyOCREngine()

    print("\nRealizando OCR...\n")
    texts = []
    for i, img in enumerate(image_files):
        print(f"Procesando imagen {i + 1}: {img}")
        text = ocr_engine.extract_text(img)
        texts.append(text)
        print(f"Texto extraído:\n{text}\n{'-' * 40}")

    print("\nCálculo de hash SHA256 y distancia de Hamming:\n")

    first_hash = calcular_sha256(texts[0])
    print(f"Hash SHA256 de la primera imagen:\n{first_hash}\n")

    distancias = []

    for i, current_text in enumerate(texts[1:], start=2):
        current_hash = calcular_sha256(current_text)
        distance = hamming_distance(first_hash, current_hash)
        distancias.append(distance)
        print(f"Imagen {i}:")
        print(f"  Hash SHA256: {current_hash}")
        print(f"  Distancia de Hamming respecto a la primera imagen: {distance}")
        print("-" * 60)

    # Guardar resultados en CSV
    guardar_resultados_csv(
        base_file=image_files[0],
        base_hash=first_hash,
        distancias=distancias
    )


if __name__ == "__main__":
    main()