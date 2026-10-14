import { useEffect, useMemo, useRef, useState } from 'react'
import { useCursor, useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { CanvasTexture, Euler, Quaternion, SRGBColorSpace, Vector3 } from 'three'
import type { Group, Mesh, MeshStandardMaterial } from 'three'
import type { ModelProps } from './Model'
import { useInteraction } from '../../interaction/useInteraction'
import placements from '../scene-layout.json'

const cardLayout = placements.corkboard.articleCard
const cardPosition = cardLayout.position as [number, number, number]
const cardSize = cardLayout.size as [number, number]

// Deterministic fibres, drawn once. No external image or runtime font download.
function surfaceTexture(paper: boolean) {
  const canvas = document.createElement('canvas')
  canvas.width = paper ? 768 : 512
  canvas.height = paper ? 512 : 256
  const ctx = canvas.getContext('2d')!
  ctx.fillStyle = paper ? '#eee2c9' : '#6d7161'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  let seed = 71
  const random = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296 }
  for (let i = 0; i < (paper ? 18000 : 24000); i++) {
    const x = random() * canvas.width, y = random() * canvas.height
    ctx.strokeStyle = random() > .5 ? 'rgba(255,247,220,.10)' : 'rgba(32,26,18,.09)'
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + random() * 3, y + random() * 2); ctx.stroke()
  }
  if (paper) {
    ctx.fillStyle = '#746a50'; ctx.font = '500 21px sans-serif'
    ctx.fillText('FIELD NOTES     /     01', 48, 64)
    ctx.fillStyle = '#343a30'; ctx.font = 'bold 43px sans-serif'
    ctx.fillText('原来，Claude 早就给', 48, 151)
    ctx.fillText('ESP32 留了个按钮', 48, 212)
    ctx.fillStyle = '#827353'; ctx.fillRect(48, 246, 90, 3)
    ctx.font = '23px sans-serif'; ctx.fillText('一块屏幕，两个按钮。', 48, 298)
    ctx.fillText('让云端任务，停到手边。', 48, 336)
    ctx.fillStyle = '#9c503b'; ctx.font = '500 21px sans-serif'
    ctx.fillText('ESP32  ×  AI', 48, 439)
    ctx.fillText('READ NOTE  ↗', 530, 439)
  }
  const texture = new CanvasTexture(canvas)
  texture.colorSpace = SRGBColorSpace
  texture.anisotropy = 4
  return texture
}

export function ArticleBoard(props: ModelProps) {
  const { nodes } = useGLTF('/models/corkboard.glb')
  // Keep the original bevels and walnut normal map, replacing only the contents.
  const frame = nodes.Large_horizontal_noticeboard_frame as Mesh
  const { focus, returning, openFocus } = useInteraction()
  const [hovered, setHovered] = useState(false)
  const card = useRef<Group>(null)
  const pin = useRef<Group>(null)
  const paper = useRef<MeshStandardMaterial>(null)
  const resources = useMemo(() => ({
    felt: surfaceTexture(false), paper: surfaceTexture(true),
    home: new Vector3(...cardPosition), target: new Vector3(),
    rotation: new Quaternion(), parentRotation: new Quaternion(),
    euler: new Euler(),
  }), [])
  const motion = useRef({ hover: 0, flight: 0 })
  useEffect(() => () => { resources.felt.dispose(); resources.paper.dispose() }, [resources])
  useCursor(hovered && !focus && !returning)
  useFrame(({ camera, clock }, rawDelta) => {
    if (!card.current?.parent) return
    const alpha = 1 - Math.exp(-7 * Math.min(rawDelta, .05))
    const active = focus === 'article'
    motion.current.flight += ((active ? 1 : 0) - motion.current.flight) * alpha
    motion.current.hover += ((hovered && !active ? 1 : 0) - motion.current.hover) * alpha
    if (active) {
      // A real 3D flight from the wall into the reader's view, facing the camera.
      resources.target.set(0, 0, -1.05).applyQuaternion(camera.quaternion).add(camera.position)
      card.current.parent.worldToLocal(resources.target)
      card.current.parent.getWorldQuaternion(resources.parentRotation).invert()
      resources.rotation.copy(resources.parentRotation).multiply(camera.quaternion)
    } else {
      resources.target.copy(resources.home)
      resources.target.setZ(resources.target.z + motion.current.hover * .065)
      resources.target.setY(resources.target.y + motion.current.hover * .012)
      resources.euler.set(-motion.current.hover * .08, motion.current.hover * .05,
        cardLayout.rotationZ + Math.sin(clock.elapsedTime * 5) * .012 * motion.current.hover)
      resources.rotation.setFromEuler(resources.euler)
    }
    card.current.position.lerp(resources.target, alpha)
    card.current.quaternion.slerp(resources.rotation, alpha)
    if (pin.current) pin.current.scale.setScalar(1 - motion.current.flight * .88)
    if (paper.current) paper.current.emissiveIntensity += ((hovered ? .1 : .015) - paper.current.emissiveIntensity) * alpha
  })
  return <group {...props}>
    <mesh geometry={frame.geometry} material={frame.material} castShadow receiveShadow dispose={null} />
    <mesh position={[0, 0, .037]} receiveShadow>
      <boxGeometry args={[1.77, .84, .018]} />
      <meshStandardMaterial map={resources.felt} bumpMap={resources.felt} bumpScale={.003} roughness={1} />
    </mesh>
    {/* Subtle brass corner fasteners keep the board grounded in the room. */}
    {[-.898, .898].flatMap((x) => [-.433, .433].map((y) => <mesh key={`${x}:${y}`} position={[x, y, .035]}>
      <sphereGeometry args={[.007, 8, 6]} /><meshStandardMaterial color="#b69c67" metalness={.75} roughness={.45} />
    </mesh>))}
    <group ref={card} position={cardPosition} rotation={[0, 0, cardLayout.rotationZ]}
      onPointerOver={(event) => { event.stopPropagation(); setHovered(true) }}
      onPointerOut={() => setHovered(false)}
      onClick={(event) => { event.stopPropagation(); setHovered(false); openFocus('article') }}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[...cardSize, .004]} />
        <meshStandardMaterial color="#d6c6a6" roughness={.98} />
      </mesh>
      <mesh position={[0, 0, .0025]}>
        <planeGeometry args={cardSize} />
        <meshStandardMaterial ref={paper} map={resources.paper} bumpMap={resources.paper} bumpScale={.0004}
          emissive="#b99d6a" emissiveIntensity={.015} roughness={.95} />
      </mesh>
    </group>
    <group ref={pin} position={[.392, .229, .078]}>
      <mesh position={[0, 0, .001]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[.003, .003, .026, 8]} />
        <meshStandardMaterial color="#bca77a" metalness={.8} roughness={.3} />
      </mesh>
      <mesh position={[0, 0, .019]} castShadow>
        <sphereGeometry args={[.015, 16, 10]} />
        <meshStandardMaterial color="#9f4738" roughness={.34} />
      </mesh>
    </group>
  </group>
}
