import { Environment, Lightformer } from '@react-three/drei'
import { roomLayout } from './layout'

// Soft 2400–3000K practical lights, with a gentle 3000K ceiling fill.
export function Lights() {
  return <>
    <Environment resolution={128} frames={1} environmentIntensity={0.65}>
      <Lightformer position={[0, 5, 0]} rotation={[Math.PI / 2, 0, 0]}
        scale={[6, 5, 1]} intensity={1.3} color="#ffe0bf" />
      <Lightformer position={[5, 2, 0]} rotation={[0, -Math.PI / 2, 0]}
        scale={[3, 3, 1]} intensity={1} color="#ffe0bf" />
      <Lightformer position={[0, 2, 5]} scale={[5, 3, 1]}
        intensity={0.6} color="#ffd2a1" />
    </Environment>
    <ambientLight intensity={0.24} color="#ffdeba" />
    <hemisphereLight args={['#ffdfbc', '#4c3025', 0.35]} />
    <directionalLight position={[1.8, 2.65, 1.2]} intensity={1.35} color="#ffdfbb"
      castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048}
      shadow-camera-left={-4} shadow-camera-right={4} shadow-camera-top={4}
      shadow-camera-bottom={-4} shadow-normalBias={0.025} />
    <pointLight position={[roomLayout.mushroom_lamp.position[0], 0.81, roomLayout.mushroom_lamp.position[2]]}
      intensity={3} color="#ffca8c" distance={3} decay={2} />
    <pointLight position={[roomLayout.desk_lamp.position[0], 1.06, roomLayout.desk_lamp.position[2]]}
      intensity={2.4} color="#ffd2a1" distance={3} decay={2} />
    {[0.50, 1.01, 1.52, 2.01].map((height) => <pointLight key={height}
      position={[-2.49, height, -0.55]} intensity={1.2} color="#ffca8c" distance={2.5} decay={2} />)}
    <pointLight position={[2.29, 1.22, 0.89]} intensity={4} color="#ffd2a1" distance={4} decay={2} />
    <pointLight position={[-2.80, 1.65, -1.81]} intensity={1.4} color="#ffd2a1" distance={3} decay={2} />
  </>
}
