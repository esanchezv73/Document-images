import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import imagehash
import os

class ImageHashApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculador de Hashes de Imagen")
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

        # Calcular y mostrar hashes
        self.calculate_hashes()

    def show_previews(self):
        for idx, path in enumerate(self.image_paths):
            img = Image.open(path)
            img.thumbnail((100, 100))  # Miniatura
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(self.preview_frame, image=photo)
            label.image = photo  # Mantener referencia
            label.grid(row=0, column=idx, padx=5)

    def calculate_hashes(self):
        result_text = ""
        for idx, path in enumerate(self.image_paths):
            try:
                img = Image.open(path)

                avg_hash = imagehash.average_hash(img)
                phash = imagehash.phash(img)
                whash = imagehash.whash(img)

                result_text += f"Imagen {idx+1}: {os.path.basename(path)}\n"
                result_text += f"  Average Hash : {avg_hash}\n"
                result_text += f"  Perceptual Hash: {phash}\n"
                result_text += f"  Wavelet Hash  : {whash}\n\n"
            except Exception as e:
                result_text += f"Error procesando {path}: {e}\n"

        self.result_label.config(text=result_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageHashApp(root)
    root.mainloop()