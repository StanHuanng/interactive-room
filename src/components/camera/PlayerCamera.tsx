import { useEffect, useRef } from 'react'
import { PerspectiveCamera, PointerLockControls } from '@react-three/drei'
import { useFrame, useThree } from '@react-three/fiber'
import { Vector3 } from 'three'
import { roomLayout, seats } from '../room/layout'
import type { Seat } from '../room/layout'
import { useInteraction } from '../interaction/useInteraction'

const forward = new Vector3()
const right = new Vector3()
const movement = new Vector3()
const goal = new Vector3()
const up = new Vector3(0, 1, 0)

// A small walking radius keeps the camera out of the solid room and furniture.
function blocked(x: number, z: number) {
  const footprints = [
    { p: roomLayout.desk.position, w: 1.15, d: .55 },
    { p: roomLayout.sofa.position, w: .69, d: .62 },
    { p: roomLayout.ottoman.position, w: .54, d: .44 },
    { p: roomLayout.side_table.position, w: .32, d: .32 },
    { p: roomLayout.bookshelf.position, w: .30, d: 1.31 },
    { p: [0.05, 0, -2.24], w: 1.04, d: .33 },
    { p: [2.76, 0, 1.75], w: .30, d: .44 },
  ]
  return Math.abs(x) > 2.80 || Math.abs(z) > 2.30 || footprints.some(
    ({ p, w, d }) => Math.abs(x - p[0]!) < w && Math.abs(z - p[2]!) < d,
  )
}

export function PlayerCamera() {
  const { camera } = useThree()
  const { seat, nearby, sit, stand, setNearby } = useInteraction()
  const keys = useRef(new Set<string>())
  const previousSeat = useRef<Seat | null>(null)
  const standingGoal = useRef<Vector3 | null>(null)

  useEffect(() => { camera.lookAt(-.15, 1.05, -1.10) }, [camera])
  useEffect(() => {
    const down = (event: KeyboardEvent) => {
      if (['KeyW', 'KeyA', 'KeyS', 'KeyD', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'KeyE', 'Escape'].includes(event.code)) event.preventDefault()
      keys.current.add(event.code)
      if (!event.repeat && event.code === 'KeyE') {
        if (seat) stand()
        else if (nearby) sit(nearby)
      }
      if (event.code === 'Escape' && seat) stand()
    }
    const release = (event: KeyboardEvent) => keys.current.delete(event.code)
    const clear = () => keys.current.clear()
    window.addEventListener('keydown', down)
    window.addEventListener('keyup', release)
    window.addEventListener('blur', clear)
    return () => {
      window.removeEventListener('keydown', down)
      window.removeEventListener('keyup', release)
      window.removeEventListener('blur', clear)
    }
  }, [seat, nearby, sit, stand])

  useFrame((_, delta) => {
    const alpha = 1 - Math.exp(-7 * delta)
    if (seat) {
      previousSeat.current = seat
      standingGoal.current = null
      camera.position.lerp(goal.set(...seats[seat].eye), alpha)
      camera.lookAt(...seats[seat].target)
      if (nearby) setNearby(null)
      return
    }
    if (previousSeat.current) {
      standingGoal.current = new Vector3(...seats[previousSeat.current].stand)
      previousSeat.current = null
    }
    if (standingGoal.current) {
      camera.position.lerp(standingGoal.current, alpha)
      if (camera.position.distanceTo(standingGoal.current) < .015) standingGoal.current = null
      return
    }
    camera.getWorldDirection(forward)
    forward.y = 0
    forward.normalize()
    right.crossVectors(forward, up).normalize()
    const held = keys.current
    movement.set(0, 0, 0)
    if (held.has('KeyW') || held.has('ArrowUp')) movement.add(forward)
    if (held.has('KeyS') || held.has('ArrowDown')) movement.sub(forward)
    if (held.has('KeyD') || held.has('ArrowRight')) movement.add(right)
    if (held.has('KeyA') || held.has('ArrowLeft')) movement.sub(right)
    movement.normalize().multiplyScalar(Math.min(delta, .05) * 1.65)
    // oxlint-disable-next-line react/immutability -- R3F cameras are updated imperatively in useFrame.
    if (!blocked(camera.position.x + movement.x, camera.position.z)) camera.position.x += movement.x
    if (!blocked(camera.position.x, camera.position.z + movement.z)) camera.position.z += movement.z
    camera.position.y = 1.6
    const nearest = (['chair', 'sofa'] as Seat[]).map((name) => ({
      name, distance: Math.hypot(camera.position.x - roomLayout[name].position[0], camera.position.z - roomLayout[name].position[2]),
    })).sort((a, b) => a.distance - b.distance)[0]!
    const next = nearest.distance < 1.35 ? nearest.name : null
    if (next !== nearby) setNearby(next)
  })
  return <>
    <PerspectiveCamera makeDefault position={[1.05, 1.6, 2.20]} fov={70} near={0.05} far={50} />
    {!seat && <PointerLockControls selector="#walk-controls" />}
  </>
}
