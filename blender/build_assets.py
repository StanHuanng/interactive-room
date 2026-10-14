"""Original procedural study assets. Run blender -b -P blender/build_assets.py.
Meters, Blender Z-up -> glTF Y-up; furniture faces Blender -Y / glTF +Z.
The existing mac.glb is protected and never exported.
"""
import hashlib
import json
import math
import random
import struct
import zlib
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'public/models'


def srgb(color):
    values = [int(color.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values)


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def surface_fields(kind):
    """Periodic baked relief/color fields, shared by Blender and glTF (no noise nodes)."""
    n = 512 if kind == 'wood' else 256
    y, x = np.mgrid[:n, :n] / n
    u, v = 2 * np.pi * x, 2 * np.pi * y
    rng = np.random.default_rng(73)
    fine = np.zeros((n, n))
    # Periodic, deterministic irregularity without visible tile boundaries.
    for _ in range(24):
        a, b = rng.integers(7, 55, 2)
        fine += np.sin(a * u + b * v + rng.uniform(0, 2 * np.pi)) / 24
    if kind == 'wood':
        bend = 2.2 * np.sin(u) + .65 * np.sin(3 * u + 1.2)
        grain = np.sin(17 * v + bend) + .45 * np.sin(39 * v + 1.8 * bend)
        pores = np.maximum(0, np.sin(73 * v + 2.2 * bend)) ** 12
        height = .35 * grain - .18 * pores + .08 * fine
        tone = .09 * grain + .07 * np.sin(3 * v + .25 * np.sin(u)) - .06 * pores
    elif kind == 'woven':
        warp, weft = np.cos(12 * u), np.cos(12 * v)
        over = np.sin(6 * u) * np.sin(6 * v)
        height = .38 * (warp + weft) + .30 * over * (warp - weft) + .18 * fine
        tone = .055 * (warp + weft) + .045 * np.sin(2 * u) + .10 * fine
    elif kind in ('boucle', 'leather', 'cork'):
        distance = np.full((n, n), 2.)
        for j in range(8):
            for i in range(8):
                cx, cy = (i + rng.uniform(.15, .85)) / 8, (j + rng.uniform(.15, .85)) / 8
                dx, dy = np.abs(x - cx), np.abs(y - cy)
                d = np.hypot(np.minimum(dx, 1 - dx), np.minimum(dy, 1 - dy)) * 8
                distance = np.minimum(distance, d)
        if kind == 'boucle':
            # Soft irregular yarn loops with dark gaps, rather than a sinusoidal grid.
            loop = np.exp(-((distance - .28) / .11) ** 2)
            height = .65 * loop + .30 * fine
            tone = .14 * (loop - .45) + .20 * fine
        elif kind == 'leather':
            height = .20 * np.minimum(distance, .50) + .12 * fine
            tone = .035 * (distance - .3) + .06 * fine
        else:
            height = .3 * distance + .35 * fine
            tone = .16 * (distance - .3) + .32 * fine
    elif kind == 'brushed':
        height = .18 * np.sin(83 * v + .15 * np.sin(u)) + .13 * np.sin(117 * v) + .04 * fine
        tone = .035 * np.sin(83 * v) + .02 * fine
    else:  # Tiny matte microcement variation; no large wall mottling.
        height = .25 * fine
        tone = .025 * fine
    return height, tone


SURFACE_FIELDS = {}


def texture_tile(kind, color=None):
    """Pack small original PNGs; normal relief survives GLB export and re-import."""
    name = f'{kind}_{color.lstrip("#") if color else "normal"}'
    if name in bpy.data.images:
        return bpy.data.images[name]
    if kind not in SURFACE_FIELDS:
        SURFACE_FIELDS[kind] = surface_fields(kind)
    height, tone = SURFACE_FIELDS[kind]
    n = height.shape[0]
    if color:
        base = np.array([int(color.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)])
        pixels = np.clip(base * (1 + tone[:, :, None]), 0, 1)
    else:
        # Central differences on a torus, with adequate contrast at fabric scale.
        dx = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) * 1.8
        dy = (np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)) * 1.8
        vectors = np.stack((-dx, -dy, np.ones_like(dx)), axis=2)
        pixels = vectors / np.linalg.norm(vectors, axis=2)[:, :, None] * .5 + .5
    rows = b''.join(b'\x00' + row.tobytes() for row in np.rint(pixels * 255).astype(np.uint8))
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    path = Path('/tmp') / f'study_{name}.png'
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', n, n, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))
    image = bpy.data.images.load(str(path))
    image.name = name
    image.colorspace_settings.name = 'sRGB' if color else 'Non-Color'
    image.pack()
    return image


def material(name, color, roughness=.7, metallic=0, texture=None, emission=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*srgb(color), 1)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    shader = nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = mat.diffuse_color
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    if emission:
        shader.inputs['Emission Color'].default_value = (*srgb(color), 1)
        shader.inputs['Emission Strength'].default_value = emission
    if texture:
        mat['surface_kind'] = texture
        for is_color in (False, True):
            tile = nodes.new('ShaderNodeTexImage')
            tile.image = texture_tile(texture, color if is_color else None)
            tile.extension = 'REPEAT'
            if is_color:
                links.new(tile.outputs['Color'], shader.inputs['Base Color'])
            else:
                normal = nodes.new('ShaderNodeNormalMap')
                normal.name = 'Portable surface normal'
                normal.inputs['Strength'].default_value = {
                    'wood': .65, 'woven': .85, 'boucle': .8, 'leather': .38,
                    'microcement': .16, 'brushed': .3, 'cork': .5,
                }[texture]
                links.new(tile.outputs['Color'], normal.inputs['Color'])
                links.new(normal.outputs['Normal'], shader.inputs['Normal'])
    return mat


def finish(obj, name, mat, bevel=0, smooth=False):
    obj.name = name
    obj.data.materials.append(mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new('Soft edges', 'BEVEL')
        mod.width, mod.segments = bevel, 3 if smooth else 1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for face in obj.data.polygons:
        face.use_smooth = smooth
    # Fabric UVs follow existing curved sweeps; boxes get physical planar UVs below.
    if obj.data.uv_layers.active:
        kind = mat.get('surface_kind')
        repeats = {'boucle': 30, 'leather': 22, 'cork': 16, 'wood': 3,
                   'woven': 45, 'brushed': 5, 'microcement': 14}.get(kind, 1)
        for uv in obj.data.uv_layers.active.data:
            uv.uv *= repeats
    return obj


def box(name, center, size, mat, bevel=0, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.dimensions = size
    if rotation:
        obj.rotation_euler = rotation
    finish(obj, name, mat, bevel)
    kind = mat.get('surface_kind')
    if kind:
        # Directional grain in meters, independent of cube-atlas face orientation.
        periods = {'wood': (.95, .24), 'woven': (.025, .025),
                   'boucle': (.035, .035), 'leather': (.025, .025),
                   'microcement': (.18, .18), 'brushed': (.35, .035), 'cork': (.045, .045)}[kind]
        for face in obj.data.polygons:
            normal_axis = max(range(3), key=lambda axis: abs(face.normal[axis]))
            tangent_axes = [axis for axis in range(3) if axis != normal_axis]
            # Longest tangent is the grain direction (including vertical door panels).
            tangent_axes.sort(key=lambda axis: size[axis], reverse=True)
            for loop in face.loop_indices:
                co = obj.data.vertices[obj.data.loops[loop].vertex_index].co
                obj.data.uv_layers.active.data[loop].uv = tuple(co[axis] / period for axis, period in zip(tangent_axes, periods))
    return obj


def cylinder(name, center, radius, depth, mat, vertices=12, rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=center)
    obj = bpy.context.object
    if rotation:
        obj.rotation_euler = rotation
    return finish(obj, name, mat, smooth=True)


def ellipsoid(name, center, size, mat, segments=24, rings=12, irregular=False):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1, location=center)
    obj = bpy.context.object
    for vertex in obj.data.vertices:
        if irregular:
            angle = math.atan2(vertex.co.y, vertex.co.x)
            vertex.co.x *= 1 + .045 * math.sin(3 * angle) + .025 * math.cos(5 * angle)
            vertex.co.y *= 1 + .055 * math.sin(3 * angle + .7)
    obj.scale = tuple(v / 2 for v in size)
    return finish(obj, name, mat, smooth=True)


def beam(name, start, end, width, depth, mat):
    direction = Vector(end) - Vector(start)
    obj = box(name, (Vector(start) + Vector(end)) / 2, (width, depth, direction.length), mat, .003)
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    return obj


def curved_back(name, mat, width, depth, bottom, top, thickness, steps=24, sides=10, lounge=False):
    """Continuous horseshoe upholstered shell, rounded across its full section."""
    verts, faces = [], []
    start, end = (0, 180) if lounge else (15, 165)
    for i in range(steps + 1):
        angle = math.radians(start + (end - start) * i / steps)
        back = max(0, math.sin(angle))
        upper = top if not lounge else top - .17 * (1 - back)
        zcenter, rz = (bottom + upper) / 2, (upper - bottom) / 2
        for j in range(sides):
            p = 2 * math.pi * j / sides
            radial = thickness / 2 * math.cos(p)
            y = -.37 + (depth / 2 + .37) * math.sin(angle) + radial * math.sin(angle) if lounge else (depth / 2 + radial) * math.sin(angle)
            verts.append(((width / 2 + radial) * math.cos(angle), y, zcenter + rz * math.sin(p)))
    if lounge:
        # Connected rounded ends: continuous topology/normals across arm tips.
        def cap(sign, degrees):
            result = []
            for deg in degrees:
                p = math.radians(deg)
                scale = max(.01, math.sin(p))
                for j in range(sides):
                    angle = 2 * math.pi * j / sides
                    result.append((sign * (width / 2 + thickness / 2 * scale * math.cos(angle)), -.37 - thickness / 2 * math.cos(p), (bottom + top - .17) / 2 + (top - .17 - bottom) / 2 * scale * math.sin(angle)))
            return result
        verts = cap(1, (0, 15, 30, 45, 60, 75)) + verts + cap(-1, (75, 60, 45, 30, 15, 0))
    intervals = len(verts) // sides - 1
    for i in range(intervals):
        for j in range(sides):
            a, b = i * sides + j, i * sides + (j + 1) % sides
            faces.append((a, b, b + sides, a + sides))
    faces += [tuple(reversed(range(sides))), tuple(intervals * sides + j for j in range(sides))]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    # Deterministic UVs on the sweep, seamless horizontal fiber repeats.
    uv = mesh.uv_layers.new(name='Fiber UV')
    for polygon in mesh.polygons:
        for loop in polygon.loop_indices:
            index = mesh.loops[loop].vertex_index
            uv.data[loop].uv = (index // sides / intervals * 2, index % sides / sides)
    finish(obj, name, mat, smooth=True)
    obj.select_set(False)


def walnut(name='Walnut', color='#493025', roughness=.48):
    return material(name, color, roughness, texture='wood')


def silver():
    return material('Brushed stainless #8C8580', '#8C8580', .38, .88, texture='brushed')


def sofa():
    fabric = material('Burgundy boucle fabric #632D28', '#632D28', .94, texture='boucle')
    foot = walnut('Hidden recessed plinth', '#261A17')
    cylinder('Hidden base', (0, 0, .03), .30, .06, foot, 24)
    ellipsoid('Deep upholstered base', (0, -.02, .22), (1.28, 1.12, .36), fabric)
    curved_back('Continuous curved back and arms', fabric, 1.02, .88, .18, .86, .29, sides=12, lounge=True)
    ellipsoid('Wide low seat cushion', (0, -.16, .365), (.92, .80, .21), fabric)


def ottoman():
    fabric = material('Burgundy boucle fabric #632D28', '#632D28', .94, texture='boucle')
    cylinder('Hidden ottoman base', (0, 0, .045), .25, .09, walnut('Recessed base', '#261A17'), 16)
    ellipsoid('Irregular oval ottoman', (0, 0, .235), (.91, .70, .43), fabric, irregular=True)


def desk():
    wood, metal = walnut('Desk walnut #493025'), silver()
    box('Thin flat walnut desktop', (0, 0, .745), (2.05, .88, .05), wood, .004)
    for x in (-.88, .88):
        box('Wide brushed stainless slab leg', (x, 0, .36), (.085, .72, .72), metal, .005)
    # Sparse original desktop accessories, leaving the center clear for the protected Mac.
    colors = ['#CEBEA5', '#75513B', '#797773']
    for side, x in enumerate((-.70, .65)):
        for i in range(3):
            book = material(f'Desk book {side} {i}', colors[i], .84)
            box('Horizontal book', (x, .17, .787 + i * .035), (.27 - .02 * i, .18, .03), book, .002)
    box('Small walnut tray', (.70, -.24, .78), (.24, .15, .02), wood, .006)
    ceramic = material('Matte ceramic', '#C8AF91', .82)
    cylinder('Ceramic bowl', (.70, -.24, .81), .055, .04, ceramic)
    cylinder('Pen cup', (.87, .27, .835), .04, .13, ceramic)
    for i in range(3):
        cylinder('Pencil', (.85 + i * .014, .27, .915), .004, .13, wood, 6)


def chair():
    leather = material('Brown leather #67422F', '#67422F', .78, texture='leather')
    frame, rubber = silver(), material('Caster rubber', '#24211F', .88)
    cylinder('Silver base hub', (0, 0, .125), .075, .085, frame)
    for i in range(5):
        a = 2 * math.pi * i / 5 + math.pi / 2
        dx, dy = math.cos(a), math.sin(a)
        beam('Five star silver spoke', (.035 * dx, .035 * dy, .14), (.30 * dx, .30 * dy, .09), .05, .03, frame)
        for offset in (-.017, .017):
            wheel = cylinder('Caster wheel', (.31 * dx - offset * dy, .31 * dy + offset * dx, .04), .04, .023, rubber, 10)
            wheel.rotation_euler = Vector((-dy, dx, 0)).to_track_quat('Z', 'Y').to_euler()
        cylinder('Caster swivel', (.31 * dx, .31 * dy, .085), .02, .04, frame)
    cylinder('Silver gas lift', (0, 0, .30), .03, .34, frame)
    ellipsoid('Leather seat cushion', (0, -.03, .48), (.56, .53, .13), leather, 20, 10)
    beam('Silver back support', (0, .18, .43), (0, .25, .72), .05, .025, frame)
    curved_back('Low curved leather back', leather, .49, .40, .51, .88, .10, steps=16, sides=8)
    for x in (-.30, .30):
        beam('Silver arm upright', (x, .08, .46), (x, .08, .67), .025, .035, frame)
        beam('Silver armrest', (x, -.19, .66), (x, .18, .66), .055, .035, frame)
        ellipsoid('Leather arm pad', (x, -.01, .685), (.067, .30, .045), leather, 12, 6)


def artwork(x, y, z, width, height, frame, rotation=0):
    paper = material('Original abstract canvas', '#D5C1A3', .93)
    dark = material('Abstract brown-black shapes', '#372821', .95)
    box('Narrow artwork frame', (x, y, z), (width, .045, height), frame, .004, (0, 0, rotation))
    box('Abstract painting background', (x, y - .028, z), (width - .045, .008, height - .045), paper)
    box('Abstract geometric block', (x - width * .16, y - .035, z + height * .15), (width * .40, .005, height * .28), dark)
    box('Abstract geometric block', (x + width * .14, y - .035, z - height * .16), (width * .30, .005, height * .38), dark)


def room():
    beige = material('Sand beige microcement (warm #B99475 target)', '#B49A78', .96, texture='microcement')
    trim = walnut('Dark walnut trim', '#302018', .63)
    floor = [walnut(f'Walnut floor plank {i}', color, .53 + (i % 3) * .025) for i, color in enumerate(('#543020', '#704127', '#40271D', '#81502E', '#4B2D20', '#603822', '#35221A', '#683E29'))]
    seam = material('Dark plank seams', '#211611', .92)
    box('Floor foundation', (0, 0, -.055), (6, 5, .08), seam)
    rng = random.Random(94)
    for row in range(20):
        edges = [-3] + [x + (.55 if row % 2 else 0) for x in (-1.8, -.6, .6, 1.8)] + [3]
        for col, (left, right) in enumerate(zip(edges, edges[1:])):
            obj = box('Walnut plank', ((left + right) / 2, -2.375 + row * .25, -.01), (right - left - .007, .243, .02), rng.choices(floor, weights=(4, 2, 1, 1, 3, 3, 1, 2))[0], .001)
            # Offset physical grain per plank to avoid identical repeats.
            for uv in obj.data.uv_layers.active.data:
                uv.uv.x += row * .137 + col * .23
                uv.uv.y += row * .317
    box('Wall back', (0, 2.58, 1.4), (6.32, .16, 2.8), beige)
    box('Wall front', (0, -2.58, 1.4), (6.32, .16, 2.8), beige)
    box('Wall left', (-3.08, 0, 1.4), (.16, 5, 2.8), beige)
    # Window on the right, toward the foreground; door toward the back.
    for center, size in [((3.08, 0, .50), (.16, 5, 1)), ((3.08, 0, 2.52), (.16, 5, .56)), ((3.08, -1.825, 1.62), (.16, 1.35, 1.24)), ((3.08, 1.575, 1.62), (.16, 1.85, 1.24))]:
        box('Right wall around window', center, size, beige)
    box('Plain warm ceiling', (0, 0, 2.87), (6.32, 5.32, .14), material('Ceiling light beige', '#CFB89B', .95))
    for y in (-2.48, 2.48):
        box('Dark baseboard', (0, y, .06), (6, .04, .12), trim)
    for x in (-2.98, 2.98):
        box('Dark baseboard', (x, 0, .06), (.04, 5, .12), trim)
    for y in (-1.15, .65):
        box('Window upright', (2.99, y, 1.62), (.09, .065, 1.30), trim)
    for z in (1, 2.24):
        box('Window horizontal trim', (2.99, -.25, z), (.09, 1.88, .065), trim)
    box('Window mullion', (3.015, -.25, 1.62), (.04, .035, 1.20), trim)
    box('Window sill', (2.96, -.25, 1.01), (.24, 1.94, .05), trim)
    glass = material('Window soft blue glass', '#849693', .22, .1)
    shader = glass.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Transmission Weight'].default_value = .65
    box('Window glazing', (3.04, -.25, 1.62), (.012, 1.74, 1.16), glass)
    door = walnut('Right wall walnut door', '#493025')
    box('Walnut single door', (2.975, 1.78, 1.05), (.06, .94, 2.10), door, .004)
    for y in (1.28, 2.28):
        box('Door casing', (2.94, y, 1.09), (.085, .055, 2.18), trim)
    box('Door casing top', (2.94, 1.78, 2.16), (.085, 1.05, .06), trim)
    box('Simple metal door handle', (2.91, 1.47, 1.01), (.08, .12, .024), silver(), .005)


def rug():
    fabric = material('Caramel sand woven rug fabric', '#AE9568', .98, texture='woven')
    stripe = material('Natural flax woven stripe fabric', '#BBA77D', .98, texture='woven')
    box('Large thin woven rug', (0, 0, .008), (4.90, 3.05, .016), fabric, .008)
    for i in range(25):
        box('Fine parallel woven stripe', (-2.34 + i * .195, 0, .0165), (.020, 2.99, .001), stripe)


def side_table():
    metal = material('Side table aged champagne metal', '#99836C', .42, 1)
    cylinder('Side table round top', (0, 0, .50), .24, .025, metal, 24)
    cylinder('Side table pedestal', (0, 0, .255), .028, .48, metal)
    cylinder('Side table foot', (0, 0, .018), .18, .036, metal, 20)


def lamp(tall=False, brass_shade=False):
    brass = material('Warm brushed brass', '#AF8E55', .30, 1, texture='brushed')
    shade = brass if brass_shade else material('Milk glass warm mushroom shade', '#E5DCC4', .53)
    glow = material('Warm 2700K lamp diffuser', '#FFCE8B', .75, emission=2.5)
    height = 1.48 if tall else .36
    radius = .27 if tall else .19
    cylinder('Mushroom lamp foot', (0, 0, .016), radius * .62, .032, brass, 20)
    cylinder('Mushroom brass column', (0, 0, height * .43), .022, height * .86, brass)
    # Upper hemisphere with a flat underside: no sphere masquerading as a mushroom.
    verts, faces = [], []
    rings, segments = 6, 24
    for i in range(rings + 1):
        angle = math.pi / 2 * i / rings
        for j in range(segments):
            a = 2 * math.pi * j / segments
            verts.append((radius * math.cos(angle) * math.cos(a), radius * math.cos(angle) * math.sin(a), height * .83 + radius * .63 * math.sin(angle)))
    for i in range(rings):
        for j in range(segments):
            a = i * segments + j
            b = i * segments + (j + 1) % segments
            faces.append((a, b, b + segments, a + segments))
    mesh = bpy.data.meshes.new('Hemisphere shade')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    uv = mesh.uv_layers.new(name='Brushed shade UV')
    for face in mesh.polygons:
        # Unwrap each sector across the seam without an interpolation jump.
        sector = (face.index % segments)
        for loop in face.loop_indices:
            index = mesh.loops[loop].vertex_index
            j = index % segments
            uv.data[loop].uv = ((sector + (j != sector)) / segments, index // segments / rings)
    obj = bpy.data.objects.new('Mushroom hemisphere shade', mesh)
    bpy.context.collection.objects.link(obj)
    finish(obj, obj.name, shade, smooth=True)
    cylinder('Warm luminous underside', (0, 0, height * .83), radius * .96, .012, glow, 24)


def mushroom_lamp():
    lamp()


def desk_lamp():
    lamp(brass_shade=True)


def bookshelf():
    wood = walnut('Deep walnut bookshelf', '#35241C', .57)
    led = material('2700K shelf LED', '#FFD9A0', .65, emission=4.5)
    box('Bookshelf rear panel', (0, .16, 1.25), (2.40, .04, 2.5), wood)
    for x in (-1.19, -.39, .39, 1.19):
        box('Bookshelf vertical divider', (x, 0, 1.25), (.045, .36, 2.50), wood)
    for z in (.08, .53, 1.02, 1.54, 2.03, 2.49):
        box('Bookshelf shelf', (0, 0, z), (2.42, .38, .045), wood)
        if z > .1:
            box('Downward warm LED strip', (0, -.155, z - .028), (2.28, .022, .010), led)
    bookmats = [material(f'Original book cover {i}', color, .9) for i, color in enumerate(('#9A7254', '#C9B99B', '#695746', '#4C5751', '#B0997D'))]
    rng = random.Random(42)
    for shelf, z in enumerate((.11, .56, 1.05, 1.57, 2.06)):
        for col in range(3):
            for i in range(4 if (col + shelf) % 2 else 6):
                h = rng.uniform(.20, .33)
                x = -.99 + col * .79 + i * .068
                box('Book spine', (x, -.018, z + h / 2), (.052, .22, h), bookmats[(shelf + col + i) % 5], .002)
    ceramic = material('Shelf ceramic sand', '#BEA68B', .9)
    for x, z in ((-.10, .64), (.71, 1.13), (-.85, 1.65)):
        ellipsoid('Original ceramic vessel', (x, -.015, z + .10), (.16, .14, .20), ceramic, 12, 8)


    # Small framed landscape, abstract bronze sculpture, and shelf greenery.
    paper = material('Original shelf picture', '#C6B697', .94)
    hills = material('Original shelf landscape', '#737B62', .95)
    box('Small shelf picture frame', (.23, -.018, .25), (.22, .035, .27), wood, .003)
    box('Original shelf picture canvas', (.23, -.039, .25), (.19, .004, .24), paper)
    box('Original landscape hill', (.23, -.043, .21), (.18, .003, .09), hills)
    bronze = material('Original bronze sculpture', '#977C50', .48, 1)
    box('Sculpture base', (.23, -.015, 1.075), (.16, .11, .035), wood, .003)
    bpy.ops.mesh.primitive_torus_add(major_segments=12, minor_segments=6, major_radius=.064,
        minor_radius=.016, location=(.23, -.015, 1.175), rotation=(math.pi / 2, 0, 0))
    finish(bpy.context.object, 'Abstract bronze ring sculpture', bronze, smooth=True)
    cylinder('Small shelf plant pot', (1.08, -.015, 2.115), .055, .11, ceramic, 12)
    for i in range(3):
        angle = 2 * math.pi * i / 3
        obj = ellipsoid('Shelf plant leaf', (1.08 + .025 * math.cos(angle), -.015 + .025 * math.sin(angle), 2.22),
            (.12, .045, .022), hills, 10, 6)
        obj.rotation_euler = (0, -.65, angle)


def corkboard():
    cork = material('Natural granular cork', '#A58157', .97, texture='cork')
    frame = walnut('Corkboard dark wood frame', '#38251C')
    box('Large horizontal noticeboard frame', (0, 0, 0), (1.86, .065, .93), frame, .007)
    box('Cork surface', (0, -.037, 0), (1.78, .015, .85), cork)
    paper = material('Vintage map parchment', '#CCB58B', .98)
    ink = material('Original map lines', '#866F4B', .98)
    box('Original vintage style map', (-.30, -.05, .045), (.88, .004, .61), paper)
    # Original schematic contour-map linework, no external artwork.
    for i in range(9):
        beam('Map route line', (-.68 + i * .09, -.054, -.18), (-.59 + i * .08, -.054, .30), .003, .003, ink)
    for i in range(6):
        box('Map latitude line', (-.30, -.055, -.16 + i * .09), (.78, .003, .002), ink)
    land = material('Original vintage map landmasses', '#A08B62', .98)
    for shape in [((- .44, .35), (-.18, .40), (-.08, .22), (-.19, .03), (-.12, -.12), (-.23, -.40), (-.32, -.17), (-.28, .02), (-.42, .13)),
                  ((.03, .30), (.33, .38), (.44, .19), (.26, .09), (.37, -.07), (.27, -.30), (.12, -.16), (.07, .02), (-.03, .14))]:
        mesh = bpy.data.meshes.new('Original map contour')
        mesh.from_pydata([(-.30 + x * .78, -.058, .045 + z * .58) for x, z in shape], [], [tuple(range(len(shape)))])
        mesh.update()
        obj = bpy.data.objects.new('Original map continent silhouette', mesh)
        bpy.context.collection.objects.link(obj)
        finish(obj, obj.name, land)
    mats = [material(f'Pinned photo or note {i}', color, .96) for i, color in enumerate(('#DDD0B5', '#76816E', '#907256', '#B9A084'))]
    for i, (x, z, w, h) in enumerate(((.42, .22, .31, .20), (.56, -.07, .26, .18), (.22, -.26, .17, .13), (-.69, -.31, .16, .11))):
        box('Pinned paper', (x, -.051, z), (w, .004, h), mats[i], rotation=(0, math.radians((-1) ** i * 5), 0))
        if i < 2:
            box('Original landscape photo horizon', (x, -.055, z - .04), (w * .9, .002, h * .34), mats[2])
        if i >= 2:
            for line in range(3):
                box('Original handwritten note line', (x - .012, -.057, z + .025 - line * .025),
                    (w * (.64 - line * .09), .002, .003), ink)
        ellipsoid('Brass pin', (x, -.058, z + h * .4), (.014, .007, .014), silver(), 8, 4)


def decor():
    """Fixed spec decorations in room-local coordinates, exported as one inexpensive asset."""
    wood = walnut('Decor dark walnut', '#38251C')
    brass = material('Decor warm brass', '#AF8E55', .38, 1)
    box('Low cabinet', (.05, 2.24, .32), (1.85, .40, .60), wood, .007)
    for x in (-.4, .49):
        box('Cabinet door', (x, 2.025, .32), (.86, .018, .54), wood, .003)
        box('Cabinet pull', (x + .25, 2.005, .40), (.10, .02, .014), brass)
    artwork(-1.35, 2.465, 1.74, .43, .83, wood)
    # Build right-wall painting facing inward by transforming its meshes.
    before = set(bpy.context.scene.objects)
    artwork(0, 0, 1.74, .43, .83, wood)
    for obj in set(bpy.context.scene.objects) - before:
        x, y = obj.location.x, obj.location.y
        obj.location.x, obj.location.y = 2.95 + y, .92 - x
        obj.rotation_euler.z = -math.pi / 2
    # Narrow right-side shelf.
    for z in (.15, .62, 1.08, 1.55, 1.99):
        box('Narrow right shelf', (2.76, -1.75, z), (.36, .64, .035), wood)
    for y in (-2.06, -1.44):
        box('Narrow shelf upright', (2.76, y, 1.06), (.36, .035, 1.92), wood)
    ceramic = material('Decor ceramic', '#B89E7D', .9)
    for z in (.69, 1.15, 1.62):
        ellipsoid('Shelf pot', (2.73, -1.73, z + .07), (.14, .14, .17), ceramic, 12, 6)
    # Right floor lamp, matching mushroom silhouette.
    before = set(bpy.context.scene.objects)
    lamp(tall=True)
    for obj in set(bpy.context.scene.objects) - before:
        obj.location += Vector((2.29, -.89, 0))
    pot = material('Plant earthenware', '#786048', .9)
    leaf = material('Muted foliage', '#46513B', .88)
    cylinder('Plant pot', (2.50, -.02, .16), .15, .32, pot, 16)
    for i in range(7):
        a = i * 2.4
        start = (2.50, -.02, .25)
        end = (2.50 + .20 * math.cos(a), -.02 + .20 * math.sin(a), .58 + .06 * (i % 3))
        beam('Plant stem', start, end, .009, .009, leaf)
        obj = ellipsoid('Plant leaf', end, (.22, .08, .025), leaf, 10, 6)
        obj.rotation_euler = (0, -.35, a)
    glow = material('Vertical wall lamp warm white', '#FFDBA2', .7, emission=2)
    box('Left wall brass sconce', (-2.94, 1.81, 1.65), (.065, .13, .66), brass, .008)
    box('Left wall sconce diffuser', (-2.90, 1.81, 1.65), (.025, .085, .59), glow, .007)


BUILDERS = {'sofa': sofa, 'ottoman': ottoman, 'desk': desk, 'chair': chair, 'room': room,
            'rug': rug, 'side_table': side_table, 'mushroom_lamp': mushroom_lamp,
            'desk_lamp': desk_lamp, 'bookshelf': bookshelf, 'corkboard': corkboard, 'decor': decor}


def build_asset(name, builder):
    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    builder()
    meshes = [obj for obj in scene.objects if obj.type == 'MESH']
    triangles = 0
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.select_set(False)
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
    if triangles > 6000:
        raise RuntimeError(f'{name}: exceeds 6000 triangle budget ({triangles})')
    root = bpy.data.objects.new(name, None)
    scene.collection.objects.link(root)
    root['units'] = 'meters'
    for obj in meshes:
        obj.parent = root
    bpy.ops.object.select_all(action='SELECT')
    path = OUTPUT / f'{name}.glb'
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True,
        export_yup=True, export_apply=True, export_normals=True, export_texcoords=True,
        export_materials='EXPORT', export_cameras=False, export_lights=False, export_extras=True)
    corners = [obj.matrix_world @ Vector(v) for obj in meshes for v in obj.bound_box]
    report = {'triangles': triangles, 'bytes': path.stat().st_size,
              'blender_bounds_m': [[round(min(v[i] for v in corners), 4) for i in range(3)], [round(max(v[i] for v in corners), 4) for i in range(3)]]}
    print(f"ASSET {name}: {triangles} triangles | {report['bytes']} bytes", flush=True)
    return report


if __name__ == '__main__':
    OUTPUT.mkdir(parents=True, exist_ok=True)
    mac_path = OUTPUT / 'mac.glb'
    mac_hash = hashlib.sha256(mac_path.read_bytes()).hexdigest()
    assert mac_hash == '5a01b2f8f937e3afe8dc136c19d370f2c22002b172396e68cf6efba18923d138', 'Unexpected protected Mac source'
    mac_report = json.loads((OUTPUT / 'manifest.json').read_text())['mac']
    report = {name: build_asset(name, builder) for name, builder in BUILDERS.items()}
    assert hashlib.sha256(mac_path.read_bytes()).hexdigest() == mac_hash, 'Protected Mac changed'
    report['mac'] = mac_report
    print(f"ASSET mac: {mac_report['triangles']} triangles | {mac_path.stat().st_size} bytes | PRESERVED sha256={mac_hash}", flush=True)
    (OUTPUT / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
