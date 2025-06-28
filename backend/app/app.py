# backend/app.py

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from openfoodfacts_api import get_product_by_barcode
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os

# Inicializa la aplicación Flask
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
# --- Configuración de la Base de Datos ---
# Define la ruta de la base de datos SQLite
# Usaremos un archivo 'site.db' en la misma carpeta del proyecto
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desactiva el seguimiento de modificaciones de objetos (consume menos memoria)

# Inicializa la extensión de SQLAlchemy
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# --- Definición de Modelos de Base de Datos ---


user_favorites = db.Table('user_favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)



class User(db.Model):
    __tablename__ = 'users' # Nombre de la tabla explícito
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) # <-- Campo para el hash de la contraseña
    favorites = db.relationship('Product', secondary=user_favorites,
                                backref=db.backref('favorited_by_users', lazy='dynamic'))

    def __repr__(self):
        return f'<User {self.username}>'

    # Métodos para verificar y guardar contraseñas
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


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


@app.route('/api/emissions', methods=['GET'])
def get_emissions():
    region_name = request.args.get('region')
    year_str = request.args.get('year')

    if not region_name or not year_str:
        return jsonify({"error": "Se requieren los parámetros 'region' y 'year'."}), 400

    try:
        year = int(year_str)
    except ValueError:
        return jsonify({"error": "El parámetro 'year' debe ser un número entero válido."}), 400

    # Buscar la emisión en la base de datos
    emission = RegionalCo2Emission.query.filter_by(region_name=region_name, year=year).first()

    if emission:
        return jsonify({
            "id": emission.id,
            "region_name": emission.region_name,
            "year": emission.year,
            "total_co2_tonnes": emission.total_co2_tonnes
        })
    else:
        return jsonify({"message": f"No se encontraron datos de emisión para la región '{region_name}' y el año '{year}'."}), 404



@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.get_json() # Obtiene los datos JSON enviados en el cuerpo de la petición

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Se requieren nombre de usuario, email y contraseña."}), 400

    # Verificar si el usuario o el email ya existen
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "El nombre de usuario ya existe."}), 409 # 409 Conflict

    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({"error": "El email ya está registrado."}), 409

    # Crear nuevo usuario
    new_user = User(username=username, email=email)
    new_user.set_password(password) # Cifra la contraseña antes de guardarla

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Usuario registrado exitosamente.", "user_id": new_user.id}), 201 # 201 Created
    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar usuario: {e}")
        return jsonify({"error": "Error interno al registrar el usuario."}), 500

@app.route('/api/users/login', methods=['POST'])
def login_user():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Se requieren nombre de usuario y contraseña."}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # En una aplicación real, aquí generarías un token JWT o iniciarías una sesión.
        # Por ahora, simplemente confirmamos el login exitoso.
        return jsonify({"message": "Inicio de sesión exitoso.", "user_id": user.id}), 200
    else:
        return jsonify({"error": "Nombre de usuario o contraseña incorrectos."}), 401 # 401 Unauthorized

@app.route('/api/users/<int:user_id>/favorites', methods=['POST'])
def add_favorite(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado."}), 404

    data = request.get_json()
    product_barcode = data.get('barcode')

    if not product_barcode:
        return jsonify({"error": "Se requiere el código de barras del producto."}), 400

    # Primero, busca el producto en la base de datos local
    product = Product.query.filter_by(barcode=product_barcode).first()

    # Si el producto no existe en nuestra BD, búscalo en Open Food Facts y guárdalo
    if not product:
        off_product_data = get_product_by_barcode(product_barcode)
        if off_product_data:
            try:
                product = Product(
                    barcode=off_product_data['barcode'],
                    name=off_product_data['name'],
                    nutriscore=off_product_data['nutriscore'],
                    ecoscore=off_product_data['ecoscore'],
                    category=off_product_data['category']
                )
                db.session.add(product)
                db.session.commit()
                print(f"Producto {product_barcode} guardado desde Open Food Facts antes de añadir a favoritos.")
            except Exception as e:
                db.session.rollback()
                print(f"Error al guardar producto desde Open Food Facts para favoritos: {e}")
                return jsonify({"error": "Error interno al procesar el producto para favoritos."}), 500
        else:
            return jsonify({"error": f"Producto con código de barras '{product_barcode}' no encontrado en Open Food Facts."}), 404

    # Verificar si el producto ya es favorito
    if product in user.favorites:
        return jsonify({"message": "El producto ya está en favoritos."}), 200 # O 409 Conflict

    user.favorites.append(product)
    try:
        db.session.commit()
        return jsonify({"message": "Producto añadido a favoritos.", "product_id": product.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error al añadir producto a favoritos: {e}")
        return jsonify({"error": "Error interno al añadir producto a favoritos."}), 500


@app.route('/api/users/<int:user_id>/favorites/<string:barcode>', methods=['DELETE'])
def remove_favorite(user_id, barcode):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado."}), 404

    product = Product.query.filter_by(barcode=barcode).first()
    if not product:
        return jsonify({"error": "Producto no encontrado."}), 404

    if product not in user.favorites:
        return jsonify({"message": "El producto no está en favoritos de este usuario."}), 404 # O 200 OK si ya no está

    user.favorites.remove(product)
    try:
        db.session.commit()
        return jsonify({"message": "Producto eliminado de favoritos."}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar producto de favoritos: {e}")
        return jsonify({"error": "Error interno al eliminar producto de favoritos."}), 500

@app.route('/api/users/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado."}), 404

    # Obtener los productos favoritos y formatearlos para la respuesta JSON
    favorite_products = []
    for product in user.favorites:
        favorite_products.append({
            "id": product.id,
            "barcode": product.barcode,
            "name": product.name,
            "nutriscore": product.nutriscore,
            "ecoscore": product.ecoscore,
            "category": product.category
        })

    return jsonify(favorite_products), 200


# --- Punto de entrada para ejecutar la aplicación ---
if __name__ == '__main__':
    # Crear las tablas en la base de datos si no existen
    with app.app_context():
        db.create_all()
        print("Base de datos y tablas creadas (si no existían).")

    app.run(debug=True)