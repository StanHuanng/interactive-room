/** Minimal on-screen hint overlay for the stub scene. */
export function Hud() {
  return (
    <div
      style={{
        position: 'absolute',
        left: 16,
        bottom: 16,
        zIndex: 10,
        padding: '10px 14px',
        borderRadius: 8,
        background: 'rgba(0,0,0,0.55)',
        fontSize: 13,
        lineHeight: 1.45,
        pointerEvents: 'none',
        maxWidth: 360,
      }}
    >
      <strong>Interactive Personal Room</strong>
      <div>灰盒房间 stub — WASD / 坐下交互将在 MVP 阶段接入</div>
    </div>
  )
}
