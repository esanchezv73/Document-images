import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import fitz  # PyMuPDF
import os
import easyocr
import threading
from pdf2image import convert_from_path
from docx import Document


class PDFToOCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF a OCR con Tkinter")
        self.root.geometry("750x600")

        self.pdf_path = None
        self.images_folder = "imagenes_extraidas"
        self.pages_folder = "paginas_convertidas"
        self.reader = easyocr.Reader(['es', 'en'])  # Puedes ajustar los idiomas

        self.ocr_text = ""  # Guarda el texto final para poder guardarlo después

        # Interfaz gráfica
        self.label = tk.Label(root, text="Selecciona un archivo PDF", font=("Arial", 14))
        self.label.pack(pady=20)

        self.select_button = tk.Button(root, text="Seleccionar PDF", command=self.select_pdf)
        self.select_button.pack(pady=5)

        self.process_button = tk.Button(
            root,
            text="Procesar PDF: Imágenes + Páginas",
            command=self.start_processing
        )
        self.process_button.pack(pady=5)

        # Barra de progreso
        self.progress_frame = tk.Frame(root)
        self.progress_frame.pack(pady=5)

        self.progress_label = tk.Label(self.progress_frame, text="Progreso:")
        self.progress_label.pack(side=tk.LEFT)

        self.progress_bar = tk.Canvas(self.progress_frame, width=400, height=20, bg="white")
        self.progress_bar.pack(side=tk.LEFT, padx=5)

        self.progress_rect = self.progress_bar.create_rectangle(0, 0, 0, 20, fill="green")

        # Área de texto
        self.text_area = scrolledtext.ScrolledText(root, wrap='word', height=18, width=85)
        self.text_area.pack(padx=10, pady=10)

        # Botones de guardar
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.save_txt_button = tk.Button(
            self.button_frame,
            text="Guardar como TXT",
            command=self.save_to_txt,
            state=tk.DISABLED
        )
        self.save_txt_button.pack(side=tk.LEFT, padx=5)

        self.save_docx_button = tk.Button(
            self.button_frame,
            text="Guardar como DOCX",
            command=self.save_to_docx,
            state=tk.DISABLED
        )
        self.save_docx_button.pack(side=tk.LEFT, padx=5)

    def select_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
        if file_path:
            self.pdf_path = file_path
            self.label.config(text=os.path.basename(file_path))

    def extract_embedded_images(self):
        """Extrae solo las imágenes incrustadas en el PDF."""
        if not self.pdf_path:
            return []

        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)
        else:
            for f in os.listdir(self.images_folder):
                os.remove(os.path.join(self.images_folder, f))

        doc = fitz.open(self.pdf_path)
        image_paths = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            images = page.get_images(full=True)
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_path = os.path.join(self.images_folder, f"img_pag_{page_num}_{img_index}.{image_ext}")
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                image_paths.append(image_path)

        doc.close()
        return image_paths

    def convert_pdf_pages_to_images(self):
        """Convierte cada página del PDF a imagen (para OCR de texto escaneado)."""
        if not self.pdf_path:
            return []

        if not os.path.exists(self.pages_folder):
            os.makedirs(self.pages_folder)
        else:
            for f in os.listdir(self.pages_folder):
                os.remove(os.path.join(self.pages_folder, f))

        pages = convert_from_path(self.pdf_path, dpi=200)  # Ajusta DPI según necesites
        image_paths = []
        for i, page in enumerate(pages):
            img_path = os.path.join(self.pages_folder, f"pagina_{i}.png")
            page.save(img_path, "PNG")
            image_paths.append(img_path)
        return image_paths

    def perform_ocr_on_images(self, image_paths):
        total = len(image_paths)
        step = 100 / total if total > 0 else 100
        all_text = ""

        for idx, img_path in enumerate(image_paths):
            result = self.reader.readtext(img_path, paragraph=True)
            text = "\n".join([res[1] for res in result])
            all_text += f"\n--- Texto de {os.path.basename(img_path)} ---\n"
            all_text += text

            # Actualizar barra de progreso
            progress = (idx + 1) * step
            self.update_progress_bar(progress)

        return all_text

    def update_progress_bar(self, percentage):
        self.progress_bar.coords(self.progress_rect, (0, 0, percentage * 4, 20))
        self.root.update_idletasks()

    def start_processing(self):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Procesando... por favor espera.\n")
        self.save_txt_button.config(state=tk.DISABLED)
        self.save_docx_button.config(state=tk.DISABLED)
        self.update_progress_bar(0)
        threading.Thread(target=self.process_pdf).start()

    def process_pdf(self):
        try:
            self.ocr_text = ""

            # Extraer imágenes incrustadas
            embedded_images = self.extract_embedded_images()
            if embedded_images:
                self.ocr_text += "\n=== Imágenes incrustadas ===\n"
                self.ocr_text += self.perform_ocr_on_images(embedded_images)

            # Convertir páginas a imágenes y hacer OCR
            page_images = self.convert_pdf_pages_to_images()
            if page_images:
                self.ocr_text += "\n\n=== Texto de páginas escaneadas ===\n"
                self.ocr_text += self.perform_ocr_on_images(page_images)

            if not self.ocr_text.strip():
                self.ocr_text = "No se encontró texto o imágenes legibles en el PDF."

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, self.ocr_text)
            self.save_txt_button.config(state=tk.NORMAL)
            self.save_docx_button.config(state=tk.NORMAL)
            self.update_progress_bar(100)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

    def save_to_txt(self):
        if not self.ocr_text:
            messagebox.showwarning("Advertencia", "No hay texto para guardar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Archivo de texto", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.ocr_text)
                messagebox.showinfo("Éxito", "El texto ha sido guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")

    def save_to_docx(self):
        if not self.ocr_text:
            messagebox.showwarning("Advertencia", "No hay texto para guardar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".docx",
                                                 filetypes=[("Documento de Word", "*.docx")])
        if file_path:
            try:
                doc = Document()
                for line in self.ocr_text.split('\n'):
                    doc.add_paragraph(line)
                doc.save(file_path)
                messagebox.showinfo("Éxito", "El documento DOCX ha sido guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToOCRApp(root)
    root.mainloop()