import { BrowserRouter, Route, Routes } from "react-router-dom";
import SoftAurora from "./components/SoftAurora.jsx";
import { Nav } from "./components/Nav";
import { Footer } from "./components/Footer";
import Analyzer from "./pages/Analyzer";
import Landing from "./pages/Landing";
import Results from "./pages/Results";

function App() {
  return (
    <BrowserRouter>
      {/* Background layer. No pointer-events-none here on purpose — the
          aurora's enableMouseInteraction relies on receiving mousemove
          events. This is safe: normal DOM stacking means clicks and
          hovers over actual page content (nav, buttons, links) above it
          are still handled by that content, not the canvas underneath.
          The aurora only "sees" the mouse in empty gaps between content. */}
      <div className="fixed inset-0 z-0">
        <SoftAurora
          speed={0.6}
          scale={1.5}
          brightness={1.0}
          color1="#f7f7f7"
          color2="#e100ff"
          noiseFrequency={2.5}
          noiseAmplitude={1.0}
          bandHeight={0.5}
          bandSpread={1.0}
          octaveDecay={0.1}
          layerOffset={0}
          colorSpeed={1.0}
          enableMouseInteraction={true}
          mouseInfluence={0.25}
        />
      </div>

      <div className="relative z-10">
        <Nav />
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/analyzer" element={<Analyzer />} />
          <Route path="/results/:scanId" element={<Results />} />
        </Routes>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
