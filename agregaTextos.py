# guardar_parrafo_gui.py
import tkinter as tk
from tkinter import filedialog, messagebox

def guardar_parrafo():
    texto = entrada.get("1.0", tk.END).strip()
    if not texto:
        messagebox.showwarning("Advertencia", "El campo está vacío.")
        return

    archivo = filedialog.asksaveasfilename(defaultextension=".txt",
                                          filetypes=[("Archivos de texto", "*.txt")])
    if archivo:
        try:
            with open(archivo, 'a', encoding='utf-8') as f:
                f.write('\n\n' + texto)  # Agregar salto de línea antes del nuevo párrafo
            messagebox.showinfo("Éxito", "Párrafo guardado correctamente.")
            entrada.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo.\n{e}")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Guardar Párrafo")

# Configurar widgets
etiqueta = tk.Label(ventana, text="Escribe un prompt para un chatbot:")
etiqueta.pack(pady=5)

entrada = tk.Text(ventana, wrap=tk.WORD, width=60, height=15)
entrada.pack(padx=10, pady=10)

boton_guardar = tk.Button(ventana, text="Guardar en archivo...", command=guardar_parrafo)
boton_guardar.pack(pady=5)

ventana.mainloop()