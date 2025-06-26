import sqlite3
import hashlib # Para simular el hash de contraseñas de usuario

def create_db_and_tables(db_name=':memory:'):
    """
    Crea una base de datos SQLite (en memoria por defecto) y define las tablas.
    Retorna el objeto de conexión.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Tabla USERS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')

    # Tabla PRODUCTS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            nutriscore TEXT,
            ecoscore TEXT,
            product_category TEXT,
            raw_json_data TEXT
        )
    ''')

    # Tabla REGIONAL_CO2_EMISSIONS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regional_co2_emissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_name TEXT NOT NULL,
            year INTEGER NOT NULL,
            total_co2_tonnes REAL,
            UNIQUE(region_name, year) -- Asegura que no haya entradas duplicadas por región y año
        )
    ''')
    
    conn.commit()
    return conn

# --- Operaciones CRUD para la tabla PRODUCTS ---
def add_product(conn, barcode, name, nutriscore=None, ecoscore=None, product_category=None, raw_json_data=None):
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO products (barcode, name, nutriscore, ecoscore, product_category, raw_json_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (barcode, name, nutriscore, ecoscore, product_category, raw_json_data))
        conn.commit()
        print(f"[PRODUCTOS] Añadido: '{name}' (Código: {barcode})")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"[PRODUCTOS] Error: Producto con código de barras '{barcode}' ya existe.")
        return None
    except Exception as e:
        print(f"[PRODUCTOS] Error al añadir producto: {e}")
        return None

def get_product_by_barcode(conn, barcode):
    cursor = conn.cursor()
    cursor.execute('SELECT id, barcode, name, nutriscore, ecoscore, product_category FROM products WHERE barcode = ?', (barcode,))
    return cursor.fetchone() # Retorna la primera fila encontrada

def update_product_ecoscore(conn, barcode, new_ecoscore):
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET ecoscore = ? WHERE barcode = ?', (new_ecoscore, barcode))
    conn.commit()
    if cursor.rowcount > 0:
        print(f"[PRODUCTOS] Actualizado: Eco-score de '{barcode}' a '{new_ecoscore}'")
        return True
    else:
        print(f"[PRODUCTOS] No encontrado para actualizar: '{barcode}'")
        return False

def delete_product(conn, barcode):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE barcode = ?', (barcode,))
    conn.commit()
    if cursor.rowcount > 0:
        print(f"[PRODUCTOS] Eliminado: '{barcode}'")
        return True
    else:
        print(f"[PRODUCTOS] No encontrado para eliminar: '{barcode}'")
        return False

# --- Operaciones CRUD para la tabla REGIONAL_CO2_EMISSIONS ---
def add_regional_emission(conn, region_name, year, total_co2_tonnes):
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO regional_co2_emissions (region_name, year, total_co2_tonnes)
            VALUES (?, ?, ?)
        ''', (region_name, year, total_co2_tonnes))
        conn.commit()
        print(f"[EMISIONES] Añadido: '{region_name}' en {year} con {total_co2_tonnes} toneladas")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"[EMISIONES] Error: Emisiones para '{region_name}' en {year} ya existen.")
        return None
    except Exception as e:
        print(f"[EMISIONES] Error al añadir emisión regional: {e}")
        return None

def get_regional_emissions(conn, region_name, year=None):
    cursor = conn.cursor()
    if year:
        cursor.execute('SELECT id, region_name, year, total_co2_tonnes FROM regional_co2_emissions WHERE region_name = ? AND year = ?', (region_name, year))
    else:
        cursor.execute('SELECT id, region_name, year, total_co2_tonnes FROM regional_co2_emissions WHERE region_name = ?', (region_name,))
    return cursor.fetchall() # Retorna todas las filas que coincidan

def update_regional_emission(conn, region_name, year, new_total_co2_tonnes):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE regional_co2_emissions
        SET total_co2_tonnes = ?
        WHERE region_name = ? AND year = ?
    ''', (new_total_co2_tonnes, region_name, year))
    conn.commit()
    if cursor.rowcount > 0:
        print(f"[EMISIONES] Actualizado: '{region_name}' en {year} a {new_total_co2_tonnes} toneladas")
        return True
    else:
        print(f"[EMISIONES] No encontrado para actualizar: '{region_name}' en {year}")
        return False

def delete_regional_emission(conn, region_name, year):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM regional_co2_emissions WHERE region_name = ? AND year = ?', (region_name, year))
    conn.commit()
    if cursor.rowcount > 0:
        print(f"[EMISIONES] Eliminado: '{region_name}' en {year}")
        return True
    else:
        print(f"[EMISIONES] No encontrado para eliminar: '{region_name}' en {year}")
        return False

# --- Operaciones CRUD básicas para la tabla USERS (para completar el ERD) ---
def add_user(conn, username, email, password):
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest() # Hash simple de la contraseña
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        conn.commit()
        print(f"[USUARIOS] Añadido: '{username}'")
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        print(f"[USUARIOS] Error: Usuario con nombre '{username}' o email '{email}' ya existe. Detalle: {e}")
        return None
    except Exception as e:
        print(f"[USUARIOS] Error al añadir usuario: {e}")
        return None

def update_user_email(conn, username, new_email):
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET email = ? WHERE username = ?', (new_email, username))
    conn.commit()
    if cursor.rowcount > 0:
        print(f"[USUARIOS] Actualizado: Email de '{username}' a '{new_email}'")
        return True
    else:
        print(f"[USUARIOS] No encontrado para actualizar: '{username}'")
        return False

def delete_user(conn, username):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    if cursor.rowcount > 0:
        print(f"[USUARIOS] Eliminado: '{username}'")
        return True
    else:
        print(f"[USUARIOS] No encontrado para eliminar: '{username}'")
        return False


# --- Ejecución de los Tests ---
if __name__ == '__main__':
    print("--- Iniciando tests de Diseño de Base de Datos y CRUD ---")
    
    # Crear la base de datos en memoria para los tests
    conn = create_db_and_tables()
    print("Base de datos en memoria y tablas creadas.")

    # --- Test 1: Operaciones CRUD en Productos ---
    print("\n=== TEST CRUD: PRODUCTOS ===")
    add_product(conn, '737628064502', 'Coca-Cola Light', 'A', 'B', 'Bebidas')
    add_product(conn, '8480000123457', 'Leche Semidesnatada', 'C', 'C', 'Lácteos')
    add_product(conn, '737628064502', 'Coca-Cola Light (duplicado)') # Intento de duplicado

    print(f"\nBuscar producto '737628064502': {get_product_by_barcode(conn, '737628064502')}")
    update_product_ecoscore(conn, '737628064502', 'A+')
    print(f"Buscar producto '737628064502' (actualizado): {get_product_by_barcode(conn, '737628064502')}")
    
    delete_product(conn, '8480000123457')
    print(f"Buscar producto '8480000123457' (eliminado, debería ser None): {get_product_by_barcode(conn, '8480000123457')}")

    # --- Test 2: Operaciones CRUD en Emisiones Regionales ---
    print("\n=== TEST CRUD: EMISIONES REGIONALES ===")
    add_regional_emission(conn, 'C.A. de Euskadi', 2020, 13659995.0)
    add_regional_emission(conn, 'C.A. de Euskadi', 2021, 14828603.0)
    add_regional_emission(conn, 'Cataluña', 2020, 25000000.0)
    add_regional_emission(conn, 'C.A. de Euskadi', 2020, 10000000.0) # Intento de duplicado

    print(f"\nEmisiones de 'C.A. de Euskadi' (todas): {get_regional_emissions(conn, 'C.A. de Euskadi')}")
    print(f"Emisiones de 'C.A. de Euskadi' en 2021: {get_regional_emissions(conn, 'C.A. de Euskadi', 2021)}")
    
    update_regional_emission(conn, 'C.A. de Euskadi', 2020, 13700000.0)
    print(f"Emisiones de 'C.A. de Euskadi' en 2020 (actualizadas): {get_regional_emissions(conn, 'C.A. de Euskadi', 2020)}")
    
    delete_regional_emission(conn, 'C.A. de Euskadi', 2021)
    print(f"Emisiones de 'C.A. de Euskadi' en 2021 (eliminadas, debería ser vacío): {get_regional_emissions(conn, 'C.A. de Euskadi', 2021)}")

    # --- Test 3: Operaciones CRUD en Usuarios ---
    print("\n=== TEST CRUD: USUARIOS ===")
    add_user(conn, 'juanperez', 'juan.perez@example.com', 'mi_password_segura')
    add_user(conn, 'mariagarcia', 'maria.garcia@example.com', 'otra_password')
    add_user(conn, 'juanperez', 'juan.perez2@example.com', 'password_duplicada') # Intento de duplicado de username
    add_user(conn, 'pedrolopez', 'juan.perez@example.com', 'password_duplicada_email') # Intento de duplicado de email

    update_user_email(conn, 'juanperez', 'juan.perez.new@example.com')
    
    delete_user(conn, 'mariagarcia')
    
    conn.close()
    print("\n--- Todos los tests de Base de Datos y CRUD han finalizado ---")