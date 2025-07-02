# backend/app/openfoodfacts_api.py

import requests

# URL base de la API de Open Food Facts
# Documentación completa en: https://wiki.openfoodfacts.org/API
OPENFOODFACTS_API_URL = "https://world.openfoodfacts.org/api/v2/product/"

def get_product_by_barcode(barcode: str):
    
    #Obtiene información de un producto de Open Food Facts por su código de barras.
    url = f"{OPENFOODFACTS_API_URL}{barcode}.json"

    try:
        response = requests.get(url, timeout=10) 
        response.raise_for_status() 
        data = response.json()

        if data.get('status') == 1 and 'product' in data:
            product_data = data['product']

            extracted_info = {
                'barcode': product_data.get('code'),
                'name': product_data.get('product_name', 'Nombre no disponible'),
                'nutriscore': product_data.get('nutriscore_grade', 'n/a'),
                'ecoscore': product_data.get('ecoscore_grade', 'n/a'),
                'category': product_data.get('categories', 'Categoría no disponible').split(',')[0].strip(),
                
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


if __name__ == '__main__':
    # Código de barras de prueba (ej. Coca-Cola Light)
    test_barcode = "5449000000996" 
    

    product = get_product_by_barcode(test_barcode)
    if product:
        print("\n--- Información del Producto desde Open Food Facts ---")
        for key, value in product.items():
            print(f"{key.replace('_', ' ').capitalize()}: {value}")
    else:
        print(f"No se pudo obtener información para el código de barras: {test_barcode}")