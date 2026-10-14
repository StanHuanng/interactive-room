// Preserve the original gray-box X/Z placement and 10 x 10 x 3 m room.
// Furniture origins now sit at floor level, rather than at each box's center.
export const roomLayout = {
  desk: [-2.5, 0, -3] as [number, number, number],
  chair: [-2.5, 0, -2] as [number, number, number],
  sofa: [2.5, 0, -2.5] as [number, number, number],
  deskHeight: 0.75,
  shellScale: [10 / 6, 3 / 2.8, 10 / 5] as [number, number, number],
}
