// src/pages/Emissions.jsx
import React, { useState } from 'react';
import './Emissions.css'; // Crearemos este archivo para estilos específicos

function Emissions() {
  const [year, setYear] = useState('');
  const [region, setRegion] = useState('');
  const [emissionData, setEmissionData] = useState(null); // Para almacenar los datos de emisión
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (event) => {
    event.preventDefault();
    setError('');
    setEmissionData(null); // Limpiar datos anteriores
    setLoading(true);

    if (!year || !region) {
      setError('Por favor, selecciona un año y una región.');
      setLoading(false);
      return;
    }

    try {
      // La URL incluye los parámetros de consulta 'year' y 'region'
      const response = await fetch(`http://localhost:5000/api/emissions?year=${year}&region=${region}`);
      const data = await response.json();

      if (!response.ok) {
        // Manejar errores como 404 (datos no encontrados) o 500
        throw new Error(data.error || data.message || 'Error al obtener datos de emisiones');
      }

      setEmissionData(data); // Guarda los datos de emisión
      console.log('Datos de emisión encontrados:', data);

    } catch (err) {
      console.error('Error en la búsqueda de emisiones:', err);
      setError(err.message || 'Error desconocido al buscar emisiones.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="emissions-container">
      <h2>Consulta de Emisiones de CO2</h2>
      <form onSubmit={handleSearch} className="emissions-search-form">
        <div className="form-group">
          <label htmlFor="year">Año:</label>
          <select
            id="year"
            value={year}
            onChange={(e) => setYear(e.target.value)}
            required
          >
            <option value="">Selecciona un año</option>
            {/* Puedes ajustar los años según los datos disponibles en tu backend/API externa */}
            <option value="2020">2020</option>
            <option value="2021">2021</option>
            <option value="2022">2022</option>
            <option value="2023">2023</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="region">Región:</label>
          <input
            type="text"
            id="region"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            placeholder="Ej. España, Francia"
            required
          />
        </div>

        <button type="submit" className="search-emissions-button" disabled={loading}>
          {loading ? 'Buscando...' : 'Buscar Emisiones'}
        </button>
      </form>

      {error && <p className="error-message">{error}</p>}

      {emissionData && (
        <div className="emission-results">
          <h3>Datos de Emisiones para {emissionData.region} en {emissionData.year}</h3>
          {emissionData.total_co2_tonnes ? (
            <p>
              <strong>Emisiones de CO2:</strong> {emissionData.total_co2_tonnes.toFixed(2)} toneladas
            </p>
          ) : (
            <p>No se encontraron datos de emisiones para el año y la región seleccionados.</p>
          )}
          {emissionData.source && <p className="source-info">Fuente: {emissionData.source}</p>}
        </div>
      )}
    </section>
  );
}

export default Emissions;