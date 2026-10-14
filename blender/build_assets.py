"""Original low-poly furniture, in meters. Run: blender -b -P blender/build_assets.py.

Blender Z-up becomes glTF Y-up. Furniture faces Blender -Y (glTF +Z).
Every exported mesh has applied transforms and shares the floor-center origin.
"""

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public" / "models"


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(collection):
            if block.users == 0:
                collection.remove(block)


def material(name, color, roughness=0.7, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if emission:
        shader.inputs["Emission Color"].default_value = (*emission, 1)
        shader.inputs["Emission Strength"].default_value = 0.18
    return mat


def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Single-facet edges", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for face in obj.data.polygons:
        face.use_smooth = False
    return obj


def box(name, center, size, mat, bevel=0, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.dimensions = size
    if rotation:
        obj.rotation_euler = rotation
    return finish(obj, name, mat, bevel)


def cylinder(name, center, radius, depth, mat, vertices=10, rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                       end_fill_type="NGON", location=center)
    obj = bpy.context.object
    if rotation:
        obj.rotation_euler = rotation
    return finish(obj, name, mat)


def beam(name, start, end, width, depth, mat, bevel=0):
    direction = Vector(end) - Vector(start)
    obj = box(name, (Vector(start) + Vector(end)) / 2,
              (width, depth, direction.length), mat, bevel)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return obj


def sofa():
    red = material("Sofa | garnet fabric", (0.42, 0.035, 0.045), 0.93)
    cushion = material("Sofa | red cushions", (0.56, 0.055, 0.065), 0.95)
    wood = material("Sofa | dark wood", (0.055, 0.026, 0.017))
    for x in (-0.87, 0.87):
        for y in (-0.32, 0.32):
            box("Sofa leg", (x, y, 0.085), (0.09, 0.09, 0.17), wood, 0.008)
    box("Sofa upholstered base", (0, 0, 0.25), (2.0, 0.86, 0.20), red, 0.035)
    box("Sofa back frame", (0, 0.365, 0.575), (2.02, 0.17, 0.55), red, 0.04)
    for x in (-0.95, 0.95):
        box("Sofa armrest", (x, -0.025, 0.455), (0.20, 0.85, 0.41), red, 0.035)
    for index, x in enumerate((-0.57, 0, 0.57), 1):
        box(f"Seat cushion {index}", (x, -0.065, 0.385), (0.55, 0.67, 0.14), cushion, 0.025)
        box(f"Back cushion {index}", (x, 0.25, 0.63), (0.55, 0.15, 0.40), cushion,
            0.03, (math.radians(8), 0, 0))


def desk():
    walnut = material("Desk | dark walnut", (0.12, 0.054, 0.028), 0.63)
    edge = material("Desk | walnut edge", (0.075, 0.028, 0.012), 0.72)
    metal = material("Desk | drawer pull", (0.20, 0.21, 0.22), 0.3, 0.75)
    box("Desk top", (0, 0, 0.715), (1.6, 0.75, 0.07), walnut, 0.012)
    for x in (-0.69, 0.69):
        for y in (-0.265, 0.265):
            box("Desk leg", (x, y, 0.34), (0.065, 0.065, 0.68), edge, 0.004)
    box("Desk rear apron", (0, 0.28, 0.62), (1.44, 0.045, 0.12), edge, 0.004)
    for x in (-0.69, 0.69):
        box("Desk side apron", (x, 0, 0.62), (0.045, 0.56, 0.12), edge, 0.004)
    box("Desk drawer housing", (0.44, 0, 0.585), (0.40, 0.57, 0.18), edge, 0.008)
    box("Desk drawer front", (0.44, -0.30, 0.585), (0.39, 0.028, 0.16), walnut, 0.005)
    box("Desk drawer handle", (0.44, -0.325, 0.585), (0.15, 0.025, 0.018), metal, 0.004)


def mac():
    silver = material("Computer | aluminum", (0.56, 0.59, 0.62), 0.3, 0.78)
    black = material("Computer | black bezel", (0.009, 0.012, 0.017), 0.3)
    screen = material("Computer | dark luminous screen", (0.015, 0.045, 0.065),
                      0.38, emission=(0.06, 0.16, 0.24))
    key = material("Computer | light keys", (0.78, 0.80, 0.81), 0.5)
    indicator = material("Computer | camera", (0.018, 0.03, 0.025), 0.35)
    box("Computer stand foot", (0, 0.10, 0.012), (0.24, 0.20, 0.024), silver, 0.007)
    beam("Computer stand neck", (0, 0.12, 0.024), (0, 0.17, 0.20), 0.07, 0.028, silver, 0.005)
    box("Computer aluminum enclosure", (0, 0.16, 0.355), (0.62, 0.036, 0.395), silver, 0.012)
    box("Computer black bezel", (0, 0.137, 0.38), (0.599, 0.010, 0.32), black, 0.004)
    box("Computer screen", (0, 0.1305, 0.381), (0.56, 0.003, 0.285), screen)
    cylinder("Computer webcam", (0, 0.130, 0.533), 0.003, 0.003, indicator,
             vertices=8, rotation=(math.pi / 2, 0, 0))
    box("Keyboard case", (-0.04, -0.225, 0.012), (0.43, 0.135, 0.024), silver, 0.006)
    # Grouped rows imply keys without hundreds of tiny triangles.
    for row in range(4):
        box("Keyboard key row", (-0.04, -0.18 - row * 0.025, 0.027),
            (0.385, 0.016, 0.006), key, 0.001)
    box("Keyboard space bar", (-0.055, -0.279, 0.027), (0.17, 0.012, 0.006), key)
    box("Mouse", (0.28, -0.225, 0.019), (0.061, 0.10, 0.038), key, 0.016)
    box("Mouse touch seam", (0.28, -0.24, 0.0385), (0.0015, 0.037, 0.001), silver)


def chair():
    black = material("Chair | charcoal upholstery", (0.025, 0.03, 0.035), 0.9)
    frame = material("Chair | black frame", (0.012, 0.015, 0.019), 0.5)
    steel = material("Chair | gas lift steel", (0.30, 0.32, 0.34), 0.3, 0.8)
    cylinder("Chair base hub", (0, 0, 0.125), 0.075, 0.085, frame)
    for index in range(5):
        angle = 2 * math.pi * index / 5 + math.pi / 2
        dx, dy = math.cos(angle), math.sin(angle)
        beam("Chair base spoke", (0.035 * dx, 0.035 * dy, 0.14),
             (0.29 * dx, 0.29 * dy, 0.095), 0.055, 0.035, frame, 0.004)
        # Wheel axle is horizontal and tangent to each spoke.
        for offset in (-0.017, 0.017):
            wheel = cylinder("Chair caster", (0.30 * dx - offset * dy,
                                                0.30 * dy + offset * dx, 0.04),
                             0.04, 0.024, frame, vertices=8)
            wheel.rotation_euler = Vector((-dy, dx, 0)).to_track_quat("Z", "Y").to_euler()
        box("Chair caster fork", (0.30 * dx, 0.30 * dy, 0.079),
            (0.036, 0.036, 0.042), frame, 0.004)
    cylinder("Chair gas lift sleeve", (0, 0, 0.22), 0.040, 0.19, frame)
    cylinder("Chair gas lift piston", (0, 0, 0.365), 0.024, 0.18, steel)
    box("Chair seat pan", (0, 0, 0.44), (0.49, 0.46, 0.05), frame, 0.02)
    box("Chair seat cushion", (0, -0.02, 0.485), (0.50, 0.47, 0.08), black, 0.03)
    beam("Chair back support", (0, 0.18, 0.43), (0, 0.25, 0.85), 0.07, 0.035, frame, 0.005)
    box("Chair back shell", (0, 0.245, 0.775), (0.45, 0.075, 0.46), frame,
        0.025, (math.radians(-8), 0, 0))
    box("Chair back cushion", (0, 0.20, 0.775), (0.42, 0.08, 0.42), black,
        0.025, (math.radians(-8), 0, 0))
    for x in (-0.29, 0.29):
        beam("Chair arm support", (x, 0.06, 0.46), (x, 0.06, 0.66), 0.03, 0.045, frame)
        box("Chair armrest", (x, 0, 0.675), (0.075, 0.33, 0.045), black, 0.012)


def join_parts(name, parts):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    parts[0].name = name
    return parts[0]


def room():
    beige = material("Room | warm beige plaster", (0.68, 0.58, 0.45), 0.95)
    trim = material("Room | cream baseboards", (0.82, 0.75, 0.62), 0.7)
    timber = [material(f"Room | oak plank {i}", color, 0.8) for i, color in enumerate(
        ((0.38, 0.22, 0.105), (0.44, 0.27, 0.13), (0.48, 0.30, 0.15),
         (0.41, 0.24, 0.11), (0.46, 0.28, 0.14)))]
    subfloor = material("Room | plank seams", (0.13, 0.074, 0.033), 0.9)
    box("Floor foundation", (0, 0, -0.071), (6, 5, 0.098), subfloor)
    planks = []
    for row in range(20):
        # Stagger the joints, with clipped end planks at the room boundary.
        edges = [-3] + [x + (0.6 if row % 2 else 0) for x in (-1.8, -0.6, 0.6, 1.8)] + [3]
        for col, (left, right) in enumerate(zip(edges, edges[1:])):
            planks.append(box("Oak plank", ((left + right) / 2, -2.375 + row * 0.25, -0.011),
                              (right - left - 0.003, 0.247, 0.022), timber[(row * 3 + col) % 5]))
    join_parts("Floor oak planks", planks)
    # Wall inner faces sit exactly at the 6 x 5 m room boundary.
    box("Wall back", (0, 2.58, 1.4), (6.32, 0.16, 2.8), beige)
    box("Wall front", (0, -2.58, 1.4), (6.32, 0.16, 2.8), beige)
    box("Wall right", (3.08, 0, 1.4), (0.16, 5, 2.8), beige)
    # One joined mesh around a real 1.8 x 1.2 m opening; no transparent wall.
    pieces = [
        box("Window wall lower", (-3.08, 0, 0.5), (0.16, 5, 1.0), beige),
        box("Window wall upper", (-3.08, 0, 2.5), (0.16, 5, 0.6), beige),
        box("Window wall side", (-3.08, -1.7, 1.6), (0.16, 1.6, 1.2), beige),
        box("Window wall side", (-3.08, 1.7, 1.6), (0.16, 1.6, 1.2), beige),
    ]
    join_parts("Wall left window opening", pieces)
    for y in (-2.49, 2.49):
        box("Baseboard front" if y < 0 else "Baseboard back", (0, y, 0.055), (6, 0.035, 0.11), trim)
    for x in (-2.99, 2.99):
        box("Baseboard left" if x < 0 else "Baseboard right", (x, 0, 0.055), (0.035, 5, 0.11), trim)
    box("Window sill", (-3.035, 0, 1.005), (0.30, 1.94, 0.07), trim, 0.006)
    for y in (-0.925, 0.925):
        box("Window upright", (-3.0, y, 1.62), (0.08, 0.065, 1.23), trim, 0.003)
    box("Window lintel trim", (-3.0, 0, 2.215), (0.08, 1.92, 0.065), trim, 0.003)
    box("Window mullion", (-3.045, 0, 1.6), (0.055, 0.035, 1.18), trim)


BUILDERS = {"sofa": sofa, "desk": desk, "mac": mac, "chair": chair, "room": room}


def build_asset(name, builder):
    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    builder()
    meshes = [obj for obj in scene.objects if obj.type == "MESH"]
    triangle_count = 0
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.select_set(False)
        obj.data.calc_loop_triangles()
        triangle_count += len(obj.data.loop_triangles)
    if triangle_count >= 3000:
        raise RuntimeError(f"{name}: exceeds triangle budget ({triangle_count})")
    root = bpy.data.objects.new(name, None)
    scene.collection.objects.link(root)
    root["units"] = "meters"
    root["origin"] = "floor surface center"
    for obj in meshes:
        obj.parent = root
    bpy.ops.object.select_all(action="SELECT")
    path = OUTPUT / f"{name}.glb"
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True,
                              export_yup=True, export_apply=True, export_normals=True,
                              export_texcoords=False, export_materials="EXPORT",
                              export_cameras=False, export_lights=False, export_extras=True)
    corners = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    bounds = [[round(min(v[i] for v in corners), 4) for i in range(3)],
              [round(max(v[i] for v in corners), 4) for i in range(3)]]
    result = {"triangles": triangle_count, "bytes": path.stat().st_size,
              "blender_bounds_m": bounds}
    print(f"ASSET {name}: {triangle_count} triangles | {result['bytes']} bytes | {path}", flush=True)
    return result


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {name: build_asset(name, builder) for name, builder in BUILDERS.items()}
    (OUTPUT / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
