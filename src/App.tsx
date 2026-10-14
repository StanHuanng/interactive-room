import { InteractionProvider } from './components/interaction/Interaction'
import { Canvas } from '@react-three/fiber'
import { PlayerCamera } from './components/camera/PlayerCamera'
import { Lights } from './components/room/Lights'
import { Room } from './components/room/Room'
import { Hud } from './components/ui/Hud'
import { DetailPanels } from './components/ui/DetailPanels'
import { useInteraction } from './components/interaction/useInteraction'

export default function App() {
  return (
    <InteractionProvider>
      <Study />
    </InteractionProvider>
  )
}

function Study() {
  const { focus, closeFocus } = useInteraction()
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <Canvas shadows gl={{ antialias: true }} onPointerMissed={(event) => {
        if (event.type === 'click' && focus) closeFocus()
      }}>
        <color attach="background" args={['#1a1a1a']} />
        <PlayerCamera />
        <Lights />
        <Room />
      </Canvas>
      <Hud />
      <DetailPanels />
    </div>
  )
}
