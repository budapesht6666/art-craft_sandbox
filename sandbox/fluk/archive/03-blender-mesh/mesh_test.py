"""Проверка: рисунок Gemini на сетке гнётся костями (как в Live2D / Spine), Blender 5.2.

blender -b --factory-startup --python-exit-code 1 -P mesh_test.py -- OUT_DIR
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector

HERE = Path(__file__).parent
SPRITE = HERE.parent.parent / "art" / "cut" / "poses" / "pose_05.png"
OUT = Path(sys.argv[sys.argv.index("--") + 1])
PX = 100.0  # пикселей на единицу Blender

sc = bpy.context.scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob)
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "Standard"
sc.render.resolution_x = sc.render.resolution_y = 900
world = bpy.data.worlds.new("w")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.72, 0.85, 1)

img = bpy.data.images.load(str(SPRITE))
img.alpha_mode = "STRAIGHT"
W, H = img.size


def px(x, y):
    """Пиксель спрайта -> мировые координаты (плоскость XZ, центр картинки в нуле)."""
    return Vector(((x - W / 2) / PX, 0.0, (H / 2 - y) / PX))


# сетка с UV, повёрнута к камере
me = bpy.data.meshes.new("sprite")
bm = bmesh.new()
bm.loops.layers.uv.new("UVMap")  # calc_uvs пишет только в уже существующий UV-слой
bmesh.ops.create_grid(bm, x_segments=60, y_segments=60, size=0.5, calc_uvs=True)
bm.to_mesh(me)
bm.free()
ob = bpy.data.objects.new("sprite", me)
ob.rotation_euler = (math.pi / 2, 0, 0)
ob.scale = (W / PX, H / PX, 1)
sc.collection.objects.link(ob)

mat = bpy.data.materials.new("sprite")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = img
tex.interpolation = "Cubic"
emi = nt.nodes.new("ShaderNodeEmission")
tra = nt.nodes.new("ShaderNodeBsdfTransparent")
mix = nt.nodes.new("ShaderNodeMixShader")
out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(tex.outputs["Color"], emi.inputs["Color"])
nt.links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
nt.links.new(tra.outputs[0], mix.inputs[1])
nt.links.new(emi.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], out.inputs["Surface"])
try:
    mat.surface_render_method = "BLENDED"
except Exception as e:  # noqa: BLE001
    print("render method:", e)
me.materials.append(mat)

# кости в плоскости XZ (пиксельные координаты спрайта)
BONES = {  # имя: (родитель, начало, конец)
    "body": (None, (300, 560), (330, 300)),
    "head": ("body", (350, 300), (370, 60)),
    "tail1": ("body", (230, 500), (120, 470)),
    "tail2": ("tail1", (120, 470), (30, 455)),
}
arm_data = bpy.data.armatures.new("rig")
arm = bpy.data.objects.new("rig", arm_data)
sc.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
for name, (parent, a, b) in BONES.items():
    eb = arm_data.edit_bones.new(name)
    eb.head, eb.tail = px(*a), px(*b)
    eb.align_roll(Vector((0, -1, 0)))  # локальная Z = к камере: поворот вокруг Z — в плоскости рисунка
    if parent:
        eb.parent = arm_data.edit_bones[parent]
bpy.ops.object.mode_set(mode="OBJECT")

# веса по расстоянию до отрезков костей
world_verts = np.array([tuple(ob.matrix_world @ v.co) for v in me.vertices])[:, [0, 2]]


def seg_dist(p, a, b):
    ab = b - a
    t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(p - (a + t[:, None] * ab), axis=1)


names = list(BONES)
d = np.stack([seg_dist(world_verts, np.array(px(*BONES[n][1]))[[0, 2]], np.array(px(*BONES[n][2]))[[0, 2]])
              for n in names], axis=1)
w = 1 / (d + 0.05) ** 4
w /= w.sum(axis=1, keepdims=True)
for i, n in enumerate(names):
    vg = ob.vertex_groups.new(name=n)
    for vi in range(len(me.vertices)):
        if w[vi, i] > 0.001:
            vg.add([vi], float(w[vi, i]), "REPLACE")
mod = ob.modifiers.new("rig", "ARMATURE")
mod.object = arm

cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = max(W, H) / PX * 1.25
cam = bpy.data.objects.new("cam", cam_data)
cam.location = (0, -10, 0)
cam.rotation_euler = (math.pi / 2, 0, 0)
sc.collection.objects.link(cam)
sc.camera = cam

OUT.mkdir(parents=True, exist_ok=True)
for tag, pose in (("rest", {}), ("posed", {"body": -6, "head": 14, "tail1": -25, "tail2": -40})):
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (0, 0, math.radians(pose.get(pb.name, 0)))
    sc.render.filepath = str(OUT / f"mesh_{tag}.png")
    bpy.ops.render.render(write_still=True)
