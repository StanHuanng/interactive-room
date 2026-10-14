import { useEffect, useMemo, useRef } from 'react'
import { PerspectiveCamera } from '@react-three/drei'
import { useFrame, useThree } from '@react-three/fiber'
import { Matrix4, PerspectiveCamera as ThreePerspectiveCamera, Quaternion, Vector3 } from 'three'
import { roomLayout, seats } from '../room/layout'
import type { Seat } from '../room/layout'
import { useInteraction } from '../interaction/useInteraction'
import { WalkControls } from './WalkControls'

const up = new Vector3(0, 1, 0)
const seatNames: Seat[] = ['chair', 'sofa']
const footprints = [
  { p: roomLayout.desk.position, w: 1.15, d: .55 },
  { p: roomLayout.sofa.position, w: .69, d: .62 },
  { p: roomLayout.ottoman.position, w: .54, d: .44 },
  { p: roomLayout.side_table.position, w: .32, d: .32 },
  { p: roomLayout.bookshelf.position, w: .30, d: 1.31 },
  { p: [0.05, 0, -2.24], w: 1.04, d: .33 },
  { p: [2.76, 0, 1.75], w: .30, d: .44 },
]

function blocked(x: number, z: number) {
  if (Math.abs(x) > 2.80 || Math.abs(z) > 2.30) return true
  for (const { p, w, d } of footprints) {
    if (Math.abs(x - p[0]!) < w && Math.abs(z - p[2]!) < d) return true
  }
  return false
}

export function PlayerCamera() {
  const { camera, size } = useThree()
  const { seat, nearby, sit, stand, setNearby, focus, returning, finishReturn } = useInteraction()
  const keys = useRef(new Set<string>())
  const previousSeat = useRef<Seat | null>(null)
  const standing = useRef(false)
  const saved = useRef(false)
  const savedFov = useRef(70)
  const busy = !!focus || returning
  // Scratch objects and return pose are allocated once, never inside the frame loop.
  const rig = useMemo(() => ({
    forward: new Vector3(), right: new Vector3(), movement: new Vector3(),
    goal: new Vector3(), target: new Vector3(), standingGoal: new Vector3(),
    savedPosition: new Vector3(), savedQuaternion: new Quaternion(),
    rotation: new Quaternion(), matrix: new Matrix4(),
  }), [])

  useEffect(() => { camera.lookAt(-.15, 1.05, -1.10) }, [camera])
  useEffect(() => {
    keys.current.clear()
    const down = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLElement && event.target.closest('input, textarea, [contenteditable], [role="dialog"]')) return
      if (busy) return
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
  }, [seat, nearby, sit, stand, busy])

  useFrame((_, rawDelta) => {
    const delta = Math.min(rawDelta, .05)
    const alpha = 1 - Math.exp(-6 * delta)
    const perspective = camera as ThreePerspectiveCamera
    if (focus && !saved.current) {
      rig.savedPosition.copy(camera.position)
      rig.savedQuaternion.copy(camera.quaternion)
      savedFov.current = perspective.fov
      saved.current = true
    }
    if (busy) {
      if (focus === 'mac') {
        // Match the immutable GLB's screen centre, then fit the bezel in any aspect.
        rig.target.set(0, .381, -.127).applyAxisAngle(up, roomLayout.mac.rotation[1])
        rig.target.add(rig.goal.set(...roomLayout.mac.position))
        const distance = Math.max(.42, .66 / (size.width / size.height)) / (2 * Math.tan(42 * Math.PI / 360)) * 1.12
        rig.goal.set(0, 0, distance).applyAxisAngle(up, roomLayout.mac.rotation[1]).add(rig.target)
        rig.rotation.setFromRotationMatrix(rig.matrix.lookAt(rig.goal, rig.target, up))
        // oxlint-disable-next-line react/immutability -- The R3F camera is an imperative Three.js object.
        perspective.fov += (42 - perspective.fov) * alpha
      } else if (saved.current) {
        rig.goal.copy(rig.savedPosition)
        rig.rotation.copy(rig.savedQuaternion)
        perspective.fov += (savedFov.current - perspective.fov) * alpha
      }
      if (saved.current) {
        camera.position.lerp(rig.goal, alpha)
        camera.quaternion.slerp(rig.rotation, alpha)
        perspective.updateProjectionMatrix()
      }
      if (returning && (!saved.current || (camera.position.distanceToSquared(rig.savedPosition) < .0000001 &&
        camera.quaternion.angleTo(rig.savedQuaternion) < .0003 && Math.abs(perspective.fov - savedFov.current) < .003))) {
        saved.current = false
        finishReturn()
      }
      return
    }
    if (seat) {
      previousSeat.current = seat
      standing.current = false
      rig.goal.set(...seats[seat].eye)
      rig.target.set(...seats[seat].target)
      rig.rotation.setFromRotationMatrix(rig.matrix.lookAt(rig.goal, rig.target, up))
      camera.position.lerp(rig.goal, alpha)
      camera.quaternion.slerp(rig.rotation, alpha)
      if (nearby) setNearby(null)
      return
    }
    if (previousSeat.current) {
      rig.standingGoal.set(...seats[previousSeat.current].stand)
      standing.current = true
      previousSeat.current = null
    }
    if (standing.current) {
      camera.position.lerp(rig.standingGoal, alpha)
      if (camera.position.distanceToSquared(rig.standingGoal) < .000001) standing.current = false
      return
    }
    camera.getWorldDirection(rig.forward)
    rig.forward.setY(0)
    rig.forward.normalize()
    rig.right.crossVectors(rig.forward, up).normalize()
    const held = keys.current
    rig.movement.set(0, 0, 0)
    if (held.has('KeyW') || held.has('ArrowUp')) rig.movement.add(rig.forward)
    if (held.has('KeyS') || held.has('ArrowDown')) rig.movement.sub(rig.forward)
    if (held.has('KeyD') || held.has('ArrowRight')) rig.movement.add(rig.right)
    if (held.has('KeyA') || held.has('ArrowLeft')) rig.movement.sub(rig.right)
    rig.movement.normalize().multiplyScalar(delta * 1.65)
    if (!blocked(camera.position.x + rig.movement.x, camera.position.z)) camera.position.setX(camera.position.x + rig.movement.x)
    if (!blocked(camera.position.x, camera.position.z + rig.movement.z)) camera.position.setZ(camera.position.z + rig.movement.z)
    camera.position.setY(1.6)
    let nearest: Seat | null = null
    let distance = 1.35
    for (const name of seatNames) {
      const nextDistance = Math.hypot(camera.position.x - roomLayout[name].position[0], camera.position.z - roomLayout[name].position[2])
      if (nextDistance < distance) { nearest = name; distance = nextDistance }
    }
    if (nearest !== nearby) setNearby(nearest)
  })
  return <>
    <PerspectiveCamera makeDefault position={[1.05, 1.6, 2.20]} fov={70} near={0.05} far={50} />
    <WalkControls enabled={!seat && !busy} />
  </>
}
