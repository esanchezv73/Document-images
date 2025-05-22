import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from PIL import Image
import easyocr
import os

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR con EasyOCR")
        self.root.geometry("600x500")

        # Botón para abrir imagen
        self.open_button = tk.Button(root, text="Abrir Imagen", command=self.abrir_imagen)
        self.open_button.pack(pady=10)

        # Área de texto con scroll para mostrar resultado OCR
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
        self.text_area.pack(padx=10, pady=10)

        # Botón para guardar resultado
        self.save_button = tk.Button(root, text="Guardar como .txt", command=self.guardar_txt, state=tk.DISABLED)
        self.save_button.pack(pady=10)

        # Variable para almacenar el texto OCR
        self.ocr_text = ""

    def abrir_imagen(self):
        # Abrir diálogo para seleccionar archivo
        file_path = filedialog.askopenfilename(
            title="Selecciona una imagen",
            filetypes=[("Imágenes JPG/PNG", "*.jpg *.jpeg *.png")]
        )

        if not file_path:
            return  # Salir si no se seleccionó nada

        try:
            # Realizar OCR
            reader = easyocr.Reader(['es'])  # Puedes cambiar 'es' a otro idioma si necesitas
            result = reader.readtext(file_path,paragraph=True, contrast_ths=0.2)

            # Extraer y concatenar solo los textos reconocidos
            self.ocr_text = "\n".join([text[1] for text in result])

            # Mostrar en el área de texto
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, self.ocr_text)

            # Habilitar botón de guardar
            self.save_button.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error durante el OCR:\n{e}")

    def guardar_txt(self):
        if not self.ocr_text:
            messagebox.showwarning("Advertencia", "No hay texto para guardar.")
            return

        # Pedir ubicación para guardar el archivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt")]
        )

        if not file_path:
            return  # Salir si se cancela

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.ocr_text)
            messagebox.showinfo("Éxito", "Texto guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

# Crear ventana principal
if __name__ == "__main__":
    os.chdir("/home/seretur/Documentos")
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()