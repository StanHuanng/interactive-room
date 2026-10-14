# Model provenance

All assets in `public/models/` are original procedural models created for this
project with Blender. No third-party models, artwork, logos, or textures are used.
The authoritative appearance and placement brief is [SCENE_SPEC.md](../../docs/SCENE_SPEC.md).

| Asset | Original procedural content |
| --- | --- |
| `sofa.glb` | Low curved lounge armchair, burgundy #632D28 bouclé, recessed base |
| `ottoman.glb` | Matching irregular oval upholstered ottoman |
| `desk.glb` | Thin #493025 walnut top, #8C8580 stainless slab legs, books and desk accessories |
| `chair.glb` | Brown leather, low curved back, silver arms and five-star caster base |
| `room.glb` | #B99475 walls, varied #543020 walnut planks, dark baseboards, ceiling, right window and walnut door |
| `rug.glb` | Thin light-brown woven rug with fine parallel stripes |
| `side_table.glb` | Small metal pedestal table |
| `mushroom_lamp.glb` | Milk-white hemisphere shade, brass column, warm emissive diffuser |
| `desk_lamp.glb` | Brass mushroom desk lamp with warm emissive diffuser |
| `bookshelf.glb` | Left-wall walnut shelves, original books, ceramics, framed landscape, sculpture, small plant and emissive LED strips |
| `corkboard.glb` | Cork, dark frame, original schematic vintage map, landscape cards, notes and pins |
| `decor.glb` | Low cabinet, original abstract art, right narrow shelf, floor lamp, plant and left sconce |
| `mac.glb` | Existing original unbranded all-in-one computer, keyboard and mouse; preserved byte-for-byte |

[build_assets.py](../../blender/build_assets.py) converts all specification sRGB
hex swatches to linear material base colors. Bouclé uses Blender procedural noise
bump, with a small periodic normal tile embedded in GLB for portable texture.
Wood grain and woven fibers also use embedded original mathematical normal tiles.
No external texture files are required. Metal uses metallic 1 and roughness 0.35.

Models use meters, glTF Y-up, applied transforms, and floor-relative origins.
The Mac origin is its desktop contact plane; corkboard origin is its center.
`decor.glb` contains fixed room-local decorative placements. Other placements
are shared by the app and renderer through `src/components/room/scene-layout.json`.
The native 6 × 5 × 2.8 m room is not stretched.

Regenerate with Blender 4.2.3 LTS:

```sh
blender -b -P blender/build_assets.py
blender -b -P blender/render_previews.py
```

`public/models/manifest.json` records triangle counts, byte sizes and bounds.
`previews/` contains an imported-GLB PNG for every asset (960 × 640) and a combined
interior (1280 × 800). Lighting uses warm 2400–3000K reference colors with moderate
exposure to preserve material colors. Previews and embedded textures are original.
