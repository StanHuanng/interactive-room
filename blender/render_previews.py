"""Render imported GLBs using Cycles CPU. Run: blender -b -P blender/render_previews.py.

Individual previews use a warm studio floor; the combined preview is photographed
from inside the complete four-wall room. No exported meshes are hidden or removed.
"""

import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "public" / "models"
OUTPUT = ROOT / "previews"


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def load(name, location=(0, 0, 0), rotation=0):
    previous = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(MODELS / f"{name}.glb"))
    imported = set(bpy.context.scene.objects) - previous
    roots = [obj for obj in imported if obj.parent not in imported]
    for obj in roots:
        obj.location += Vector(location)
        obj.rotation_mode = "XYZ"
        obj.rotation_euler.z += rotation
    return imported


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area(name, location, target, energy, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, target)


def setup(camera_position, target, ortho=None):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.world = bpy.data.worlds.new("Warm studio world")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.60, 0.49, 0.37, 1)
    background.inputs["Strength"].default_value = 0.35
    data = bpy.data.cameras.new("Preview camera")
    camera = bpy.data.objects.new("Preview camera", data)
    scene.collection.objects.link(camera)
    camera.location = camera_position
    aim(camera, target)
    data.lens = 24
    data.clip_start = 0.01
    if ortho:
        data.type = "ORTHO"
        data.ortho_scale = ortho
    scene.camera = camera
    area("Warm key", (1.6, -2, 4.5), target, 450, 4, (1.0, 0.80, 0.61))
    area("Soft window fill", (-2.5, -0.4, 3), target, 250, 3, (0.83, 0.90, 1.0))
    area("Warm rim", (0.8, 2.0, 4), target, 300, 2.5, (1.0, 0.89, 0.72))


def studio_floor():
    mat = bpy.data.materials.new("Preview ground")
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (0.30, 0.255, 0.20, 1)
    shader.inputs["Roughness"].default_value = 0.95
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.003))
    bpy.context.object.name = "Preview-only studio floor"
    bpy.context.object.data.materials.append(mat)


def frame_asset(objects):
    """Fit projected mesh bounds with margin, independent of aspect ratio."""
    bpy.context.view_layer.update()
    camera = bpy.context.scene.camera
    orientation = camera.rotation_euler.to_matrix()
    inverse = orientation.transposed()
    corners = [inverse @ (obj.matrix_world @ Vector(corner) - camera.location)
               for obj in objects if obj.type == "MESH" for corner in obj.bound_box]
    left, right = min(v.x for v in corners), max(v.x for v in corners)
    bottom, top = min(v.y for v in corners), max(v.y for v in corners)
    camera.location += orientation @ Vector(((left + right) / 2, (bottom + top) / 2, 0))
    render_settings = bpy.context.scene.render
    aspect = render_settings.resolution_x / render_settings.resolution_y
    camera.data.ortho_scale = max(right - left, (top - bottom) * aspect) * 1.20


def render(name):
    path = OUTPUT / f"{name}.png"
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(f"PREVIEW {path} ({path.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, position, target, scale in (
        ("sofa", (3, -4, 2.7), (0, 0, 0.42), 3.6),
        ("desk", (2.6, -3.4, 2.3), (0, 0, 0.36), 2.9),
        ("mac", (1.05, -1.6, 0.95), (0, 0, 0.27), 1.2),
        ("chair", (1.6, -2.5, 1.65), (0, 0, 0.5), 1.85),
        ("room", (2.5, -2.1, 2.3), (-0.7, 1.0, 1.0), None),
    ):
        clear_scene()
        objects = load(name)
        setup(position, target, scale)
        if name != "room":
            frame_asset(objects)
            studio_floor()
        render(name)
    clear_scene()
    load("room")
    load("desk", (-1.6, 1.45, 0))
    load("mac", (-1.6, 1.45, 0.75))
    load("chair", (-1.6, 0.45, 0), math.pi)
    load("sofa", (1.4, 1.25, 0))
    setup((0.6, -2.2, 1.8), (-0.1, 1.1, 0.8))
    # Match the wide interior view without crossing any of the four walls.
    bpy.context.scene.camera.data.lens = 20
    render("combined")
