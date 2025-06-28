// src/App.jsx
import './App.css';
import Header from './components/Header';
import Footer from './components/Footer';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Register from './pages/Register'; // Lo crearemos ahora
import Login from './pages/Login';       // Lo crearemos ahora
import ProductScanner from './pages/ProductScanner'; // Lo crearemos después
import Favorites from './pages/Favorites'; // Lo crearemos después
import Emissions from './pages/Emissions'; // Lo crearemos después

function App() {
  return (
    <Router>
      <div className="App">
        <Header />

        <main className="app-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            {/* Las siguientes dos rutas las dejaremos, aunque no estén en el backend de Flask actual.
                Las renombraremos o eliminaremos si no las vas a usar. */}
            

            {/* ¡Nuevas Rutas! */}
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/scan-product" element={<ProductScanner />} /> {/* Ruta para el escáner/búsqueda de productos */}
            <Route path="/favorites" element={<Favorites />} /> {/* Ruta para ver favoritos */}
            <Route path="/emissions" element={<Emissions />} /> {/* Ruta para emisiones */}

            {/* Ruta para un error 404 */}
            <Route path="*" element={<h2>404: Página no encontrada</h2>} />
          </Routes>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;