/** Warm ambient + key light stub matching the reference mood. */
export function Lights() {
  return (
    <>
      <ambientLight intensity={0.35} color="#ffd9b3" />
      <directionalLight
        position={[4, 6, 2]}
        intensity={1.1}
        color="#ffcc99"
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <pointLight position={[-2.5, 2.4, -3]} intensity={0.6} color="#ffb066" distance={8} />
    </>
  )
}
