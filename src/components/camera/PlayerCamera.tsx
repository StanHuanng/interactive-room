import { PerspectiveCamera } from '@react-three/drei'

/**
 * Stub first-person camera. WASD + pointer-lock controls come in MVP phase.
 */
export function PlayerCamera() {
  return <PerspectiveCamera makeDefault position={[0, 1.6, 3]} fov={70} near={0.1} far={100} />
}
