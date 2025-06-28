// src/components/Footer.jsx
import React from 'react';
import './Footer.css'; // Crearemos este archivo para estilos específicos

function Footer() {
  return (
    <footer className="app-footer">
      <p>&copy; {new Date().getFullYear()} Ecotrack. Todos los derechos reservados.</p>
      <p>Hecho con ❤️ para el planeta.</p>
    </footer>
  );
}

export default Footer;