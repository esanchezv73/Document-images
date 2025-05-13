import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import imagehash
import os
import itertools

class ImageHashApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculador y Comparador de Hashes de Imágenes")
        self.image_paths = []

        # Botón para seleccionar imágenes
        self.select_button = tk.Button(root, text="Seleccionar hasta 4 imágenes", command=self.select_images)
        self.select_button.pack(pady=10)

        # Frame para mostrar miniaturas
        self.preview_frame = tk.Frame(root)
        self.preview_frame.pack()

        # Etiqueta para mostrar resultados
        self.result_label = tk.Label(root, text="", justify="left", font=("Courier", 10))
        self.result_label.pack(pady=10)

    def select_images(self):
        # Limpiar datos previos
        self.image_paths.clear()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        self.result_label.config(text="")

        # Abrir diálogo de selección múltiple
        filetypes = [("Imágenes", "*.png *.jpg *.jpeg")]
        paths = filedialog.askopenfilenames(title="Seleccionar imágenes", filetypes=filetypes)

        if not paths:
            return

        self.image_paths = list(paths)[:4]  # Limitar a 4 imágenes

        # Mostrar miniaturas
        self.show_previews()

        # Calcular y mostrar hashes + comparaciones
        self.calculate_and_compare_hashes()

    def show_previews(self):
        for idx, path in enumerate(self.image_paths):
            img = Image.open(path)
            img.thumbnail((120, 150))  # Miniatura
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(self.preview_frame, image=photo)
            label.image = photo  # Mantener referencia
            label.grid(row=0, column=idx, padx=5)

    def calculate_and_compare_hashes(self):
        result_text = ""
        hash_objects = []

        # Paso 1: Calcular hashes de cada imagen
        for idx, path in enumerate(self.image_paths):
            try:
                img = Image.open(path)

                avg_hash = imagehash.average_hash(img)
                phash = imagehash.phash(img)
                whash = imagehash.whash(img)

                # Guardar objetos hash para comparar después
                hash_objects.append({
                    'name': os.path.basename(path),
                    'avg': avg_hash,
                    'phash': phash,
                    'whash': whash
                })

                result_text += f"Imagen {idx+1}: {os.path.basename(path)}\n"
                result_text += f"  Average Hash : {avg_hash}\n"
                result_text += f"  Perceptual Hash: {phash}\n"
                result_text += f"  Wavelet Hash   : {whash}\n\n"

            except Exception as e:
                result_text += f"Error procesando {path}: {e}\n"

        # Paso 2: Comparar todas las combinaciones de imágenes (si hay al menos 2)
        if len(hash_objects) >= 2:
            result_text += "="*60 + "\n"
            result_text += "Comparación entre pares de imágenes:\n"
            result_text += "="*60 + "\n"

            for (i1, i2) in itertools.combinations(range(len(hash_objects)), 2):
                h1 = hash_objects[i1]
                h2 = hash_objects[i2]

                # Usamos una función auxiliar para calcular distancia de Hamming
                def hamming(a, b): return bin(int(str(a),16) ^ int(str(b),16)).count("1")

                avg_diff = hamming(h1['avg'], h2['avg'])
                phash_diff = hamming(h1['phash'], h2['phash'])
                whash_diff = hamming(h1['whash'], h2['whash'])

                result_text += f"{h1['name']} vs {h2['name']}:\n"
                result_text += f"  Diferencia Average Hash : {avg_diff}\n"
                result_text += f"  Diferencia Perceptual   : {phash_diff}\n"
                result_text += f"  Diferencia Wavelet      : {whash_diff}\n"
                result_text += "-"*60 + "\n"

        self.result_label.config(text=result_text)


if __name__ == "__main__":
    os.chdir("/home/seretur/Documentos")
    root = tk.Tk()
    root.geometry("600x450")
    app = ImageHashApp(root)
    root.mainloop()