import React, { useState } from 'react';
import './Emissions.css'; 

function Emissions() {
  const [year, setYear] = useState('');
  const [region, setRegion] = useState('');
  const [emissionData, setEmissionData] = useState(null); 
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (event) => {
    event.preventDefault();
    setError('');
    setEmissionData(null); 
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
            <option value="1990">1990</option>
            <option value="1991">1991</option>
            <option value="1992">1992</option>
            <option value="1993">1993</option>
            <option value="1994">1994</option>
            <option value="1995">1995</option>
            <option value="1996">1996</option>
            <option value="1997">1997</option>
            <option value="1998">1998</option>
            <option value="1999">1999</option>
            <option value="2000">2000</option>
            <option value="2001">2001</option>
            <option value="2002">2002</option>
            <option value="2003">2003</option>
            <option value="2004">2004</option>
            <option value="2005">2005</option>
            <option value="2006">2006</option>
            <option value="2007">2007</option>
            <option value="2008">2008</option>
            <option value="2009">2009</option>
            <option value="2010">2010</option>
            <option value="2011">2011</option>
            <option value="2012">2012</option>
            <option value="2013">2013</option>
            <option value="2014">2014</option>
            <option value="2015">2015</option>
            <option value="2016">2016</option>
            <option value="2017">2017</option>
            <option value="2018">2018</option>
            <option value="2019">2019</option>
            <option value="2020">2020</option>
            <option value="2021">2021</option>
            <option value="2022">2022</option>
            
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