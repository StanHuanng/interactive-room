import { useInteraction } from '../interaction/useInteraction'

export function Hud() {
  const { seat, nearby, sit, stand } = useInteraction()
  return <div style={{ position: 'absolute', left: 16, bottom: 16, zIndex: 10,
    padding: '12px 16px', borderRadius: 8, background: 'rgba(38,25,19,0.85)',
    color: '#ecdbc3', fontSize: 13, lineHeight: 1.65, maxWidth: 360 }}>
    <strong>Warm Walnut Study</strong>
    <div>{seat ? `Seated in the ${seat === 'chair' ? 'office chair' : 'lounge chair'} · E / Esc to stand` : 'WASD / arrows to walk · E near a seat to sit'}</div>
    {nearby && !seat && <div>Press E to sit in the {nearby === 'chair' ? 'office chair' : 'lounge chair'}</div>}
    {seat ? <button onClick={stand}>Stand up</button> : <>
      <button id="walk-controls">Walk / look</button>{' '}
      <button onClick={() => sit('chair')}>Sit at desk</button>{' '}
      <button onClick={() => sit('sofa')}>Sit in lounge</button>
    </>}
  </div>
}
