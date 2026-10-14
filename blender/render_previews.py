"""Warm previews of every exported GLB, plus the app's shared layout.
Run: blender -b -P blender/render_previews.py. Cycles CPU, no external textures.
"""
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
MODELS, OUTPUT = ROOT / 'public/models', ROOT / 'previews'
LAYOUT = json.loads((ROOT / 'src/components/room/scene-layout.json').read_text())


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def load(name, location=(0, 0, 0), rotation=0):
    previous = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(MODELS / f'{name}.glb'))
    imported = set(bpy.context.scene.objects) - previous
    for obj in imported:
        if obj.parent not in imported:
            obj.location += Vector(location)
            obj.rotation_mode = 'XYZ'
            obj.rotation_euler.z += rotation
    return imported


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def area(name, location, target, energy, size, color=(1, .81, .62)):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy, data.shape, data.size, data.color = energy, 'DISK', size, color
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, target)


def point(name, location, energy, radius=.12, color=(1, .71, .43)):
    data = bpy.data.lights.new(name, 'POINT')
    data.energy, data.shadow_soft_size, data.color = energy, radius, color
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location


def setup(position, target, interior=False):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device, scene.cycles.samples = 'CPU', 20
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 6
    scene.render.resolution_x, scene.render.resolution_y = 960, 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = -.35
    scene.view_settings.gamma = 1
    scene.world = bpy.data.worlds.new('Quiet warm environment')
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (.35, .31, .26, 1)
    bg.inputs['Strength'].default_value = .20 if interior else .45
    data = bpy.data.cameras.new('Preview camera')
    camera = bpy.data.objects.new('Preview camera', data)
    scene.collection.objects.link(camera)
    camera.location = position
    aim(camera, target)
    data.lens, data.clip_start = 21, .01
    scene.camera = camera
    if interior:
        area('3000K ceiling soft fill', (0, -.4, 2.65), (0, .3, 0), 160, 2.5)
        area('3000K window soft key', (2.86, -.25, 1.9), (-.5, .3, .7), 100, 1.4)
        area('2700K rear wall wash', (0, 1.9, 2.65), (0, 2.4, 1.1), 16, 1.3, (1, .74, .48))
    else:
        data.type, data.ortho_scale = 'ORTHO', 3
        area('3000K large soft key', (1.6, -2, 4), target, 240, 3.5)
        area('3000K gentle fill', (-2, -.5, 2.5), target, 100, 3)
        area('2700K edge highlight', (.8, 2, 3), target, 110, 2.5, (1, .74, .48))


def studio_floor():
    mat = bpy.data.materials.new('Preview-only sand ground')
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (.20, .16, .12, 1)
    shader.inputs['Roughness'].default_value = .95
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.005))
    bpy.context.object.data.materials.append(mat)


def frame_asset(objects):
    bpy.context.view_layer.update()
    camera = bpy.context.scene.camera
    orientation = camera.rotation_euler.to_matrix()
    inverse = orientation.transposed()
    corners = [inverse @ (obj.matrix_world @ Vector(c) - camera.location) for obj in objects if obj.type == 'MESH' for c in obj.bound_box]
    left, right = min(v.x for v in corners), max(v.x for v in corners)
    bottom, top = min(v.y for v in corners), max(v.y for v in corners)
    camera.location += orientation @ Vector(((left + right) / 2, (bottom + top) / 2, 0))
    render = bpy.context.scene.render
    camera.data.ortho_scale = max(right - left, (top - bottom) * render.resolution_x / render.resolution_y) * 1.20


def practical_lights():
    x, y, z = LAYOUT['mushroom_lamp']['position']
    point('2700K sofa mushroom', (x, -z, y + .29), 12)
    x, y, z = LAYOUT['desk_lamp']['position']
    point('2700K desk mushroom', (x, -z, y + .28), 10)
    point('2700K right floor mushroom', (2.29, -.89, 1.22), 24, .18)
    point('2700K left sconce', (-2.79, 1.81, 1.65), 10)
    for height in (.48, .98, 1.50, 1.99, 2.45):
        area('2400–2700K bookshelf LED wash', (-2.48, .55, height), (-2.3, .55, height - .35), 7, .65, (1, .70, .40))


def render(name):
    path = OUTPUT / f'{name}.png'
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(f'PREVIEW {path.name} | {path.stat().st_size} bytes', flush=True)


if __name__ == '__main__':
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name in json.loads((MODELS / 'manifest.json').read_text()):
        clear_scene()
        objects = load(name)
        if name in ('room', 'decor'):
            setup((.75, -2.23, 1.75), (-.10, 1.0, 1.02), interior=True)
            if name == 'decor':
                load('room')
                practical_lights()
        else:
            setup((2.6, -3.8, 2.6), (0, 0, .60))
            if name == 'corkboard':
                camera = bpy.context.scene.camera
                camera.location = (1, -4, .5)
                aim(camera, (0, 0, 0))
            frame_asset(objects)
            studio_floor()
        render(name)
    clear_scene()
    for name, placement in LAYOUT.items():
        x, y, z = placement['position']
        load(name, (x, -z, y), placement['rotation'])
    setup((0, -2.43, 2.50), (0, .40, .70), interior=True)
    bpy.context.scene.camera.data.lens = 13.5
    practical_lights()
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 1280, 800
    scene.cycles.samples = 40
    render('combined')
