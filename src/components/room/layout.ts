import placements from './scene-layout.json'

export type Position = [number, number, number]
export type Seat = 'chair' | 'sofa'

// Shared with Blender preview rendering. Native 6 x 5 x 2.8 m shell, no stretching.
export const roomLayout = Object.fromEntries(
  Object.entries(placements).map(([name, placement]) => [name, {
    position: placement.position as Position,
    rotation: [0, placement.rotation, 0] as Position,
  }]),
) as Record<keyof typeof placements, { position: Position; rotation: Position }>

export const seats: Record<Seat, { eye: Position; target: Position; stand: Position }> = {
  chair: {
    eye: [roomLayout.chair.position[0], 1.02, roomLayout.chair.position[2]],
    target: [roomLayout.mac.position[0], 1.12, roomLayout.mac.position[2]],
    stand: [0.72, 1.6, 0.18],
  },
  sofa: {
    eye: [roomLayout.sofa.position[0], 0.90, roomLayout.sofa.position[2]],
    target: [0.5, 0.95, 1.7],
    stand: [-0.82, 1.6, 0.65],
  },
}
