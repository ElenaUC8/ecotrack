// src/App.jsx
import './App.css';
import Header from './components/Header';
import Footer from './components/Footer';

function App() {
  return (
    <div className="App">
      <Header />
      <main className="app-content">
        {/* Aquí irán las diferentes páginas o secciones de tu aplicación */}
        <h2>Bienvenido a Ecotrack</h2>
        <p>Empieza a registrar y visualizar tus datos de sostenibilidad.</p>
      </main>
      <Footer />
    </div>
  );
}

export default App;