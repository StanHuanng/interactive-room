import { useMemo } from 'react'
import { useGLTF } from '@react-three/drei'
import type { ThreeElements } from '@react-three/fiber'
import { Mesh } from 'three'

const modelPaths = {
  sofa: '/models/sofa.glb',
  desk: '/models/desk.glb',
  mac: '/models/mac.glb',
  chair: '/models/chair.glb',
  room: '/models/room.glb',
} as const

export type ModelProps = Omit<ThreeElements['group'], 'children' | 'dispose'>

type AssetProps = ModelProps & { asset: keyof typeof modelPaths }

// Preload through the same cache used by useGLTF and the Room Suspense boundary.
Object.values(modelPaths).forEach((path) => useGLTF.preload(path))

export function Model({ asset, ...props }: AssetProps) {
  const { scene } = useGLTF(modelPaths[asset])
  const instance = useMemo(() => {
    // Each instance owns its hierarchy; cached geometry/materials remain shared.
    const clone = scene.clone(true)
    clone.traverse((object) => {
      if (object instanceof Mesh) {
        object.castShadow = true
        object.receiveShadow = true
      }
    })
    return clone
  }, [scene])

  return (
    <group {...props} dispose={null}>
      <primitive object={instance} />
    </group>
  )
}
