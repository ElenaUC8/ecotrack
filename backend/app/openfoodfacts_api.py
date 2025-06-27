# backend/app/openfoodfacts_api.py

import requests

# URL base de la API de Open Food Facts
# Puedes encontrar la documentación completa en: https://wiki.openfoodfacts.org/API
OPENFOODFACTS_API_URL = "https://world.openfoodfacts.org/api/v2/product/"

def get_product_by_barcode(barcode: str):
    """
    Obtiene información de un producto de Open Food Facts por su código de barras.

    Args:
        barcode (str): El código de barras del producto.

    Returns:
        dict or None: Un diccionario con los datos relevantes del producto si se encuentra,
                      o None si no se encuentra o hay un error.
    """
    url = f"{OPENFOODFACTS_API_URL}{barcode}.json"

    try:
        response = requests.get(url, timeout=10) # Añadimos un timeout para evitar esperas infinitas
        response.raise_for_status() # Lanza una excepción si la respuesta HTTP es un error (4xx o 5xx)
        data = response.json()

        if data.get('status') == 1 and 'product' in data:
            product_data = data['product']

            # Extraer solo la información que nos interesa y mapearla
            # Los campos pueden variar ligeramente, ajusta según lo que necesites
            extracted_info = {
                'barcode': product_data.get('code'),
                'name': product_data.get('product_name', 'Nombre no disponible'),
                'nutriscore': product_data.get('nutriscore_grade', 'n/a'),
                'ecoscore': product_data.get('ecoscore_grade', 'n/a'),
                'category': product_data.get('categories', 'Categoría no disponible').split(',')[0].strip(),
                # Podrías añadir más campos como 'brands', 'image_url', 'ingredients_text', etc.
                # 'full_json': product_data # Opcional: guardar el JSON completo si lo necesitas
            }
            return extracted_info
        else:
            print(f"Producto con código de barras {barcode} no encontrado en Open Food Facts.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con Open Food Facts: {e}")
        return None
    except ValueError as e:
        print(f"Error al procesar la respuesta JSON de Open Food Facts: {e}")
        return None

# Ejemplo de uso (puedes ejecutar este archivo directamente para probarlo)
if __name__ == '__main__':
    # Código de barras de prueba (ej. Coca-Cola Light)
    test_barcode = "5449000000996" 
    # Otro ejemplo (Galletas María)
    # test_barcode = "8480000101859" 

    product = get_product_by_barcode(test_barcode)
    if product:
        print("\n--- Información del Producto desde Open Food Facts ---")
        for key, value in product.items():
            print(f"{key.replace('_', ' ').capitalize()}: {value}")
    else:
        print(f"No se pudo obtener información para el código de barras: {test_barcode}")