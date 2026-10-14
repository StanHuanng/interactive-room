import { Suspense } from 'react'
import { Bookshelf, Chair, Decor, Desk, DeskLamp, MushroomLamp, Ottoman, Rug, SideTable, Sofa } from './models/Furniture'
import { MacProfile } from './models/MacProfile'
import { ArticleBoard } from './models/ArticleBoard'
import { RoomShell } from './models/RoomShell'
import { roomLayout } from './layout'
import { useInteraction } from '../interaction/useInteraction'

export function Room() {
  const { sit, focus, returning, closeFocus } = useInteraction()
  return (
    <Suspense fallback={null}>
      <group onClick={() => { if (focus) closeFocus() }}>
        <RoomShell />
        <Rug {...roomLayout.rug} />
        <Desk {...roomLayout.desk} />
        <MacProfile {...roomLayout.mac} />
        <Chair {...roomLayout.chair} onClick={(event) => { event.stopPropagation(); if (focus) closeFocus(); else if (!returning) sit('chair') }} />
        <Sofa {...roomLayout.sofa} onClick={(event) => { event.stopPropagation(); if (focus) closeFocus(); else if (!returning) sit('sofa') }} />
        <Ottoman {...roomLayout.ottoman} />
        <SideTable {...roomLayout.side_table} />
        <MushroomLamp {...roomLayout.mushroom_lamp} />
        <DeskLamp {...roomLayout.desk_lamp} />
        <Bookshelf {...roomLayout.bookshelf} />
        <ArticleBoard {...roomLayout.corkboard} />
        <Decor {...roomLayout.decor} />
      </group>
    </Suspense>
  )
}
