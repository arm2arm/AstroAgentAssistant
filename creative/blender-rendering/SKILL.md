---
name: blender-rendering
description: Headless Blender 5 rendering from Docker with Cycles CPU, material creation patterns, and S3 delivery. Use when rendering 3D scenes via Blender in container.
tags: [blender, rendering, docker, cycles, python]
---

# Blender Rendering in Headless Docker

## Trigger Conditions
- Rendering 3D scenes with Blender 5.0.1 in headless mode
- Using the `blender-mcp-headless` Docker image
- Cycles CPU rendering (GPU not available in headless containers)

## Environment

**Docker image**: `blender-mcp-headless:latest` (built on linuxserver/blender arm64)

**Blender version**: 5.0.1

**Render device**: CPU only (GPU/GPU-EGL fails in headless mode — produces all-black frames)

## Docker Command Pattern

```bash
docker run --rm \
  -v /path/to/script.py:/scripts/script.py:ro \
  -v /path/to/output:/output:rw \
  blender-mcp-headless:latest \
  blender -b --python /scripts/script.py
```

- `-b` = background mode (no GUI)
- Script must write to `/output/` for files to persist
- Container has Blender at `/usr/bin/blender` (via python3.3 symlink)

## Blender 5.0.1 Migration Notes

### API Changes from Blender 4.x
- `bpy.ops.wm.read_factory_setting` → `bpy.ops.wm.read_factory_settings` (plural "settings")
- `ShaderNodeOutputMaterial.outputs["BSDF"]` → outputs remain "BSDF" for Principled/Glossy
- `ShaderNodeBackground.outputs["BSDF"]` → outputs renamed to `"Background"`
- `Vector.to_track_quaternion()` → still works but prefer `constraints.new(type='TRACK_TO')`
- `Light.data.rotation_euler` → use `Object.rotation_euler` instead (on the light object, not data)
- `Material.use_nodes` → deprecated, will be removed in 6.0 (still works, just warns)
- `Principled BSDF` → `"Specular"` and `"Sheen"` inputs may not exist — always check with:
  ```python
  input_names = [inp.name for inp in principled.inputs]
  if "Specular" in input_names:
      principled.inputs["Specular"].default_value = value
  ```
- Engine enum: `'BLENDER_EEVEE_NEXT'` doesn't exist — use `'BLENDER_EEVEE'` or `'CYCLES'`

### Rendering Gotchas
- **GPU mode fails silently**: Setting `scene.cycles.device = 'GPU'` in headless Docker produces all-black renders (EGL context issues). Always use `'CPU'`.
- **EEVEE needs Wayland**: `BLENDER_EEVEE` requires a display/Wayland socket — may fail in some headless configs. Cycles CPU is most reliable.
- **Denoising works fine** with Cycles CPU.

## Material Patterns

### Mirror (Glossy BSDF)
```python
def make_mirror_mat():
    mat = bpy.data.materials.new("Mirror")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    glossy = nt.nodes.new("ShaderNodeBsdfGlossy")
    glossy.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    glossy.inputs["Roughness"].default_value = 0.005  # not 0.0 — avoids delta issues

    nt.links.new(glossy.outputs["BSDF"], out.inputs["Surface"])
    return mat
```

### Principled with Blender 5 compatibility
```python
def safe_principled(name, base_color, roughness=0.5, metallic=0.0, specular=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (300, 0)

    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.inputs["Base Color"].default_value = base_color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = metallic

    input_names = [inp.name for inp in principled.inputs]
    if "Specular" in input_names:
        principled.inputs["Specular"].default_value = specular

    links.new(principled.outputs["BSDF"], out.inputs["Surface"])
    return mat
```

### World Background
```python
def setup_world(color=(0.15, 0.15, 0.18, 1.0), strength=1.0):
    scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    nodes = scene.world.node_tree.nodes
    links = scene.world.node_tree.links
    nodes.clear()

    w_out = nodes.new("ShaderNodeOutputWorld")
    w_bg = nodes.new("ShaderNodeBackground")
    w_bg.inputs[0].default_value = color
    w_bg.inputs[1].default_value = strength
    links.new(w_bg.outputs["Background"], w_out.inputs["Surface"])
```

## Camera & Lighting Patterns

### Camera with Track To
```python
bpy.ops.object.camera_add()
camera = bpy.context.object
camera.location = Vector((x, y, z))  # top-down 45° angle

target = bpy.data.objects.new("CamTarget", None)
bpy.context.collection.objects.link(target)
target.location = Vector((look_x, look_y, look_z))

constraint = camera.constraints.new(type='TRACK_TO')
constraint.target = target
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'
scene.camera = camera
```

### Three-Point Lighting
```python
# Key light
bpy.ops.object_light_add(type='SUN')
key = bpy.context.object
key.data.energy = 10.0
key.rotation_euler = (math.radians(35), 0, math.radians(45))

# Fill light
bpy.ops.object_light_add(type='SUN')
fill = bpy.context.object
fill.data.energy = 4.0
fill.rotation_euler = (math.radians(55), 0, math.radians(-135))

# Rim light
bpy.ops.object_light_add(type='SUN')
rim = bpy.context.object
rim.data.energy = 6.0
rim.rotation_euler = (math.radians(20), 0, math.radians(200))
```

## Mirror Geometry

### Correct Mirror Plane Setup
Blender's `primitive_plane_add()` creates a plane in the XY-plane (normal = +Z). For a vertical mirror facing +Y:

```python
bpy.ops.mesh.primitive_plane_add()
mirror = bpy.context.object
mirror.location = (0, -3.0, 0.5)  # mirror position
mirror.rotation_euler = (math.radians(90), 0, 0)  # rotate to YZ plane, facing +Y
mirror.scale = (width * 0.48, 1.0, height * 0.48)  # scale X and Z (not Y)
```

### Mirror Visibility Issues
- **Mirror appears invisible**: Check the plane rotation — default plane faces +Z (up), not +Y (forward)
- **No reflection**: Ensure `glossy_bounces >= 8` in Cycles settings
- **Reflection too faint**: Increase world background strength (3.0+) and add more lights
- **Mirror shows as gray**: The Glossy BSDF reflects the environment — use a brighter world or add colored environment

## Render Settings Template
```python
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'  # Always CPU in headless Docker
scene.cycles.samples = 256   # or 512/1024 for final
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 12
scene.cycles.glossy_bounces = 8  # Critical for mirror reflections
scene.cycles.diffuse_bounces = 8
scene.cycles.transmission_bounces = 8
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
```

## Delivery Pipeline
```bash
# After render, upload to S3 and get Telegram URL
python3 ~/.hermes/scripts/s3_media_upload.py /output/render.png
```

## Project Location
- Scripts: `/home/hermes/projects/manim-tutorials/scripts/`
- Output: `/home/hermes/projects/manim-tutorials/output/`
- Docker image: `blender-mcp-headless:latest`
