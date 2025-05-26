import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import imagehash
import os
import itertools
import csv
import matplotlib.pyplot as plt

class ImageHashApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculador y Comparador de Hashes de Imágenes")
        self.image_paths = []
        self.comparison_data = []  # Para almacenar datos para CSV y gráficos

        # Botón para seleccionar imágenes
        self.select_button = tk.Button(root, text="Seleccionar hasta 4 imágenes", command=self.select_images)
        self.select_button.pack(pady=10)

        # Botón para mostrar gráfico
        self.plot_button = tk.Button(root, text="Mostrar Gráfico de Distancias", command=self.plot_comparisons)
        self.plot_button.pack(pady=5)
        self.plot_button.config(state=tk.DISABLED)  # Inicia deshabilitado

        # Frame para miniaturas
        self.preview_frame = tk.Frame(root)
        self.preview_frame.pack()

        # Etiqueta para mostrar resultados
        self.result_label = tk.Label(root, text="", justify="left", font=("Courier", 10))
        self.result_label.pack(pady=10)

    def select_images(self):
        self.image_paths.clear()
        self.comparison_data.clear()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        self.result_label.config(text="")
        self.plot_button.config(state=tk.DISABLED)

        filetypes = [("Imágenes", "*.png *.jpg *.jpeg")]
        paths = filedialog.askopenfilenames(title="Seleccionar imágenes", filetypes=filetypes)

        if not paths:
            return

        self.image_paths = list(paths)[:4]

        self.show_previews()
        self.calculate_and_compare_hashes()

    def show_previews(self):
        for idx, path in enumerate(self.image_paths):
            img = Image.open(path)
            img.thumbnail((130, 150)) #Aquí va el tamaño de la miniatura a mostrar en la GUI
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(self.preview_frame, image=photo)
            label.image = photo
            label.grid(row=0, column=idx, padx=5)

    def calculate_and_compare_hashes(self):
        result_text = ""
        hash_objects = []

        for idx, path in enumerate(self.image_paths):
            try:
                img = Image.open(path)

                avg_hash = imagehash.average_hash(img)
                phash = imagehash.phash(img)
                whash = imagehash.whash(img)

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

        if len(hash_objects) >= 2:
            result_text += "="*60 + "\n"
            result_text += "Comparación entre pares de imágenes:\n"
            result_text += "="*60 + "\n"

            for (i1, i2) in itertools.combinations(range(len(hash_objects)), 2):
                h1 = hash_objects[i1]
                h2 = hash_objects[i2]

                # Calcular distancias usando .value
                def hamming(a, b): return bin(int(str(a),16) ^ int(str(b),16)).count("1")

                avg_diff = hamming(h1['avg'], h2['avg'])
                phash_diff = hamming(h1['phash'], h2['phash'])
                whash_diff = hamming(h1['whash'], h2['whash'])

                # Guardar datos para CSV y gráfico
                self.comparison_data.append({
                    'img1': h1['name'],
                    'img2': h2['name'],
                    'avg': avg_diff,
                    'phash': phash_diff,
                    'whash': whash_diff
                })

                result_text += f"{h1['name']} vs {h2['name']}:\n"
                result_text += f"  Diferencia Average Hash : {avg_diff}\n"
                result_text += f"  Diferencia Perceptual   : {phash_diff}\n"
                result_text += f"  Diferencia Wavelet      : {whash_diff}\n"
                result_text += "-"*60 + "\n"

            self.save_to_csv()
            self.plot_button.config(state=tk.NORMAL)

        self.result_label.config(text=result_text)

    def save_to_csv(self):
        """Guarda los datos de comparación en un archivo CSV"""
        filename = "HashVariations.csv"
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['Imagen1', 'Imagen2', 'AverageHash', 'PerceptualHash', 'WaveletHash'])
            if not os.path.exists(filename):
                writer.writeheader()
            for data in self.comparison_data:
                writer.writerow({
                    'Imagen1': data['img1'],
                    'Imagen2': data['img2'],
                    'AverageHash': data['avg'],
                    'PerceptualHash': data['phash'],
                    'WaveletHash': data['whash']
                })
        print(f"Datos guardados en {filename}")

    def plot_comparisons(self):
        """Muestra un gráfico de barras comparando las distancias por tipo de hash"""
        if not self.comparison_data:
            messagebox.showwarning("Sin datos", "No hay comparaciones para graficar.")
            return

        labels = [f"{d['img1']}-{d['img2']}" for d in self.comparison_data]
        avg_values = [d['avg'] for d in self.comparison_data]
        phash_values = [d['phash'] for d in self.comparison_data]
        whash_values = [d['whash'] for d in self.comparison_data]

        x = range(len(labels))

        plt.figure(figsize=(12, 6))
        bar_width = 0.25

        plt.bar(x, avg_values, width=bar_width, label='Average Hash', color='blue')
        plt.bar([p + bar_width for p in x], phash_values, width=bar_width, label='Perceptual Hash', color='green')
        plt.bar([p + 2 * bar_width for p in x], whash_values, width=bar_width, label='Wavelet Hash', color='orange')

        plt.xticks([p + bar_width for p in x], labels, rotation=45, ha='right')
        plt.ylabel('Distancia de Hamming')
        plt.title('Comparación de Distancias de Hash entre Pares de Imágenes')
        plt.legend()
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    os.chdir("/home/seretur/Documentos/") #Modificar según necesidad y sistema operativo
    root = tk.Tk()
    root.geometry("600x450") # Tamaño de la ventana
    app = ImageHashApp(root)
    root.mainloop()