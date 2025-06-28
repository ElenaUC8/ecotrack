// src/pages/ProductScanner.jsx
import React, { useState, useEffect } from 'react';
import './ProductScanner.css'; // Crearemos este archivo para estilos específicos

function ProductScanner() {
  const [barcode, setBarcode] = useState('');
  const [product, setProduct] = useState(null); // Para almacenar los datos del producto encontrado
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false); // Para indicar que la búsqueda está en curso

  // Obtener el user_id del localStorage para las operaciones de favoritos
  const userId = localStorage.getItem('user_id');

  const handleSearch = async (event) => {
    event.preventDefault();
    setError('');
    setProduct(null); // Limpiar producto anterior
    setLoading(true);

    if (!barcode) {
      setError('Por favor, introduce un código de barras.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`http://localhost:5000/api/products/search?barcode=${barcode}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Error al buscar el producto');
      }

      setProduct(data); // Guarda los datos del producto
      console.log('Producto encontrado:', data);

    } catch (err) {
      console.error('Error en la búsqueda:', err);
      setError(err.message || 'Error desconocido al buscar el producto.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddFavorite = async () => {
    if (!userId) {
      setError('Debes iniciar sesión para añadir favoritos.');
      return;
    }
    if (!product || !product.barcode) {
      setError('No hay producto seleccionado para añadir a favoritos.');
      return;
    }

    try {
      const response = await fetch(`http://localhost:5000/api/users/${userId}/favorites`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ barcode: product.barcode }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Error al añadir a favoritos');
      }

      alert(data.message || 'Producto añadido a favoritos!');
      console.log('Favorito añadido:', data);

    } catch (err) {
      console.error('Error al añadir favorito:', err);
      setError(err.message || 'Error desconocido al añadir a favoritos.');
    }
  };

  return (
    <section className="product-scanner-container">
      <h2>Escanear o Buscar Producto</h2>
      <form onSubmit={handleSearch} className="product-search-form">
        <div className="form-group">
          <label htmlFor="barcode">Código de Barras:</label>
          <input
            type="text"
            id="barcode"
            value={barcode}
            onChange={(e) => setBarcode(e.target.value)}
            placeholder="Ej. 8410000000000"
            required
          />
        </div>
        <button type="submit" className="search-button" disabled={loading}>
          {loading ? 'Buscando...' : 'Buscar Producto'}
        </button>
      </form>

      {error && <p className="error-message">{error}</p>}

      {product && (
        <div className="product-details">
          <h3>{product.name}</h3>
          <p><strong>Código de Barras:</strong> {product.barcode}</p>
          <p><strong>Nutriscore:</strong> {product.nutriscore || 'N/A'}</p>
          <p><strong>Ecoscore:</strong> {product.ecoscore || 'N/A'}</p>
          <p><strong>Categoría:</strong> {product.category || 'N/A'}</p>
          {
            userId ? ( // Solo muestra el botón de favorito si el usuario está logueado
              <button onClick={handleAddFavorite} className="favorite-button">
                Añadir a Favoritos
              </button>
            ) : (
              <p className="login-prompt">Inicia sesión para añadir a favoritos.</p>
            )
          }
        </div>
      )}
    </section>
  );
}

export default ProductScanner;