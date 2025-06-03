import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import imagehash
import os
from datetime import datetime
import csv


class ImageHashApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Hashes de Imágenes")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        # Botón para seleccionar imágenes
        self.select_button = tk.Button(root, text="Seleccionar hasta 4 imágenes", command=self.select_images)
        self.select_button.pack(pady=10)

        # Frame para miniaturas
        self.preview_frame = tk.Frame(root)
        self.preview_frame.pack()

        # Etiqueta para mostrar resultados
        self.result_label = tk.Label(root, text="", justify="left", font=("Courier", 10))
        self.result_label.pack(pady=10)

        # Datos
        self.image_paths = []
        self.hash_objects = []

    def select_images(self):
        self.image_paths.clear()
        self.hash_objects.clear()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        self.result_label.config(text="")

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
            img.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(self.preview_frame, image=photo)
            label.image = photo
            label.grid(row=0, column=idx, padx=5)

    def calculate_and_compare_hashes(self):
        result_text = ""
        self.hash_objects = []

        for idx, path in enumerate(self.image_paths):
            try:
                img = Image.open(path)

                avg_hash = imagehash.average_hash(img)
                phash = imagehash.phash(img)
                dhash = imagehash.dhash(img)
                whash = imagehash.whash(img)

                self.hash_objects.append({
                    'name': os.path.basename(path),
                    'avg': avg_hash,
                    'phash': phash,
                    'dhash': dhash,
                    'whash': whash
                })

                result_text += f"Imagen {idx+1}: {os.path.basename(path)}\n"
                result_text += f"  Average Hash : {avg_hash}\n"
                result_text += f"  Perceptual Hash: {phash}\n"
                result_text += f"  Difference Hash: {dhash}\n"
                result_text += f"  Wavelet Hash   : {whash}\n\n"

            except Exception as e:
                result_text += f"Error procesando {path}: {e}\n"

        if len(self.hash_objects) >= 2:
            first_hash = self.hash_objects[0]
            result_text += "="*60 + "\n"
            result_text += f"Comparación contra la primera imagen: {first_hash['name']}\n"
            result_text += "="*60 + "\n"

            comparison_data = []

            for i in range(1, len(self.hash_objects)):
                h = self.hash_objects[i]

                def hamming(a, b): return bin(int(str(a), 16) ^ int(str(b), 16)).count("1")

                avg_diff = hamming(first_hash['avg'], h['avg'])
                phash_diff = hamming(first_hash['phash'], h['phash'])
                dhash_diff = hamming(first_hash['dhash'], h['dhash'])
                whash_diff = hamming(first_hash['whash'], h['whash'])

                comparison_data.append({
                    'index': i,
                    'name': h['name'],
                    'avg': avg_diff,
                    'phash': phash_diff,
                    'dhash': dhash_diff,
                    'whash': whash_diff
                })

                result_text += f"{h['name']} vs {first_hash['name']}:\n"
                result_text += f"  Diferencia Average Hash : {avg_diff}\n"
                result_text += f"  Diferencia Perceptual   : {phash_diff}\n"
                result_text += f"  Diferencia Difference   : {dhash_diff}\n"
                result_text += f"  Diferencia Wavelet      : {whash_diff}\n"
                result_text += "-"*60 + "\n"

            self.save_to_csv(comparison_data)

        self.result_label.config(text=result_text)

    def save_to_csv(self, comparison_data):
        """Guarda una sola fila con todas las comparaciones contra la primera imagen"""
        filename = "HashesPerceptuales.csv"

        now = datetime.now()
        timestamp_id = now.strftime("%Y%m%d_%H%M%S")
        timestamp_full = now.strftime("%Y-%m-%d %H:%M:%S")

        header = ['ID', 'Fecha']
        row = [timestamp_id, timestamp_full]

        first = self.hash_objects[0]
        header += ['Imagen1', 'Average1', 'Perceptual1', 'Difference1', 'Wavelet1']
        row += [first['name'], str(first['avg']), str(first['phash']), str(first['dhash']), str(first['whash'])]

        for comp in comparison_data:
            h = self.hash_objects[comp['index']]
            header += [f'Imagen{comp["index"]+1}']
            row += [h['name']]

            header += [f'Avg_1v{comp["index"]+1}']
            row += [comp['avg']]

            header += [f'Phash_1v{comp["index"]+1}']
            row += [comp['phash']]

            header += [f'Dhash_1v{comp["index"]+1}']
            row += [comp['dhash']]

            header += [f'Whash_1v{comp["index"]+1}']
            row += [comp['whash']]

        try:
            file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0

            with open(filename, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                if not file_exists:
                    writer.writerow(header)

                writer.writerow(row)

            print(f"Datos guardados en {filename}")
        except Exception as e:
            print("Error al guardar en CSV:", e)


if __name__ == "__main__":
    os.chdir("/home/seretur/Documentos") # Cambia al directorio donde se guardarán los archivos CSV
    root = tk.Tk()
    app = ImageHashApp(root)
    root.mainloop()