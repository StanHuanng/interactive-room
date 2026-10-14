import { useEffect } from 'react'
import { useThree } from '@react-three/fiber'
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js'

// Keep ordinary pointer rays when unlocked; only walking uses the centre reticle.
export function WalkControls({ enabled }: { enabled: boolean }) {
  const { camera, gl, get, setEvents } = useThree()
  useEffect(() => {
    if (!enabled) return
    const controls = new PointerLockControls(camera, gl.domElement)
    const previousCompute = get().events.compute
    setEvents({ compute: (event, state, previous) => {
      if (controls.isLocked) {
        state.pointer.set(0, 0)
        state.raycaster.setFromCamera(state.pointer, state.camera)
      } else previousCompute?.(event, state, previous)
    } })
    const button = document.getElementById('walk-controls')
    const lock = () => controls.lock()
    button?.addEventListener('click', lock)
    return () => {
      button?.removeEventListener('click', lock)
      if (controls.isLocked) controls.unlock()
      controls.dispose()
      setEvents({ compute: previousCompute })
    }
  }, [enabled, camera, gl, get, setEvents])
  return null
}
