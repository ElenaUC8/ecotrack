import unittest
from flask import json
from app import app, db, User, Product, RegionalCo2Emission, bcrypt # Importa todos los componentes necesarios
from unittest.mock import patch, MagicMock # Para simular llamadas a APIs externas
import os

# --- CLASE DE TESTS PARA LA APLICACIÓN FLASK ---
class FlaskAppTests(unittest.TestCase):

    # Método que se ejecuta ANTES de cada test
    def setUp(self):
        # 1. Configurar la aplicación para testing
        app.config['TESTING'] = True
        # Usar una base de datos SQLite en memoria para que los tests sean rápidos y no afecten a la BD real
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client() # Cliente de prueba de Flask para simular peticiones

        # 2. Crear las tablas de la base de datos en el contexto de la aplicación
        with app.app_context():
            db.create_all()
            # 3. Cargar datos de prueba para las emisiones (se cargarán solo si no existen)
            self._load_test_emissions_data()
            # 4. Registrar un usuario de prueba para tests de autenticación/favoritos
            self.test_user = User(username='testuser', email='test@example.com')
            self.test_user.set_password('testpassword')
            db.session.add(self.test_user)
            db.session.commit()
            self.test_user_id = self.test_user.id # Guardar el ID del usuario de prueba

    # Método que se ejecuta DESPUÉS de cada test
    def tearDown(self):
        # Limpiar la sesión de la base de datos y eliminar todas las tablas
        with app.app_context():
            db.session.remove() # Cierra la sesión
            db.drop_all() # Elimina todas las tablas de la base de datos en memoria

    # --- Ayudante: Cargar datos de emisiones para tests ---
    def _load_test_emissions_data(self):
        """Carga un conjunto mínimo de datos de emisiones de prueba directamente en la BD."""
        # Asegúrate de que los datos coincidan con lo que buscarías en los tests
        euskadi_2021 = RegionalCo2Emission(region_name='C.A. de Euskadi', year=2021, total_co2_tonnes=14828603.0)
        euskadi_2022 = RegionalCo2Emission(region_name='C.A. de Euskadi', year=2022, total_co2_tonnes=16006313.0)
        db.session.add(euskadi_2021)
        db.session.add(euskadi_2022)
        db.session.commit()

    # --- TESTS FUNCIONALES ---

    # Test de la ruta principal
    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200) #
        self.assertIn(b"Bienvenido al backend", response.data) #

    # --- TESTS DE GESTIÓN DE USUARIOS ---

    def test_register_user_success(self):
        response = self.app.post('/api/users/register',
                                 data=json.dumps({"username": "newuser", "email": "new@example.com", "password": "newpassword"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201) #
        self.assertIn(b"Usuario registrado exitosamente", response.data) #
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(user)

    def test_register_user_duplicate_username(self):
        # Intenta registrar el usuario de prueba de nuevo
        response = self.app.post('/api/users/register',
                                 data=json.dumps({"username": "testuser", "email": "another@example.com", "password": "password123"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 409) #
        self.assertIn(b"El nombre de usuario ya existe.", response.data) #

    def test_register_user_duplicate_email(self):
        # Intenta registrar el usuario de prueba con el mismo email
        response = self.app.post('/api/users/register',
                                 data=json.dumps({"username": "anotheruser", "email": "test@example.com", "password": "password123"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 409) #
        self.assertIn(b"El email ya est\xc3\xa1 registrado.", response.data) # (Manejo de caracteres especiales)

    def test_register_user_missing_fields(self):
        response = self.app.post('/api/users/register',
                                 data=json.dumps({"username": "incomplete"}), # Falta email y password
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400) #
        self.assertIn(b"Se requieren nombre de usuario, email y contrase\xc3\xb1a.", response.data) #

    def test_login_user_success(self):
        response = self.app.post('/api/users/login',
                                 data=json.dumps({"username": "testuser", "password": "testpassword"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200) #
        self.assertIn(b"Inicio de sesi\xc3\xb3n exitoso.", response.data) #

    def test_login_user_incorrect_password(self):
        response = self.app.post('/api/users/login',
                                 data=json.dumps({"username": "testuser", "password": "wrongpassword"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 401) #
        self.assertIn(b"Nombre de usuario o contrase\xc3\xb1a incorrectos.", response.data) #

    def test_login_user_non_existent(self):
        response = self.app.post('/api/users/login',
                                 data=json.dumps({"username": "nonexistent", "password": "anypassword"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 401) #
        self.assertIn(b"Nombre de usuario o contrase\xc3\xb1a incorrectos.", response.data) #

    # --- TESTS DE BÚSQUEDA DE PRODUCTOS ---

    @patch('app.get_product_by_barcode') # Mockea la función externa openfoodfacts_api.get_product_by_barcode
    def test_search_product_in_local_db(self, mock_get_product):
        # Añadir un producto de prueba directamente a la BD para simular que ya existe localmente
        with app.app_context():
            existing_product = Product(barcode='1234567890123', name='Leche Test', nutriscore='B', ecoscore='A', category='Lacteos')
            db.session.add(existing_product)
            db.session.commit()

        response = self.app.get('/api/products/search?barcode=1234567890123')
        self.assertEqual(response.status_code, 200) #
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Leche Test') #
        mock_get_product.assert_not_called() # Asegura que la API externa NO fue llamada

    @patch('app.get_product_by_barcode')
    def test_search_product_from_openfoodfacts_and_save(self, mock_get_product):
        # Simula una respuesta exitosa de Open Food Facts
        mock_get_product.return_value = {
            'barcode': '9876543210987',
            'name': 'Pan Integral Mock',
            'nutriscore': 'A',
            'ecoscore': 'B',
            'category': 'Panaderia'
        }

        response = self.app.get('/api/products/search?barcode=9876543210987')
        self.assertEqual(response.status_code, 201) # (Se espera 201 Created porque se guarda)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Pan Integral Mock') #
        mock_get_product.assert_called_once_with('9876543210987') # Asegura que la API externa FUE llamada

        # Verificar que el producto fue guardado en la BD
        with app.app_context():
            product = Product.query.filter_by(barcode='9876543210987').first()
            self.assertIsNotNone(product)
            self.assertEqual(product.name, 'Pan Integral Mock')

    @patch('app.get_product_by_barcode')
    def test_search_product_not_found(self, mock_get_product):
        # Simula que Open Food Facts no encuentra el producto
        mock_get_product.return_value = None

        response = self.app.get('/api/products/search?barcode=1111111111111')
        self.assertEqual(response.status_code, 404) #
        self.assertIn(b"Producto con c\xc3\xb3digo de barras '1111111111111' no encontrado.", response.data) #

    def test_search_product_missing_barcode(self):
        response = self.app.get('/api/products/search') # Sin parámetro barcode
        self.assertEqual(response.status_code, 400) #
        self.assertIn(b"Se requiere un c\xc3\xb3digo de barras para la b\xc3\xbasqueda.", response.data) #

    # --- TESTS DE GESTIÓN DE FAVORITOS ---

    @patch('app.get_product_by_barcode')
    def test_add_favorite_success(self, mock_get_product):
        # Simula un producto que se añade a favoritos (puede venir de OFF)
        mock_get_product.return_value = {
            'barcode': '1122334455667',
            'name': 'Agua Mineral',
            'nutriscore': 'A',
            'ecoscore': 'A',
            'category': 'Bebidas'
        }
        response = self.app.post(f'/api/users/{self.test_user_id}/favorites',
                                 data=json.dumps({"barcode": "1122334455667"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201) #
        self.assertIn(b"Producto a\xc3\xb1adido a favoritos.", response.data) #

        with app.app_context():
            user = User.query.get(self.test_user_id)
            self.assertEqual(len(user.favorites), 1)
            self.assertEqual(user.favorites[0].barcode, '1122334455667')

    def test_add_favorite_product_already_favorited(self):
        with app.app_context():
            product = Product(barcode='2233445566778', name='Yogur', nutriscore='B', ecoscore='B', category='Lacteos')
            db.session.add(product)
            self.test_user.favorites.append(product)
            db.session.commit()

        response = self.app.post(f'/api/users/{self.test_user_id}/favorites',
                                 data=json.dumps({"barcode": "2233445566778"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200) #
        self.assertIn(b"El producto ya est\xc3\xa1 en favoritos.", response.data) #

    @patch('app.get_product_by_barcode')
    def test_add_favorite_product_not_found_off(self, mock_get_product):
        mock_get_product.return_value = None # OFF no encuentra el producto
        response = self.app.post(f'/api/users/{self.test_user_id}/favorites',
                                 data=json.dumps({"barcode": "9999999999999"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 404) #
        self.assertIn(b"Producto con c\xc3\xb3digo de barras '9999999999999' no encontrado en Open Food Facts.", response.data) #

    def test_add_favorite_user_not_found(self):
        response = self.app.post('/api/users/999/favorites',
                                 data=json.dumps({"barcode": "1234567890123"}),
                               _type='application/json')
        self.assertEqual(response.status_code, 404) #
        self.assertIn(b"Usuario no encontrado.", response.data) #

    def test_get_favorites_success(self):
        # Añadir un producto a favoritos para el test_user
        with app.app_context():
            product_fav = Product(barcode='3344556677889', name='Manzana', nutriscore='A', ecoscore='A', category='Frutas')
            db.session.add(product_fav)
            db.session.commit()
            self.test_user.favorites.append(product_fav)
            db.session.commit()

        response = self.app.get(f'/api/users/{self.test_user_id}/favorites')
        self.assertEqual(response.status_code, 200) #
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Manzana') #

    def test_get_favorites_no_favorites(self):
        response = self.app.get(f'/api/users/{self.test_user_id}/favorites')
        self.assertEqual(response.status_code, 200) #
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

    def test_get_favorites_user_not_found(self):
        response = self.app.get('/api/users/999/favorites')
        self.assertEqual(response.status_code, 404) #
        self.assertIn(b"Usuario no encontrado.", response.data) #

    def test_remove_favorite_success(self):
        # Añadir un producto a favoritos para luego eliminarlo
        with app.app_context():
            product_to_remove = Product(barcode='4455667788990', name='Cereal', nutriscore='C', ecoscore='C', category='Desayuno')
            db.session.add(product_to_remove)
            db.session.commit()
            self.test_user.favorites.append(product_to_remove)
            db.session.commit()

        response = self.app.delete(f'/api/users/{self.test_user_id}/favorites/4455667788990')
        self.assertEqual(response.status_code, 200) #
        self.assertIn(b"Producto eliminado de favoritos.", response.data) #

        with app.app_context():
            user = User.query.get(self.test_user_id)
            self.assertNotIn(product_to_remove, user.favorites) # Verifica que ya no está en favoritos

    def test_remove_favorite_product_not_in_favorites(self):
        # Intenta eliminar un producto que el usuario no tiene como favorito
        with app.app_context():
            product_not_fav = Product(barcode='5566778899001', name='Galletas', nutriscore='D', ecoscore='B', category='Snacks')
            db.session.add(product_not_fav)
            db.session.commit()

        response = self.app.delete(f'/api/users/{self.test_user_id}/favorites/5566778899001')
        self.assertEqual(response.status_code, 404) #
        self.assertIn(b"El producto no est\xc3\xa1 en favoritos de este usuario.", response.data) #

    def test_remove_favorite_user_not_found(self):
        response = self.app.delete('/api/users/999/favorites/1234567890123')
        self.assertEqual(response.status_code, 404) #
        self.assertIn(b"Usuario no encontrado.", response.data) #

    # --- TESTS DE CONSULTA DE EMISIONES ---

    def test_get_emissions_success(self):
        response = self.app.get('/api/emissions?year=2021&region=C.A.%20de%20Euskadi')
        self.assertEqual(response.status_code, 200) #
        data = json.loads(response.data)
        self.assertEqual(data['region_name'], 'C.A. de Euskadi') #
        self.assertEqual(data['year'], 2021) #
        self.assertAlmostEqual(data['total_co2_tonnes'], 14828603.0) #

    def test_get_emissions_not_found(self):
        response = self.app.get('/api/emissions?year=1900&region=Region%20Inexistente')
        self.assertEqual(response.status_code, 404) #
        self.assertIn(b"No se encontraron datos de emisi\xc3\xb3n para la regi\xc3\xb3n 'Region Inexistente' y el a\xc3\xb1o '1900'.", response.data) #

    def test_get_emissions_missing_params(self):
        response = self.app.get('/api/emissions?year=2021') # Falta la región
        self.assertEqual(response.status_code, 400) #
        self.assertIn(b"Se requieren los par\xc3\xa1metros 'region' y 'year'.", response.data) #

        response = self.app.get('/api/emissions?region=C.A.%20de%20Euskadi') # Falta el año
        self.assertEqual(response.status_code, 400) #
        self.assertIn(b"Se requieren los par\xc3\xa1metros 'region' y 'year'.", response.data) #

    def test_get_emissions_invalid_year(self):
        response = self.app.get('/api/emissions?year=invalid&region=C.A.%20de%20Euskadi')
        self.assertEqual(response.status_code, 400) #
        self.assertIn(b"El par\xc3\xa1metro 'year' debe ser un n\xc3\xba", response.data) # (El mensaje completo sería '...número entero válido.')

if __name__ == '__main__':
    unittest.main()