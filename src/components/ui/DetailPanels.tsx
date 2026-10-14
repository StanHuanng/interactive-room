import { useEffect, useRef } from 'react'
import { useInteraction } from '../interaction/useInteraction'
import { esp32Article } from '../../data/esp32Article'

export function DetailPanels() {
  const { focus, returning, openFocus, closeFocus } = useInteraction()
  const dialog = useRef<HTMLElement>(null)
  const close = useRef<HTMLButtonElement>(null)
  const active = focus === 'article'
  useEffect(() => {
    if (!active) return
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null
    // Wait until the flying card has reached the foreground before focusing the reader.
    const timer = window.setTimeout(() => close.current?.focus({ preventScroll: true }), 650)
    return () => {
      window.clearTimeout(timer)
      previous?.focus({ preventScroll: true })
    }
  }, [active])

  return <>
    <div className={`detail-hint ${focus === 'mac' ? 'is-visible' : ''}`} aria-hidden={focus !== 'mac'}>
      <span>PROFILE / 01</span><span>Esc or click the room to return</span>
      <button onClick={closeFocus} tabIndex={focus === 'mac' ? 0 : -1} aria-label="Return to room">Close ×</button>
    </div>
    <div className={`article-reader ${active ? 'is-open' : ''}`} aria-hidden={!active} inert={!active}
      onClick={closeFocus}>
      <article ref={dialog} className="article-panel" role="dialog" aria-modal="true" aria-labelledby="article-title"
        lang="zh-CN" onClick={(event) => event.stopPropagation()}
        onKeyDown={(event) => {
          if (event.key !== 'Tab') return
          const items = dialog.current?.querySelectorAll<HTMLElement>('button, a[href]')
          if (!items?.length) return
          const first = items[0], last = items[items.length - 1]
          if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
          else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
        }}>
        <div className="article-topline"><span>FIELD NOTES <i>/</i> 01</span>
          <button ref={close} className="article-close" onClick={closeFocus} aria-label="关闭文章">×</button>
        </div>
        <p className="article-eyebrow">ESP32 · HARDWARE · HUMAN IN THE LOOP</p>
        <h1 id="article-title">{esp32Article.title}</h1>
        <div className="article-byline"><span className="byline-avatar">1</span><strong>1psum Stan</strong><span>{esp32Article.source}</span></div>
        <div className="article-rule" />
        <div className="article-summary">{esp32Article.summary.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</div>
        <div className="article-footer"><a href={esp32Article.href} onClick={(event) => event.preventDefault()}
          aria-label="原文链接待补充">阅读 X 原文 <span>↗</span></a><span>原文链接待补充</span></div>
        <p className="article-return">Esc 或点击纸张外侧，放回墙上</p>
      </article>
    </div>
    {/* Keyboard equivalents for the same two scene interactions. */}
    <div className="scene-accessibility" hidden={!!focus || returning}>
      <button onClick={() => openFocus('mac')}>Open Mac profile</button>
      <button onClick={() => openFocus('article')}>Read ESP32 wall note</button>
    </div>
  </>
}
