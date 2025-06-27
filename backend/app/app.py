# backend/app.py

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from openfoodfacts_api import get_product_by_barcode
import os

# Inicializa la aplicación Flask
app = Flask(__name__)

# --- Configuración de la Base de Datos ---
# Define la ruta de la base de datos SQLite
# Usaremos un archivo 'site.db' en la misma carpeta del proyecto
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desactiva el seguimiento de modificaciones de objetos (consume menos memoria)

# Inicializa la extensión de SQLAlchemy
db = SQLAlchemy(app)

# --- Definición de Modelos de Base de Datos ---

class User(db.Model):
    __tablename__ = 'users' # Nombre de la tabla explícito
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Puedes añadir más campos como password_hash, created_at, etc.

    # Relación con favoritos (si decides implementarla)
    # favorites = db.relationship('Product', secondary='user_favorites',
    #                             backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    __tablename__ = 'products' # Nombre de la tabla explícito
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(13), unique=True, nullable=False) # Código de barras (EAN-13)
    name = db.Column(db.String(255), nullable=False)
    nutriscore = db.Column(db.String(1), nullable=True) # A, B, C, D, E
    ecoscore = db.Column(db.String(2), nullable=True)   # A+, A, B, C, D, E (A+ para mayor granularidad)
    category = db.Column(db.String(100), nullable=True) # Bebidas, Lácteos, etc.
    # Puedes añadir más campos si los necesitas del JSON de Open Food Facts, ej. brand, image_url, etc.

    def __repr__(self):
        return f'<Product {self.name} ({self.barcode})>'

class RegionalCo2Emission(db.Model):
    __tablename__ = 'regional_co2_emissions' # Nombre de la tabla explícito
    id = db.Column(db.Integer, primary_key=True)
    region_name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_co2_tonnes = db.Column(db.Float, nullable=False)

    # Para asegurar que no haya entradas duplicadas para la misma región y año
    __table_args__ = (db.UniqueConstraint('region_name', 'year', name='_region_year_uc'),)

    def __repr__(self):
        return f'<Emission {self.region_name} {self.year}: {self.total_co2_tonnes} tonnes>'


# --- Ruta de prueba (dejamos la misma por ahora) ---
@app.route('/')
def home():
    """
    Ruta de inicio para verificar que el servidor está funcionando.
    """
    return jsonify({"message": "¡Bienvenido al backend de tu startup! Flask está funcionando."})

@app.route('/api/products/search', methods=['GET'])
def search_product():
    barcode = request.args.get('barcode') # Obtiene el código de barras de los parámetros de la URL (?barcode=...)

    if not barcode:
        return jsonify({"error": "Se requiere un código de barras para la búsqueda."}), 400

    # 1. Intentar buscar el producto en nuestra propia base de datos
    product = Product.query.filter_by(barcode=barcode).first()

    if product:
        # Si el producto ya está en nuestra BD, lo devolvemos
        print(f"Producto {barcode} encontrado en la base de datos local.")
        return jsonify({
            "id": product.id,
            "barcode": product.barcode,
            "name": product.name,
            "nutriscore": product.nutriscore,
            "ecoscore": product.ecoscore,
            "category": product.category
        })
    else:
        # 2. Si no está en nuestra BD, buscar en Open Food Facts
        print(f"Producto {barcode} no encontrado localmente, buscando en Open Food Facts...")
        off_product_data = get_product_by_barcode(barcode)

        if off_product_data:
            # 3. Si se encuentra en Open Food Facts, guardarlo en nuestra BD
            try:
                new_product = Product(
                    barcode=off_product_data['barcode'],
                    name=off_product_data['name'],
                    nutriscore=off_product_data['nutriscore'],
                    ecoscore=off_product_data['ecoscore'],
                    category=off_product_data['category']
                )
                db.session.add(new_product)
                db.session.commit()
                print(f"Producto {barcode} guardado exitosamente desde Open Food Facts.")

                # Devolver la información del producto recién guardado
                return jsonify({
                    "id": new_product.id,
                    "barcode": new_product.barcode,
                    "name": new_product.name,
                    "nutriscore": new_product.nutriscore,
                    "ecoscore": new_product.ecoscore,
                    "category": new_product.category
                }), 201 # 201 Created
            except Exception as e:
                db.session.rollback() # Deshacer si hay un error al guardar
                print(f"Error al guardar el producto {barcode} en la base de datos: {e}")
                return jsonify({"error": "Error interno al guardar el producto."}), 500
        else:
            # 4. Si no se encuentra en ningún sitio
            return jsonify({"message": f"Producto con código de barras '{barcode}' no encontrado."}), 404


# --- Punto de entrada para ejecutar la aplicación ---
if __name__ == '__main__':
    # Crear las tablas en la base de datos si no existen
    with app.app_context():
        db.create_all()
        print("Base de datos y tablas creadas (si no existían).")

    app.run(debug=True)