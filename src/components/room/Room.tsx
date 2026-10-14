import { Suspense } from 'react'
import { Bookshelf, Chair, Corkboard, Decor, Desk, DeskLamp, Mac, MushroomLamp, Ottoman, Rug, SideTable, Sofa } from './models/Furniture'
import { RoomShell } from './models/RoomShell'
import { roomLayout } from './layout'
import { useInteraction } from '../interaction/useInteraction'

export function Room() {
  const { sit } = useInteraction()
  return (
    <Suspense fallback={null}>
      <group>
        <RoomShell />
        <Rug {...roomLayout.rug} />
        <Desk {...roomLayout.desk} />
        <Mac {...roomLayout.mac} />
        <Chair {...roomLayout.chair} onClick={(event) => { event.stopPropagation(); sit('chair') }} />
        <Sofa {...roomLayout.sofa} onClick={(event) => { event.stopPropagation(); sit('sofa') }} />
        <Ottoman {...roomLayout.ottoman} />
        <SideTable {...roomLayout.side_table} />
        <MushroomLamp {...roomLayout.mushroom_lamp} />
        <DeskLamp {...roomLayout.desk_lamp} />
        <Bookshelf {...roomLayout.bookshelf} />
        <Corkboard {...roomLayout.corkboard} />
        <Decor {...roomLayout.decor} />
      </group>
    </Suspense>
  )
}
