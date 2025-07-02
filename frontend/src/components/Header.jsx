import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom'; 
import './Header.css';

function Header() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const navigate = useNavigate();

  
  useEffect(() => {
    const userId = localStorage.getItem('user_id');
    const storedUsername = localStorage.getItem('username');
    if (userId && storedUsername) {
      setIsLoggedIn(true);
      setUsername(storedUsername);
    } else {
      setIsLoggedIn(false);
      setUsername('');
    }
  }, []); 

  const handleLogout = () => {
    localStorage.removeItem('user_id'); 
    localStorage.removeItem('username'); 
    setIsLoggedIn(false);
    setUsername('');
    alert('Has cerrado sesión.');
    navigate('/login'); 
  };

  return (
    <header className="app-header">
      <h1><Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Ecotrack 🌿</Link></h1> 
      <nav>
        <ul className="nav-list">
          <li><Link to="/">Dashboard</Link></li>
          <li><Link to="/scan-product">Escanear Producto</Link></li> 
          {isLoggedIn && <li><Link to="/favorites">Mis Favoritos</Link></li>} {/* Mostrar solo si logueado */}
          <li><Link to="/emissions">Emisiones CO2</Link></li> 
        

          {!isLoggedIn ? (
            <>
              <li><Link to="/register">Registrar</Link></li>
              <li><Link to="/login">Login</Link></li>
            </>
          ) : (
            <>
              <li style={{ color: 'white', fontWeight: 'bold' }}>Hola, {username}</li>
              <li><button onClick={handleLogout} className="logout-button">Logout</button></li>
            </>
          )}
        </ul>
      </nav>
    </header>
  );
}

export default Header;