// src/pages/Favorites.jsx
import React, { useState, useEffect } from 'react';
import './Favorites.css';

function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const userId = localStorage.getItem('user_id');

  const fetchFavorites = async () => {
    if (!userId) {
      setError('Debes iniciar sesión para ver tus favoritos.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`http://localhost:5000/api/users/${userId}/favorites`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Error al cargar los favoritos');
      }

      setFavorites(data);
      console.log('Favoritos cargados:', data);

    } catch (err) {
      console.error('Error al cargar los favoritos:', err);
      setError(err.message || 'Error desconocido al cargar los favoritos.');
    } finally {
      setLoading(false);
    }
  };

  // Nueva función para eliminar un favorito
  const handleDeleteFavorite = async (barcodeToDelete) => {
    if (!userId) {
      alert('Error: Debes iniciar sesión para eliminar favoritos.');
      return;
    }

    if (window.confirm('¿Estás seguro de que quieres eliminar este producto de tus favoritos?')) {
      try {
        const response = await fetch(`http://localhost:5000/api/users/${userId}/favorites/${barcodeToDelete}`, {
          method: 'DELETE',
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.message || 'Error al eliminar el producto de favoritos');
        }

        // Si la eliminación en el backend fue exitosa, actualiza el estado local
        setFavorites(favorites.filter(product => product.barcode !== barcodeToDelete));
        alert(data.message || 'Producto eliminado de favoritos.');
        console.log('Favorito eliminado:', data);

      } catch (err) {
        console.error('Error al eliminar favorito:', err);
        setError(err.message || 'Error desconocido al eliminar de favoritos.');
      }
    }
  };

  useEffect(() => {
    fetchFavorites();
  }, [userId]); // Ejecutar al cargar y si cambia el userId

  if (loading) {
    return (
      <section className="favorites-container">
        <h2>Cargando Favoritos...</h2>
        <p>Por favor, espera.</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="favorites-container">
        <h2>Error al cargar Favoritos</h2>
        <p className="error-message">{error}</p>
        {!userId && <p>Asegúrate de haber iniciado sesión.</p>}
      </section>
    );
  }

  return (
    <section className="favorites-container">
      <h2>Mis Productos Favoritos</h2>
      {favorites.length === 0 ? (
        <p>Aún no tienes productos favoritos. ¡Busca algunos y añádelos!</p>
      ) : (
        <div className="favorites-list">
          {favorites.map((product) => (
            <div key={product.id} className="favorite-item">
              <h3>{product.name}</h3>
              <p><strong>Código de Barras:</strong> {product.barcode}</p>
              <p><strong>Nutriscore:</strong> {product.nutriscore || 'N/A'}</p>
              <p><strong>Ecoscore:</strong> {product.ecoscore || 'N/A'}</p>
              <p><strong>Categoría:</strong> {product.category || 'N/A'}</p>
              <button
                onClick={() => handleDeleteFavorite(product.barcode)}
                className="remove-favorite-button"
              >
                Eliminar
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default Favorites;