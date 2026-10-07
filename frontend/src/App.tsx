import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Analyzer from './pages/Analyzer';
import Results from './pages/Results';
import ModelCard from './pages/ModelCard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/analyzer" element={<Analyzer />} />
        <Route path="/results" element={<Results />} />
        <Route path="/model" element={<ModelCard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;