# backend/load_emissions_data.py

import pandas as pd
import os
# Asegúrate de que esta importación sea correcta según dónde tengas 'app.py' y 'load_emissions_data.py'
# Si app.py está en 'backend/app/' y este script en 'backend/', usa:
from app import app, db, RegionalCo2Emission
# Si ambos están en 'backend/', usa:
# from app import app, db, RegionalCo2Emission


def load_emissions_from_csv(file_path):
    """
    Carga los datos de emisiones de CO2 desde un archivo CSV a la base de datos.
    Esta función asume que se llama dentro de un `app.app_context()`.
    """
    try:
        df = pd.read_csv(file_path, sep=';', encoding='latin1', skiprows=3, index_col=0)

        if 'C.A. de Euskadi' in df.index:
            emissions_row = df.loc['C.A. de Euskadi']
        elif '1' in df.index and df.loc['1'].iloc[0] == 'C.A. de Euskadi':
             emissions_row = df.loc['1']
             emissions_row = emissions_row.iloc[1:]
        else:
            print("No se encontró la fila 'C.A. de Euskadi' o su equivalente en el CSV. No se cargaron datos.")
            return

        years_data = emissions_row.filter(regex=r'^\d{4}$')

        emissions_to_insert = []
        for year_col, value in years_data.items():
            try:
                year = int(year_col)
                co2_tonnes = float(str(value).replace('.', ''))
                emissions_to_insert.append(
                    RegionalCo2Emission(
                        region_name='C.A. de Euskadi',
                        year=year,
                        total_co2_tonnes=co2_tonnes
                    )
                )
            except ValueError:
                print(f"Advertencia: No se pudo convertir el año '{year_col}' o valor '{value}' a número. Saltando.")
                continue

        # --- SOLUCIÓN INTEGRITYERROR: Eliminar datos existentes antes de la carga ---
        # Si esta función se ejecuta dentro de un app_context, db.session ya es accesible
        db.session.query(RegionalCo2Emission).filter_by(region_name='C.A. de Euskadi').delete()
        db.session.commit() # Confirma la eliminación antes de añadir nuevos
        print("Datos existentes de C.A. de Euskadi eliminados antes de la carga (si los había).")

        # Añadir todos los nuevos registros
        db.session.add_all(emissions_to_insert)
        db.session.commit()
        print(f"Datos de emisiones de CO2 para C.A. de Euskadi ({len(emissions_to_insert)} registros) cargados exitosamente.")

    except FileNotFoundError:
        print(f"Error: El archivo CSV no se encontró en '{file_path}'.")
    except pd.errors.EmptyDataError:
        print(f"Error: El archivo CSV '{file_path}' está vacío.")
    except Exception as e:
        # Aunque el rollback aquí estará dentro del contexto, la causa raíz es el IntegrityError
        # y la solución principal es evitar que ocurra al eliminar duplicados.
        print(f"Ocurrió un error inesperado durante la carga de datos: {e}")
        db.session.rollback() # Deshacer si hay un error al añadir


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Asegúrate de que esta ruta sea correcta dependiendo de dónde esté 'load_emissions_data.py'
    # Si load_emissions_data.py está en 'backend/' y 'data/' también, entonces:
    csv_file_path = os.path.join(current_dir, '..', 'data', 'BIG-TAB.4.07.19_c.csv')
    # Si load_emissions_data.py está en 'backend/app/' y 'data/' está en 'backend/', entonces:
    # csv_file_path = os.path.join(current_dir, '..', 'data', 'BIG-TAB.4.07.19_c.csv')

    # --- SOLUCIÓN RUNTIMEERROR: Envuelve todo en un contexto de aplicación ---
    with app.app_context():
        db.create_all() # Asegura que las tablas estén creadas
        print("Base de datos y tablas creadas (si no existían).")
        load_emissions_from_csv(csv_file_path)