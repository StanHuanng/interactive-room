/**
 * Procedural gray-box room stub.
 * Walls/floor/ceiling use simple boxes so MVP can ship without Blender assets.
 */
export function Room() {
  const wallMat = { color: '#6b6b6b' } as const
  const floorMat = { color: '#4a4a4a' } as const
  const ceilingMat = { color: '#5a5a5a' } as const

  return (
    <group>
      {/* Floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial {...floorMat} />
      </mesh>

      {/* Ceiling */}
      <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 3, 0]}>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial {...ceilingMat} />
      </mesh>

      {/* Back wall */}
      <mesh position={[0, 1.5, -5]}>
        <boxGeometry args={[10, 3, 0.2]} />
        <meshStandardMaterial {...wallMat} />
      </mesh>

      {/* Front wall (open doorway feel — thinner / lower opacity later) */}
      <mesh position={[0, 1.5, 5]}>
        <boxGeometry args={[10, 3, 0.2]} />
        <meshStandardMaterial {...wallMat} />
      </mesh>

      {/* Left wall */}
      <mesh position={[-5, 1.5, 0]}>
        <boxGeometry args={[0.2, 3, 10]} />
        <meshStandardMaterial {...wallMat} />
      </mesh>

      {/* Right wall */}
      <mesh position={[5, 1.5, 0]}>
        <boxGeometry args={[0.2, 3, 10]} />
        <meshStandardMaterial {...wallMat} />
      </mesh>

      {/* Placeholder desk block (office zone) */}
      <mesh position={[-2.5, 0.4, -3]} castShadow>
        <boxGeometry args={[2.2, 0.8, 1]} />
        <meshStandardMaterial color="#3d2b1f" />
      </mesh>

      {/* Placeholder chair */}
      <mesh position={[-2.5, 0.45, -2]} castShadow>
        <boxGeometry args={[0.6, 0.9, 0.6]} />
        <meshStandardMaterial color="#2a2a2a" />
      </mesh>

      {/* Placeholder red sofa */}
      <mesh position={[2.5, 0.35, -2.5]} castShadow>
        <boxGeometry args={[2.4, 0.7, 1]} />
        <meshStandardMaterial color="#8b1a1a" />
      </mesh>
    </group>
  )
}
