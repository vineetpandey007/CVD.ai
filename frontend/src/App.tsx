import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Scene from './components/Scene';
import Nav from './components/Nav';
import Footer from './components/Footer';
import Landing from './pages/Landing';
import Analyzer from './pages/Analyzer';
import Results from './pages/Results';
import ModelCard from './pages/ModelCard';
import History from './pages/History'; // <-- The missing import!

function App() {
  return (
    <BrowserRouter>
      {/* Removed the solid bg-gray-950 so the WebGL particles are visible! */}
      <div className="relative min-h-screen flex flex-col text-gray-900 dark:text-gray-100 transition-colors duration-300">
        
        {/* The 3D Background */}
        <Scene />
        
        {/* Detailed Navigation */}
        <Nav />
        
        {/* Main Content */}
        <div className="flex-grow z-10 flex flex-col">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/analyzer" element={<Analyzer />} />
            <Route path="/results" element={<Results />} />
            <Route path="/model" element={<ModelCard />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </div>

        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;