import { useMemo } from 'react'
import { useGLTF } from '@react-three/drei'
import type { ThreeElements } from '@react-three/fiber'
import { Mesh } from 'three'

const modelPaths = {
  sofa: `${import.meta.env.BASE_URL}models/sofa.glb`,
  ottoman: `${import.meta.env.BASE_URL}models/ottoman.glb`,
  desk: `${import.meta.env.BASE_URL}models/desk.glb`,
  mac: `${import.meta.env.BASE_URL}models/mac.glb`,
  chair: `${import.meta.env.BASE_URL}models/chair.glb`,
  room: `${import.meta.env.BASE_URL}models/room.glb`,
  rug: `${import.meta.env.BASE_URL}models/rug.glb`,
  side_table: `${import.meta.env.BASE_URL}models/side_table.glb`,
  mushroom_lamp: `${import.meta.env.BASE_URL}models/mushroom_lamp.glb`,
  desk_lamp: `${import.meta.env.BASE_URL}models/desk_lamp.glb`,
  bookshelf: `${import.meta.env.BASE_URL}models/bookshelf.glb`,
  corkboard: `${import.meta.env.BASE_URL}models/corkboard.glb`,
  decor: `${import.meta.env.BASE_URL}models/decor.glb`,

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
