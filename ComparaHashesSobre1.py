import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import imagehash
import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt


class ImageHashApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Hashes de Imágenes")
        self.root.geometry("600x600")      # ✅ Tamaño fijo de ventana
        self.root.resizable(False, False) # ✅ Bloquear redimensionamiento

        self.image_paths = []
        self.hash_objects = []

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
        self.hash_objects.clear()
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
                dhash = imagehash.dhash(img)          # ✅ Nuevo hash: dhash
                whash = imagehash.whash(img)

                self.hash_objects.append({
                    'name': os.path.basename(path),
                    'avg': avg_hash,
                    'phash': phash,
                    'dhash': dhash,   # ✅ Guardamos dhash
                    'whash': whash
                })

                result_text += f"Imagen {idx+1}: {os.path.basename(path)}\n"
                result_text += f"  Average Hash : {avg_hash}\n"
                result_text += f"  Perceptual Hash: {phash}\n"
                result_text += f"  Difference Hash: {dhash}\n"  # ✅ Mostramos dhash
                result_text += f"  Wavelet Hash   : {whash}\n\n"

            except Exception as e:
                result_text += f"Error procesando {path}: {e}\n"

        if len(self.hash_objects) >= 2:
            result_text += "="*60 + "\n"
            result_text += "Comparación solo contra la primera imagen:\n"
            result_text += "="*60 + "\n"

            first_hash = self.hash_objects[0]
            comparison_data = []

            for i in range(1, len(self.hash_objects)):
                h = self.hash_objects[i]

                # ✅ Usamos conversión hexadecimal para evitar errores
                def hamming(a, b): return bin(int(str(a), 16) ^ int(str(b), 16)).count("1")

                avg_diff = hamming(first_hash['avg'], h['avg'])
                phash_diff = hamming(first_hash['phash'], h['phash'])
                dhash_diff = hamming(first_hash['dhash'], h['dhash'])  # ✅ Comparación dhash
                whash_diff = hamming(first_hash['whash'], h['whash'])

                comparison_data.append({
                    'pair': f"1v{i+1}",
                    'avg': avg_diff,
                    'phash': phash_diff,
                    'dhash': dhash_diff,   # ✅ Guardamos diferencia dhash
                    'whash': whash_diff
                })

                result_text += f"{first_hash['name']} vs {h['name']}:\n"
                result_text += f"  Diferencia Average Hash : {avg_diff}\n"
                result_text += f"  Diferencia Perceptual   : {phash_diff}\n"
                result_text += f"  Diferencia Difference   : {dhash_diff}\n"  # ✅ Mostramos dhash diff
                result_text += f"  Diferencia Wavelet      : {whash_diff}\n"
                result_text += "-"*60 + "\n"

            self.save_to_csv(comparison_data)
            self.plot_button.config(state=tk.NORMAL)

        self.result_label.config(text=result_text)

    def save_to_csv(self, comparison_data):
        """Guarda una sola fila con todas las comparaciones contra la primera imagen"""
        filename = "Hashes.csv"

        now = datetime.now()
        timestamp_id = now.strftime("%Y%m%d_%H%M%S")
        timestamp_full = now.strftime("%Y-%m-%d %H:%M:%S")

        header = ['ID', 'Fecha']
        row = [timestamp_id, timestamp_full]

        # Información de la primera imagen
        first = self.hash_objects[0]
        header += ['Imagen1', 'Average1', 'Perceptual1', 'Difference1', 'Wavelet1']  # ✅ Agregamos Difference1
        row += [first['name'], str(first['avg']), str(first['phash']), str(first['dhash']), str(first['whash'])]

        # Agregar datos de las demás imágenes y sus comparaciones
        for i, comp in enumerate(comparison_data):
            h = self.hash_objects[i+1]

            # Datos de cada imagen comparada
            header += [f'Imagen{i+2}', f'Average{i+2}', f'Perceptual{i+2}', f'Difference{i+2}', f'Wavelet{i+2}']  # ✅ Difference
            row += [h['name'], str(h['avg']), str(h['phash']), str(h['dhash']), str(h['whash'])]

            # Resultados de distancia de Hamming
            pair = comp['pair']
            header += [
                f'Avg_{pair}',
                f'Phash_{pair}',
                f'Dhash_{pair}',  # ✅ Guardamos dhash en CSV
                f'Whash_{pair}'
            ]
            row += [comp['avg'], comp['phash'], comp['dhash'], comp['whash']]  # ✅ Incluimos dhash

        # Escribir en CSV
        try:
            file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0

            with open(filename, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                if not file_exists:
                    writer.writerow(header)  # Solo si no existe el archivo

                writer.writerow(row)

            print(f"Datos guardados en {filename}")
        except Exception as e:
            print("Error al guardar en CSV:", e)

    def plot_comparisons(self):
        """Gráfico comparativo solo contra la primera imagen"""
        if not self.hash_objects:
            messagebox.showwarning("Sin datos", "No hay comparaciones para graficar.")
            return

        labels = []
        avg_values = []
        phash_values = []
        dhash_values = []  # ✅ Para gráfico
        whash_values = []

        first = self.hash_objects[0]
        for i in range(1, len(self.hash_objects)):
            h = self.hash_objects[i]
            def hamming(a, b): return bin(int(str(a), 16) ^ int(str(b), 16)).count("1")

            labels.append(f"{h['name']}")
            avg_values.append(hamming(first['avg'], h['avg']))
            phash_values.append(hamming(first['phash'], h['phash']))
            dhash_values.append(hamming(first['dhash'], h['dhash']))  # ✅ Calculamos dhash
            whash_values.append(hamming(first['whash'], h['whash']))

        x = range(len(labels))
        bar_width = 0.2

        plt.figure(figsize=(10, 6))
        plt.bar(x, avg_values, width=bar_width, label='Average Hash', color='blue')
        plt.bar([p + bar_width for p in x], phash_values, width=bar_width, label='Perceptual Hash', color='green')
        plt.bar([p + 2 * bar_width for p in x], dhash_values, width=bar_width, label='Difference Hash', color='orange')  # ✅ Barra para dhash
        plt.bar([p + 3 * bar_width for p in x], whash_values, width=bar_width, label='Wavelet Hash', color='purple')

        plt.xticks([p + 1.5 * bar_width for p in x], labels, rotation=45, ha='right')
        plt.ylabel('Distancia de Hamming')
        plt.title('Comparación de Imágenes contra la Primera (Hamming)')
        plt.legend()
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    os.chdir("/home/seretur/Documentos/")  # Cambia al directorio donde están las imágenes
    root = tk.Tk()
    app = ImageHashApp(root)
    root.mainloop()