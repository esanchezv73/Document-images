import pandas as pd
import matplotlib.pyplot as plt
import os

def mostrar_tabla(dataframe):
    """Muestra el dataframe como una tabla formateada"""
    print("\n" + "="*80)
    print("Contenido del archivo CSV:")
    print("="*80)
    print(dataframe.to_string(index=False))
    print("="*80 + "\n")

def seleccionar_columnas(dataframe):
    """Permite al usuario seleccionar columnas para analizar"""
    columnas = dataframe.columns.tolist()
    
    print("\nColumnas disponibles:")
    for i, col in enumerate(columnas, 1):
        print(f"{i}. {col}")
    
    seleccion = input("\nIngrese los números de las columnas a analizar (separados por comas): ")
    indices = [int(i.strip())-1 for i in seleccion.split(",") if i.strip().isdigit()]
    
    # Validar selección
    columnas_seleccionadas = []
    for i in indices:
        if 0 <= i < len(columnas):
            columnas_seleccionadas.append(columnas[i])
        else:
            print(f"Advertencia: El índice {i+1} está fuera de rango y será ignorado.")
    
    if not columnas_seleccionadas:
        print("No se seleccionaron columnas válidas. Usando las primeras 2 columnas por defecto.")
        columnas_seleccionadas = columnas[:2]
    
    return columnas_seleccionadas

def crear_histogramas(dataframe, columnas):
    """Crea histogramas superpuestos para las columnas seleccionadas"""
    plt.figure(figsize=(10, 6))
    
    for col in columnas:
        # Limpiar datos: eliminar NaN y convertir a numérico si es posible
        datos = pd.to_numeric(dataframe[col], errors='coerce').dropna()
        
        if datos.empty:
            print(f"Advertencia: La columna '{col}' no contiene datos numéricos válidos y será omitida.")
            continue
        
        plt.hist(datos, bins=15, alpha=0.5, label=col, edgecolor='black')
    
    if not plt.gca().has_data():
        print("Error: No hay datos válidos para graficar.")
        return
    
    plt.title('Histogramas Superpuestos') #Título del gráfico
    plt.xlabel('Valores')
    plt.ylabel('Frecuencia')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Mostrar el gráfico
    plt.tight_layout()
    plt.show()
    
    # Preguntar si desea guardar el gráfico
    guardar = input("\n¿Desea guardar el gráfico? (s/n): ").lower()
    if guardar == 's':
        guardar_grafico()

def guardar_grafico():
    """Guarda el gráfico actual en un archivo"""
    formatos_disponibles = ['png', 'jpg', 'pdf', 'svg']
    
    print("\nFormatos disponibles:")
    for i, fmt in enumerate(formatos_disponibles, 1):
        print(f"{i}. {fmt}")
    
    seleccion = input("\nSeleccione el formato (número): ")
    try:
        indice = int(seleccion) - 1
        formato = formatos_disponibles[indice]
    except (ValueError, IndexError):
        print("Selección no válida. Usando PNG por defecto.")
        formato = 'png'
    
    nombre_archivo = input("Ingrese el nombre del archivo (sin extensión): ").strip()
    if not nombre_archivo:
        nombre_archivo = "histogramas"
    
    nombre_completo = f"{nombre_archivo}.{formato}"
    
    try:
        plt.savefig(nombre_completo, format=formato, dpi=300, bbox_inches='tight')
        print(f"Gráfico guardado exitosamente como '{nombre_completo}'")
    except Exception as e:
        print(f"Error al guardar el gráfico: {e}")

def main():
    print("=== Analizador de CSV con Histogramas Superpuestos ===")
    
    # Solicitar archivo CSV
    archivo = input("\nIngrese la ruta del archivo CSV: ").strip()
    
    if not os.path.exists(archivo):
        print("Error: El archivo no existe.")
        return
    
    try:
        # Leer el archivo CSV
        df = pd.read_csv(archivo)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return
    
    # Mostrar la tabla
    mostrar_tabla(df)
    
    # Seleccionar columnas
    columnas_analizar = seleccionar_columnas(df)
    
    # Crear histogramas
    crear_histogramas(df, columnas_analizar)

if __name__ == "__main__":
    main()