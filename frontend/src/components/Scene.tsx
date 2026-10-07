import { ParticleNetwork } from "../shaders/neuform-isolated/NeuformBatchEffects";
import "../shaders/threeui.css";

export default function Scene() {
  return (
    <div className="shader-frame w-full h-full absolute inset-0 -z-10 pointer-events-none">
      <ParticleNetwork
        mode="dark"
        speed={1.00}
        size={1.00}
        length={1.00}
        density={1.00}
        opacity={1.00}
        hue={0}
        saturation={1.00}
        brightness={1.00}
      />
    </div>
  );
}