import { Model } from './Model'
import type { ModelProps } from './Model'

export function Sofa(props: ModelProps) {
  return <Model asset="sofa" {...props} />
}

export function Desk(props: ModelProps) {
  return <Model asset="desk" {...props} />
}

export function Mac(props: ModelProps) {
  return <Model asset="mac" {...props} />
}

export function Chair(props: ModelProps) {
  return <Model asset="chair" {...props} />
}
