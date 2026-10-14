import { InteractionProvider } from './components/interaction/Interaction'
import { Canvas } from '@react-three/fiber'
import { PlayerCamera } from './components/camera/PlayerCamera'
import { Lights } from './components/room/Lights'
import { Room } from './components/room/Room'
import { Hud } from './components/ui/Hud'

export default function App() {
  return (
    <InteractionProvider>
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <Canvas shadows gl={{ antialias: true }}>
        <color attach="background" args={['#1a1a1a']} />
        <PlayerCamera />
        <Lights />
        <Room />
      </Canvas>
      <Hud />
    </div>
    </InteractionProvider>
  )
}
