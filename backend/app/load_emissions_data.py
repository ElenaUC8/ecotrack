# backend/load_emissions_data.py

import pandas as pd
import os
from app import app, db, RegionalCo2Emission # Importa los objetos app, db y el modelo desde tu app.py

def load_emissions_from_csv(file_path):
    """
    Carga los datos de emisiones de CO2 desde un archivo CSV a la base de datos.
    """
    try:
        # Replicar la lógica de lectura del CSV de tus pruebas, si es necesario ajustando skiprows, etc.
        df = pd.read_csv(file_path, sep=';', encoding='latin1', skiprows=3, index_col=0)

        # Limpiar el DataFrame para solo contener los datos de emisiones
        # La primera fila (índice 1 en la imagen de tu salida) contiene los datos
        # Asegúrate de que 'C.A. de Euskadi' es el índice correcto o ajusta
        if 'C.A. de Euskadi' in df.index:
            emissions_row = df.loc['C.A. de Euskadi']
        elif '1' in df.index and df.loc['1'].iloc[0] == 'C.A. de Euskadi': # Si el índice es numérico
             emissions_row = df.loc['1']
             # Elimina la primera columna que contiene "C.A. de Euskadi" para que solo queden los años y valores
             emissions_row = emissions_row.iloc[1:]
        else:
            print("No se encontró la fila 'C.A. de Euskadi' o su equivalente en el CSV.")
            return

        # Filtra las columnas que representan los años (de 2005 a 2022)
        # Asume que los nombres de las columnas son los años (strings)
        years_data = emissions_row.filter(regex=r'^\d{4}$') # Filtra solo columnas con nombres que son 4 dígitos (años)

        # Convertir los datos a un formato que podamos insertar en la BD
        emissions_to_insert = []
        for year_col, value in years_data.items():
            try:
                year = int(year_col)
                # El valor puede tener puntos como separadores de miles, eliminarlos antes de convertir a float
                co2_tonnes = float(str(value).replace('.', ''))
                emissions_to_insert.append(
                    RegionalCo2Emission(
                        region_name='C.A. de Euskadi', # O el nombre de la región que extraigas del CSV
                        year=year,
                        total_co2_tonnes=co2_tonnes
                    )
                )
            except ValueError:
                print(f"Advertencia: No se pudo convertir el año '{year_col}' o valor '{value}' a número. Saltando.")
                continue

        # Usar el contexto de la aplicación para interactuar con la BD
        with app.app_context():
            # Opcional: Eliminar datos existentes de Euskadi para evitar duplicados si se ejecuta varias veces
            # db.session.query(RegionalCo2Emission).filter_by(region_name='C.A. de Euskadi').delete()
            # db.session.commit()
            # print("Datos existentes de C.A. de Euskadi eliminados antes de la carga.")

            # Añadir todos los nuevos registros
            db.session.add_all(emissions_to_insert)
            db.session.commit()
            print(f"Datos de emisiones de CO2 para C.A. de Euskadi ({len(emissions_to_insert)} registros) cargados exitosamente.")

    except FileNotFoundError:
        print(f"Error: El archivo CSV no se encontró en '{file_path}'.")
    except pd.errors.EmptyDataError:
        print(f"Error: El archivo CSV '{file_path}' está vacío.")
    except Exception as e:
        print(f"Ocurrió un error inesperado durante la carga de datos: {e}")
        db.session.rollback() # En caso de error, deshacer la transacción


if __name__ == '__main__':
    # Define la ruta absoluta al archivo CSV
    # Asegúrate de que 'load_emissions_data.py' está en el directorio 'backend'
    # y 'data/BIG-TAB.4.07.19_c.csv' es la ruta relativa desde 'backend'

    # Obtiene la ruta del directorio actual donde se ejecuta este script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_dir, '..', 'data', 'BIG-TAB.4.07.19_c.csv')

    load_emissions_from_csv(csv_file_path)