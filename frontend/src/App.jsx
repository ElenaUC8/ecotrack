import './App.css';
import Header from './components/Header';
import Footer from './components/Footer';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Register from './pages/Register'; 
import Login from './pages/Login';       
import ProductScanner from './pages/ProductScanner'; 
import Favorites from './pages/Favorites'; 
import Emissions from './pages/Emissions'; 

function App() {
  return (
    <Router>
      <div className="App">
        <Header />

        <main className="app-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/scan-product" element={<ProductScanner />} /> 
            <Route path="/favorites" element={<Favorites />} /> 
            <Route path="/emissions" element={<Emissions />} /> 

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