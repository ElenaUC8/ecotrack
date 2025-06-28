// src/pages/Register.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom'; // Para redirigir al usuario
import './Auth.css'; // Crearemos un CSS común para autenticación

function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate(); // Hook para la navegación programática

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(''); // Limpia errores anteriores

    try {
      const response = await fetch('http://localhost:5000/api/users/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Si la respuesta no es 2xx, es un error (ej. 400, 409, 500)
        throw new Error(data.error || 'Error en el registro');
      }

      console.log('Registro exitoso:', data);
      alert('¡Usuario registrado exitosamente!');
      navigate('/login'); // Redirige al usuario a la página de login

    } catch (err) {
      console.error('Error al registrar:', err.message);
      setError(err.message); // Muestra el mensaje de error al usuario
    }
  };

  return (
    <section className="auth-container">
      <h2>Registrarse en Ecotrack</h2>
      <form onSubmit={handleSubmit} className="auth-form">
        {error && <p className="error-message">{error}</p>} {/* Muestra el error si existe */}

        <div className="form-group">
          <label htmlFor="username">Nombre de Usuario:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Contraseña:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button type="submit" className="auth-button">Registrar</button>
      </form>
      <p className="auth-link-text">
        ¿Ya tienes cuenta? <Link to="/login">Inicia sesión aquí</Link>
      </p>
    </section>
  );
}

export default Register;