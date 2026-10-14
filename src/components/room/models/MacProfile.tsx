import { useRef, useState } from 'react'
import { Html, useCursor } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import type { MeshBasicMaterial } from 'three'
import { Model } from './Model'
import type { ModelProps } from './Model'
import { useInteraction } from '../../interaction/useInteraction'

const posts = ['A place for ideas, experiments, and things in progress.', 'Small boards. Curious buttons. More soon.', 'Notes from the desk — a new story is on the wall.']

export function MacProfile(props: ModelProps) {
  const { focus, returning, openFocus, closeFocus } = useInteraction()
  const [hovered, setHovered] = useState(false)
  const glow = useRef<MeshBasicMaterial>(null)
  useCursor(hovered && !focus && !returning)
  useFrame((_, delta) => {
    if (glow.current) glow.current.opacity += ((hovered || focus === 'mac' ? .2 : 0) - glow.current.opacity) * (1 - Math.exp(-9 * Math.min(delta, .05)))
  })
  return <group {...props}
    onClick={(event) => { event.stopPropagation(); setHovered(false); openFocus('mac') }}
    onPointerOver={(event) => { event.stopPropagation(); setHovered(true) }}
    onPointerOut={() => setHovered(false)}>
    <Model asset="mac" />
    <mesh position={[0, .381, -.133]}>
      <planeGeometry args={[.609, .333]} />
      <meshBasicMaterial ref={glow} color="#d4b981" transparent opacity={0} depthWrite={false} toneMapped={false} />
    </mesh>
    <Html transform occlude position={[0, .381, -.126]} distanceFactor={.4}
      zIndexRange={[20, 10]} wrapperClass="mac-html">
      <section className="mac-profile" aria-label="X profile for 1psum Stan"
        onPointerEnter={() => setHovered(true)} onPointerLeave={() => setHovered(false)}
        onPointerDown={(event) => event.stopPropagation()}
        onClick={(event) => { event.stopPropagation(); setHovered(false); openFocus('mac') }}>
        <nav className="profile-nav"><span className="x-mark">𝕏</span><span>1psum Stan <small>3 posts · preview</small></span>
          {focus === 'mac' && <button aria-label="Close profile" onClick={(event) => {
            event.stopPropagation()
            closeFocus()
          }}>×</button>}
        </nav>
        <div className="profile-content">
          <div className="profile-identity">
            <div className="profile-avatar" aria-label="Avatar placeholder">1<span>↗</span></div>
            <h1>1psum Stan</h1><span className="profile-handle">@1psumesse</span>
            <p>Ideas, hardware &amp; little experiments.<br /><span>Bio placeholder · a work in progress.</span></p>
            <a href="https://x.com/1psumesse" target="_blank" rel="noopener noreferrer"
              onClick={(event) => event.stopPropagation()}>View on X <span>↗</span></a>
          </div>
          <div className="profile-posts" aria-label="Three placeholder posts">
            {posts.map((post, index) => <article key={post}>
              <div className="post-meta"><strong>1psum Stan</strong><span>@1psumesse · 0{index + 1}</span></div>
              <p>{post}</p><div className="post-placeholder">POST PLACEHOLDER <span>♡ &nbsp; ↗</span></div>
            </article>)}
          </div>
        </div>
      </section>
    </Html>
  </group>
}
