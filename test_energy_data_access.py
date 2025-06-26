import requests
import json
import pandas as pd
import os

# --- Fuente de Datos 1: Leer un archivo local de Factores de Emisión ---
# Define la ruta a tu archivo CSV o XLSX descargado
# Asegúrate de que el nombre del archivo coincida con el que descargues
EMISSION_FACTORS_FILE = "BIG-TAB.4.07.19_c.csv" 

def test_load_emission_factors_from_file(file_path=EMISSION_FACTORS_FILE):
    """
    Prueba la carga de factores de emisión de CO2 desde un archivo CSV o XLSX local.
    """
    print(f"\n--- Probando carga de Factores de Emisión desde el archivo: {file_path} ---")
    
    if not os.path.exists(file_path):
        print(f"Error: El archivo '{file_path}' no se encontró en la misma carpeta que el script.")
        print("Por favor, descarga el archivo de datos.gob.es y colócalo en la ubicación correcta.")
        return False, "Archivo no encontrado"

    try:
        # Detecta el tipo de archivo por la extensión y usa la función de lectura adecuada
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path, encoding='latin-1', sep=';', header=2)
            print(f"Archivo CSV '{file_path}' cargado exitosamente.")
        elif file_path.lower().endswith('.xlsx'):
            df = pd.read_excel(file_path)
            print(f"Archivo XLSX '{file_path}' cargado exitosamente.")
        else:
            print(f"Error: Formato de archivo no soportado para '{file_path}'. Se esperan .csv o .xlsx")
            return False, "Formato de archivo no soportado"

        print("Primeras 5 filas de los datos cargados:")
        print(df.head().to_string()) # .to_string() para imprimir bien en consola
        print(f"\nEl DataFrame tiene {len(df)} filas y {len(df.columns)} columnas.")
        
        # Aquí puedes añadir lógica para procesar los datos específicos que necesites
        # Por ejemplo, buscar un factor de emisión concreto.
        
        return True, df.to_dict('records') # Devuelve el DataFrame como una lista de diccionarios
    except Exception as e:
        print(f"Error al cargar o leer el archivo '{file_path}': {e}")
        return False, str(e)

# --- Fuente de Datos 2: Open Food Facts API (se mantiene) ---
def test_fetch_product_data_openfoodfacts(barcode="737628064502"): # Ejemplo: Código de barras de Coca-Cola Light
    """
    Prueba el acceso a la API de Open Food Facts para un producto dado.
    """
    api_url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    print(f"\n--- Probando acceso a Open Food Facts API para código {barcode} ---")
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data and 'product' in data:
            product_name = data['product'].get('product_name', 'N/A')
            nutriscore = data['product'].get('nutriscore_score', 'N/A')
            ecoscore = data['product'].get('ecoscore_score', 'N/A')
            print(f"Producto encontrado: {product_name}")
            print(f"Nutri-score: {nutriscore}, Eco-score: {ecoscore}")
            print("Datos recibidos (primeras 200 caracteres):")
            print(json.dumps(data, indent=2)[:200] + "...")
            return True, data
        else:
            print(f"Producto con código {barcode} no encontrado o estructura de datos inesperada.")
            return False, "Producto no encontrado"
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a la API de Open Food Facts: {e}")
        return False, str(e)

if __name__ == "__main__":
    print("--- Ejecutando tests de acceso a datos ---")
    
    # Prueba de carga de Factores de Emisión desde archivo
    # Asegúrate de cambiar 'tu_archivo_de_emisiones.csv' por el nombre de tu archivo descargado
    success_emission_factors, _ = test_load_emission_factors_from_file(EMISSION_FACTORS_FILE)
    if success_emission_factors:
        print("\nTest de carga de factores de emisión desde archivo pasó.")
    else:
        print("\nTest de carga de factores de emisión desde archivo falló. Revisa el nombre del archivo y su ubicación.")

    # Prueba Open Food Facts
    success_openfoodfacts, _ = test_fetch_product_data_openfoodfacts()
    if success_openfoodfacts:
        print("\nTest de acceso a datos de productos (Open Food Facts) pasó.")
    else:
        print("\nTest de acceso a datos de productos (Open Food Facts) falló.")

    if success_emission_factors and success_openfoodfacts:
        print("\nTodos los tests de acceso a datos pasaron.")
    else:
        print("\nAlgunos tests de acceso a datos fallaron.")