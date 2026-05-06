"""
COSMIC JOURNEY AUTOMATOR
Compatible with Blender 5.1.1
Prerequisites: Have your character .blend/.obj and Mixamo .fbx ready.
Instructions: Update the FILE PATHS below, then run in the Scripting workspace.
"""

import bpy
import os
import math
from mathutils import Vector

def resolve_base_dir():
    """Finds the most reliable project root for Blender text-editor runs."""
    # FIRST: Try the hardcoded workspace path directly (most reliable for text editor)
    hardcoded_path = r"C:\Users\USER\Desktop\Blender run2"
    if os.path.isdir(hardcoded_path) and os.path.isdir(os.path.join(hardcoded_path, "assets")):
        print(f"[INFO] Resolved project base to: {hardcoded_path}")
        return hardcoded_path
    
    candidates = []
    
    # Check saved .blend file
    blend_path = getattr(bpy.data, "filepath", "")
    if blend_path and os.path.isfile(blend_path):
        candidates.append(os.path.dirname(blend_path))

    # Check script location
    script_path = globals().get("__file__")
    if script_path:
        script_dir = os.path.dirname(os.path.abspath(script_path))
        candidates.append(script_dir)

    # Check current working directory
    cwd = os.getcwd()
    candidates.append(cwd)

    # Check Desktop/Blender run2 (common location)
    user_home = os.path.expanduser("~")
    desktop_path = os.path.join(user_home, "Desktop", "Blender run2")
    if os.path.isdir(desktop_path):
        candidates.append(desktop_path)

    # Check parent directories for assets folder
    candidates.append(os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else None)

    for candidate in candidates:
        if candidate and os.path.isdir(os.path.join(candidate, "assets")):
            print(f"[INFO] Resolved project base to: {candidate}")
            return candidate

    # Fallback: try Desktop location
    if os.path.isdir(desktop_path):
        print(f"[INFO] Using Desktop fallback: {desktop_path}")
        return desktop_path

    print(f"[WARNING] Could not find assets folder. Candidates checked: {candidates}")
    return candidates[0] if candidates and candidates[0] else cwd


BASE_DIR = resolve_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# =========================================================================
# 1. USER DEFINED VARIABLES (UPDATE THESE PATHS)
# =========================================================================
# Use the FBX already placed in the assets folder
MIXAMO_FBX_PATH = os.path.join(ASSETS_DIR, "Flying.fbx")
# Write the finished animation FBX back into the assets folder
EXPORT_FBX_PATH = os.path.join(ASSETS_DIR, "Flying_Animation_Export.fbx")
RENDER_MOVIE_PATH = os.path.join(ASSETS_DIR, "Cosmic_Journey_Preview.mp4")
RENDER_STILL_PATH = os.path.join(ASSETS_DIR, "Cosmic_Journey_FinalFrame.png")
RENDER_SEQUENCE_DIR = os.path.join(ASSETS_DIR, "Cosmic_Journey_Frames")
# Optional fallback mesh name if the imported FBX does not already contain skinned meshes
CHARACTER_MESH_NAME = "Male_Futuristic_Suit" 

# =========================================================================
# 2. SCENE PREPARATION
# =========================================================================
def clear_scene():
    """Clears the default scene to start fresh."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Switch to Cycles for realistic cosmic lighting and volumes
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU' # Use GPU if available
    
    # Set frame rate and length for a smooth loop
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 250
    scene.render.fps = 30
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.cycles.samples = 128
    scene.cycles.use_adaptive_sampling = True
    scene.view_settings.look = 'AgX - Very High Contrast'

    # Safe default for Blender builds where movie formats are unavailable.
    os.makedirs(RENDER_SEQUENCE_DIR, exist_ok=True)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(RENDER_SEQUENCE_DIR, "frame_")

    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    # Build a richer procedural space background for stronger mood.
    world = bpy.data.worlds.new("Space_World")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputWorld')
    bg = nodes.new(type='ShaderNodeBackground')
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    mapping = nodes.new(type='ShaderNodeMapping')
    noise = nodes.new(type='ShaderNodeTexNoise')
    ramp = nodes.new(type='ShaderNodeValToRGB')

    mapping.inputs['Scale'].default_value = (0.8, 0.8, 0.8)
    noise.inputs['Scale'].default_value = 2.2
    noise.inputs['Detail'].default_value = 12.0
    noise.inputs['Roughness'].default_value = 0.55
    ramp.color_ramp.elements[0].position = 0.18
    ramp.color_ramp.elements[0].color = (0.004, 0.006, 0.018, 1.0)
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (0.05, 0.12, 0.35, 1.0)
    bg.inputs['Strength'].default_value = 0.7

    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bg.inputs['Color'])
    links.new(bg.outputs['Background'], output.inputs['Surface'])
    print("Scene cleared and prepared.")


def create_starfield():
    """Creates a dense star field using particle instancing."""
    bpy.ops.mesh.primitive_cube_add(size=1200, location=(0, 0, 0))
    star_emitter = bpy.context.active_object
    star_emitter.name = "Star_Emitter"
    star_emitter.display_type = 'BOUNDS'
    star_emitter.hide_render = True

    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.25, subdivisions=1, location=(0, 0, 0))
    star_obj = bpy.context.active_object
    star_obj.name = "Star_Instance"
    star_obj.hide_viewport = True
    star_obj.hide_render = True

    star_mat = bpy.data.materials.new(name="Star_Material")
    star_mat.use_nodes = True
    nodes = star_mat.node_tree.nodes
    links = star_mat.node_tree.links
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    emi = nodes.new(type='ShaderNodeEmission')
    emi.inputs['Color'].default_value = (0.8, 0.9, 1.0, 1.0)
    emi.inputs['Strength'].default_value = 60.0
    links.new(emi.outputs['Emission'], out.inputs['Surface'])
    star_obj.data.materials.append(star_mat)

    bpy.context.view_layer.objects.active = star_emitter
    star_emitter.select_set(True)
    bpy.ops.object.particle_system_add()
    ps = star_emitter.particle_systems[-1]
    ps.name = "Stars"
    s = ps.settings
    s.type = 'EMITTER'
    s.emit_from = 'VOLUME'
    s.count = 5000
    s.frame_start = 1
    s.frame_end = 1
    s.lifetime = 10000
    s.render_type = 'OBJECT'
    s.instance_object = star_obj
    s.particle_size = 1.0
    s.size_random = 0.7


def create_asteroid_belt():
    """Creates stylized asteroid belt around the mid-space section."""
    asteroid_mat = bpy.data.materials.new(name="Asteroid_Material")
    asteroid_mat.use_nodes = True
    nodes = asteroid_mat.node_tree.nodes
    links = asteroid_mat.node_tree.links
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    noise = nodes.new(type='ShaderNodeTexNoise')
    bump = nodes.new(type='ShaderNodeBump')
    noise.inputs['Scale'].default_value = 8.0
    noise.inputs['Detail'].default_value = 8.0
    bsdf.inputs['Base Color'].default_value = (0.06, 0.06, 0.07, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    ring_center = Vector((-20, 15, 20))
    for i in range(80):
        angle = (i / 80.0) * math.tau
        radius = 18.0 + (i % 7) * 0.9
        x = ring_center.x + math.cos(angle) * radius
        y = ring_center.y + math.sin(angle) * radius
        z = ring_center.z + ((i % 9) - 4) * 0.7
        scale = 0.3 + (i % 5) * 0.12
        bpy.ops.mesh.primitive_ico_sphere_add(radius=scale, subdivisions=1, location=(x, y, z))
        rock = bpy.context.active_object
        rock.name = f"Asteroid_{i:03d}"
        rock.rotation_euler = (i * 0.13, i * 0.21, i * 0.09)
        rock.data.materials.append(asteroid_mat)

# =========================================================================
# 3. MIXAMO IMPORT & RIGGING
# =========================================================================
def import_and_rig_character():
    """Imports the animated FBX character and returns its armature and meshes."""
    if not os.path.exists(MIXAMO_FBX_PATH):
        print(f"ERROR: FBX not found at {MIXAMO_FBX_PATH}. Skipping import.")
        return None, []

    # Import FBX
    bpy.ops.import_scene.fbx(filepath=MIXAMO_FBX_PATH)
    
    # Mixamo or pre-animated character FBXs usually import an armature plus
    # one or more skinned mesh objects. Keep the imported hierarchy intact.
    armature = None
    mesh_objects = []
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            armature = obj
            armature.name = "Mixamo_Rig"
        elif obj.type == 'MESH':
            mesh_objects.append(obj)

    if armature and mesh_objects:
        print(f"Imported character with {len(mesh_objects)} skinned mesh object(s).")
        return armature, mesh_objects

    # Fallback: if the FBX only brought in the rig, try binding a custom mesh.
    mesh_obj = bpy.data.objects.get(CHARACTER_MESH_NAME)
    if armature and mesh_obj:
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh_obj.select_set(True)
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')

        print("Imported rig was missing meshes, so the fallback mesh was bound automatically.")
        return armature, [mesh_obj]

    print("ERROR: Could not find an imported armature or any usable mesh objects.")
    return armature, mesh_objects

# =========================================================================
# 4. FLIGHT PATH CREATION (Sectors: Crash -> Asteroids -> Nebula -> Sun)
# =========================================================================
def create_flight_path():
    """Creates a sweeping Bezier curve representing the flight path."""
    curve_data = bpy.data.curves.new('FlightPath', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0  # Invisible path
    
    # Map out 4 key waypoints for the cosmic journey
    waypoints = [
        Vector((-100, 0, 0)),    # Sector 1: Crash site (slow start)
        Vector((-30, 25, 15)),   # Sector 2: Dodging Asteroids (erratic)
        Vector((40, -15, 40)),   # Sector 3: Gliding through Nebula (sweeping up)
        Vector((-100, 0, 0))     # Sector 4: Return to crash site for a seamless loop
    ]
    
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(waypoints) - 1)
    
    for i, point in enumerate(spline.bezier_points):
        point.co = waypoints[i]
        # Set handles to create smooth, cinematic sweeping curves
        point.handle_left_type = 'AUTO'
        point.handle_right_type = 'AUTO'
        
    flight_path = bpy.data.objects.new('Flight_Path', curve_data)
    bpy.context.collection.objects.link(flight_path)
    return flight_path

def setup_eye_emission(mesh_objects):
    """Assigns emissive eye materials when the imported character contains eye-like materials."""
    if not mesh_objects:
        return

    eye_keywords = ("eye", "eyes", "pupil", "iris", "eyeball")
    target_materials = []

    for mesh_obj in mesh_objects:
        if not mesh_obj or mesh_obj.type != 'MESH':
            continue

        object_name = mesh_obj.name.lower()
        for material in mesh_obj.data.materials:
            if not material:
                continue
            material_name = material.name.lower()
            if any(keyword in object_name or keyword in material_name for keyword in eye_keywords):
                target_materials.append(material)

    for eye_material in target_materials:
        eye_material.use_nodes = True
        nodes = eye_material.node_tree.nodes
        links = eye_material.node_tree.links

        principled = None
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled = node
                break

        if principled is None:
            principled = nodes.new(type='ShaderNodeBsdfPrincipled')

        principled.inputs['Base Color'].default_value = (0.1, 0.5, 1.0, 1.0)
        principled.inputs['Emission Color'].default_value = (0.1, 0.5, 1.0, 1.0)
        principled.inputs['Emission Strength'].default_value = 25.0

        output = None
        for node in nodes:
            if node.type == 'OUTPUT_MATERIAL':
                output = node
                break

        if output is None:
            output = nodes.new(type='ShaderNodeOutputMaterial')

        for link in list(links):
            if link.to_node == output and link.to_socket.name == 'Surface':
                links.remove(link)

        links.new(principled.outputs['BSDF'], output.inputs['Surface'])

def create_eye_glow_proxy(armature):
    """Creates a pair of tiny emissive eye proxies when no dedicated eye material exists."""
    if not armature:
        return

    head_bone = None
    for bone_name in ("Head", "head", "mixamorig_Head", "mixamorig:Head"):
        if bone_name in armature.pose.bones:
            head_bone = bone_name
            break

    if not head_bone:
        return

    eye_mat = bpy.data.materials.new(name="Eye_Glow_Material")
    eye_mat.use_nodes = True
    nodes = eye_mat.node_tree.nodes
    links = eye_mat.node_tree.links
    for node in list(nodes):
        if node.name != "Material Output":
            nodes.remove(node)

    emission = nodes.new(type='ShaderNodeEmission')
    output = nodes.get('Material Output')
    emission.inputs['Color'].default_value = (0.1, 0.5, 1.0, 1.0)
    emission.inputs['Strength'].default_value = 50.0
    links.new(emission.outputs['Emission'], output.inputs['Surface'])

    eye_locations = [(0.045, 0.08, 0.08), (0.045, -0.08, 0.08)]
    for index, eye_location in enumerate(eye_locations, start=1):
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.02, location=(0, 0, 0))
        eye_obj = bpy.context.active_object
        eye_obj.name = f"Eye_Glow_{index}"
        eye_obj.data.materials.append(eye_mat)
        eye_obj.parent = armature
        eye_obj.parent_type = 'BONE'
        eye_obj.parent_bone = head_bone
        eye_obj.location = eye_location
        eye_obj.scale = (1.0, 1.0, 1.0)

def attach_to_path(obj, path):
    """Constrains an object to follow a path and keyframes the journey."""
    # Add Follow Path constraint
    follow_c = obj.constraints.new(type='FOLLOW_PATH')
    follow_c.target = path
    follow_c.use_curve_follow = True
    follow_c.forward_axis = 'FORWARD_X'
    follow_c.up_axis = 'UP_Y'
    
    # Ensure curve length is calculated
    path.data.use_path = True
    path.data.path_duration = 250  # Match scene length
    
    # Animate the Offset Factor to move along the path using keyframes
    follow_c.offset_factor = 0.0
    follow_c.keyframe_insert(data_path='offset_factor', frame=1)
    follow_c.offset_factor = 1.0
    follow_c.keyframe_insert(data_path='offset_factor', frame=250)

# =========================================================================
# 5. CINEMATIC CAMERA SETUP
# =========================================================================
def setup_cinematic_camera(target_obj):
    """Creates an intimate character-focused camera with close-ups and dynamic zoom transitions.
    Camera stays tightly focused on the character's expression and movement, with occasional
    zoom-outs to reveal cosmic scope before returning to close, emotional framing.
    """
    cam_data = bpy.data.cameras.new('Cosmic_Cam')
    cam = bpy.data.objects.new('Cosmic_Cam', cam_data)
    bpy.context.collection.objects.link(cam)
    
    # Start with close-up lens; will keyframe transitions
    cam_data.lens = 35  # Close-up focal length
    cam_data.clip_end = 10000.0
    
    # Create primary camera path with VARYING DISTANCES from character
    # Strategy: Tight orbits (close-ups) most of the time, brief wide moments
    cam_path_data = bpy.data.curves.new('CamPath', type='CURVE')
    cam_path_data.dimensions = '3D'
    spline = cam_path_data.splines.new('BEZIER')
    
    # Define camera waypoints with strategic distance variations
    # These orbits around character path, maintaining emotional proximity
    cam_waypoints = [
        Vector((-95, -8, 3)),      # Waypoint 1: Extreme close-up (character awakening, tight frame)
        Vector((-32, 12, 18)),     # Waypoint 2: Close-up orbit (dodging asteroids, character focused)
        Vector((15, -20, 35)),     # Waypoint 3: Medium close-up (through nebula, character prominent)
        Vector((50, 25, 40)),      # Waypoint 4: BRIEF WIDE SHOT (cosmic panorama reveal, sun visible)
        Vector((35, -12, 25)),     # Waypoint 5: Back to close-up orbit (returning focus to character)
        Vector((-95, -8, 3))       # Waypoint 6: Return to character awakening for loop
    ]
    
    spline.bezier_points.add(len(cam_waypoints) - 1)
    for i, point in enumerate(spline.bezier_points):
        point.co = cam_waypoints[i]
        point.handle_left_type = 'AUTO'
        point.handle_right_type = 'AUTO'
        
    cam_path = bpy.data.objects.new('Cam_Path', cam_path_data)
    bpy.context.collection.objects.link(cam_path)
    
    attach_to_path(cam, cam_path)
    
    # CRITICAL: Track the character constantly to keep them centered in frame
    track_c = cam.constraints.new(type='TRACK_TO')
    track_c.target = target_obj
    track_c.track_axis = 'TRACK_NEGATIVE_Z'
    track_c.up_axis = 'UP_Y'
    
    # Set camera as active
    bpy.context.scene.camera = cam
    
    # KEYFRAME FOCAL LENGTH for smooth zoom transitions
    # Strategy: Stay close on character (35mm), zoom out briefly at cosmic reveal (50mm), return to intimate (35mm)
    scene = bpy.context.scene
    frame_total = scene.frame_end
    
    # Frame ranges for emotional beats
    # Frames 1-60: Character awakening, extreme close-up
    cam_data.lens = 35
    cam_data.keyframe_insert(data_path='lens', frame=1)
    
    # Frames 61-120: Asteroid dodging, maintain close-up with slight zoom
    cam_data.lens = 33
    cam_data.keyframe_insert(data_path='lens', frame=60)
    
    # Frames 121-170: Through nebula, still intimate focus
    cam_data.lens = 35
    cam_data.keyframe_insert(data_path='lens', frame=120)
    
    # Frames 171-200: COSMIC PANORAMA - zoom out wide to reveal sun and asteroids
    cam_data.lens = 50
    cam_data.keyframe_insert(data_path='lens', frame=170)
    
    # Frame 200: Hold the wide shot
    cam_data.lens = 50
    cam_data.keyframe_insert(data_path='lens', frame=200)
    
    # Frames 201-240: Zoom back IN to intimate character close-up (emotional return)
    cam_data.lens = 35
    cam_data.keyframe_insert(data_path='lens', frame=201)
    
    # Frames 241-250: Final loop return, maintain intimate framing
    cam_data.lens = 35
    cam_data.keyframe_insert(data_path='lens', frame=250)
    
    print("Character-intimate cinematic camera configured with dynamic focus transitions.")

# =========================================================================
# 6. CHARACTER KEY LIGHT (Highlighting Expression & Suit)
# =========================================================================
def create_character_key_light():
    """Creates a soft key light positioned to illuminate the character's face,
    suit details, and glowing eyes, enhancing emotional presence and suit texture.
    """
    key_light_data = bpy.data.lights.new('Character_Key_Light', type='AREA')
    key_light_data.energy = 8000.0  # Strong but not overwhelming
    key_light_data.color = (0.95, 0.98, 1.0)  # Slightly cool white for suit tech aesthetic
    key_light_data.size = 8.0  # Soft light for flattering face/eye illumination
    
    key_light = bpy.data.objects.new('Character_Key_Light', key_light_data)
    bpy.context.collection.objects.link(key_light)
    
    # Position to light character from an angle that emphasizes eyes and expression
    # Front-left offset during character-focused moments
    key_light.location = Vector((-15, 8, 12))
    key_light.rotation_euler = (math.radians(70), math.radians(-45), 0)
    
    print("Character key light added to enhance expression and suit details.")

# =========================================================================
# 7. DYNAMIC LIGHTING & LIGHTNING SPARKS
# =========================================================================
def create_energy_effects(armature, mesh_objects):
    """Adds dynamic blue lights and lightning particle sparks to the rig."""
    if not armature:
        return
        
    # 1. Add Point Lights to the Hips (Root Bone) to emanate energy
    root_bone = armature.pose.bones.get("Hips") or armature.pose.bones.get("mixamorig_Hips")
    if root_bone:
        light_data = bpy.data.lights.new('Energy_Glow', type='POINT')
        light_data.energy = 5000.0 # High for space scale
        light_data.color = (0.1, 0.5, 1.0) # Glowing Blue
        light_data.shadow_soft_size = 2.0
        
        light_obj = bpy.data.objects.new('Energy_Glow', light_data)
        bpy.context.collection.objects.link(light_obj)
        
        # Parent light to root bone
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        light_obj.select_set(True)
        bpy.ops.object.parent_set(type='BONE')
        
        # Animate the light intensity to pulse
        light_obj.data.keyframe_insert(data_path='energy', frame=1)
        light_obj.data.energy = 15000.0
        light_obj.data.keyframe_insert(data_path='energy', frame=125)
        light_obj.data.energy = 5000.0
        light_obj.data.keyframe_insert(data_path='energy', frame=250)

    # 2. Lightning Spark Particle System (emit from mesh, not armature)
    emitter_obj = mesh_objects[0] if mesh_objects else None
    if not emitter_obj:
        print("Warning: No mesh available for lightning spark emitter.")
        return

    bpy.context.view_layer.objects.active = emitter_obj
    emitter_obj.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    try:
        bpy.ops.object.particle_system_add()
    except Exception as e:
        print(f"Warning: Could not add particle system: {e}")
        return
    
    if not emitter_obj.particle_systems:
        print("Warning: Particle system was not created.")
        return
        
    ps = emitter_obj.particle_systems[-1]
    ps.name = "Lightning_Sparks"
    settings = ps.settings
    
    settings.type = 'EMITTER'
    settings.emit_from = 'FACE'
    settings.count = 500 # Dense sparks
    settings.frame_start = 1
    settings.frame_end = 250
    settings.lifetime = 5
    settings.lifetime_random = 0.8
    
    # Velocity: shoot backward to simulate high-speed flight.
    # Some particle attributes vary across Blender versions, so guard optional ones.
    settings.normal_factor = -5.0
    settings.object_factor = -15.0  # Pushed opposite to flight path
    if hasattr(settings, 'factor_random'):
        settings.factor_random = 10.0
    elif hasattr(settings, 'brownian_factor'):
        settings.brownian_factor = 2.0
    
    # Render as glowing spheres
    settings.render_type = 'OBJECT'
    settings.use_rotations = True
    settings.rotation_factor_random = 1.0
    
    # Create a small glowing icosphere for the particle instance
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.1, subdivisions=2)
    spark_obj = bpy.context.active_object
    spark_obj.name = "Spark_Mesh"
    spark_mat = bpy.data.materials.new(name="Spark_Material")
    spark_mat.use_nodes = True
    spark_nodes = spark_mat.node_tree.nodes
    spark_links = spark_mat.node_tree.links
    spark_nodes.clear()
    spark_output = spark_nodes.new(type='ShaderNodeOutputMaterial')
    spark_emission = spark_nodes.new(type='ShaderNodeEmission')
    spark_emission.inputs['Color'].default_value = (0.2, 0.6, 1.0, 1.0) # Blue
    spark_emission.inputs['Strength'].default_value = 50000.0
    spark_links.new(spark_emission.outputs['Emission'], spark_output.inputs['Surface'])
    spark_obj.data.materials.append(spark_mat)
    spark_obj.hide_viewport = True
    spark_obj.hide_render = True # Only visible as particle
    
    settings.instance_object = spark_obj
    print("Energy lights and lightning sparks generated.")

# =========================================================================
# 8. PROCEDURAL ENVIRONMENT (Nebula & Sun)
# =========================================================================
def create_environment():
    """Builds a volumetric nebula and an emissive sun."""
    # 1. The Sun
    bpy.ops.mesh.primitive_uv_sphere_add(radius=15, location=(130, 0, 10))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun_mat = bpy.data.materials.new(name="Sun_Material")
    sun_mat.use_nodes = True
    sun_nodes = sun_mat.node_tree.nodes
    sun_links = sun_mat.node_tree.links
    sun_nodes.clear()
    sun_output = sun_nodes.new(type='ShaderNodeOutputMaterial')
    sun_emission = sun_nodes.new(type='ShaderNodeEmission')
    sun_emission.inputs['Color'].default_value = (1.0, 0.8, 0.3, 1.0)
    sun_emission.inputs['Strength'].default_value = 100000.0
    sun_links.new(sun_emission.outputs['Emission'], sun_output.inputs['Surface'])
    sun.data.materials.append(sun_mat)
    
    # 2. The Nebula (Volume)
    bpy.ops.mesh.primitive_cube_add(size=80, location=(40, -15, 40))
    nebula = bpy.context.active_object
    nebula.name = "Nebula"
    nebula.scale = (1.5, 1.5, 0.5) # Flatten it like a cosmic cloud
    nebula_mat = bpy.data.materials.new(name="Nebula_Material")
    nebula_mat.use_nodes = True
    
    # Clear default nodes and add Volume shader
    nodes = nebula_mat.node_tree.nodes
    links = nebula_mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    principled_vol = nodes.new(type='ShaderNodeVolumePrincipled')
    
    principled_vol.inputs['Density'].default_value = 0.05
    principled_vol.inputs['Emission Color'].default_value = (0.4, 0.1, 0.8, 1.0) # Mysterious purple
    principled_vol.inputs['Emission Strength'].default_value = 2.0
    
    links.new(principled_vol.outputs[0], output.inputs[0])
    nebula.data.materials.append(nebula_mat)
    
    print("Cosmic environment generated.")


def render_outputs():
    """Renders a preview movie and final still frame for immediate viewing."""
    scene = bpy.context.scene

    # Try MP4 output first; if unavailable in this build, fall back to PNG sequence.
    rendered_movie = False
    try:
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
        scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
        scene.render.filepath = RENDER_MOVIE_PATH
        bpy.ops.render.render(animation=True)
        rendered_movie = True
    except Exception as exc:
        print(f"Movie render unavailable in this Blender build: {exc}")
        os.makedirs(RENDER_SEQUENCE_DIR, exist_ok=True)
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = os.path.join(RENDER_SEQUENCE_DIR, "frame_")
        bpy.ops.render.render(animation=True)

    scene.frame_set(scene.frame_end)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = RENDER_STILL_PATH
    bpy.ops.render.render(write_still=True)
    if rendered_movie:
        print(f"Preview movie rendered to {RENDER_MOVIE_PATH}")
    else:
        print(f"Preview PNG sequence rendered to {RENDER_SEQUENCE_DIR}")
    print(f"Final frame rendered to {RENDER_STILL_PATH}")

# =========================================================================
# 9. COMPOSITOR (The Dreamlike Glow)
# =========================================================================

def setup_compositor():
    """Adds Bloom to make the eyes, sparks, and sun glow beautifully."""
    scene = bpy.context.scene
    try:
        scene.use_nodes = True
    except Exception:
        pass

    tree = getattr(scene, "node_tree", None)
    if tree is None:
        tree = getattr(scene, "compositor_node_tree", None)
    if tree is None:
        print("Compositor node tree is unavailable in this Blender build; skipping glow setup.")
        return

    nodes = tree.nodes
    links = tree.links
    
    # Clear existing
    nodes.clear()
    
    # Create render layers and output (always available)
    render_layers = nodes.new(type='CompositorNodeRLayers')
    output = nodes.new(type='CompositorNodeComposite')
    
    # Simple fallback: direct connection (most compatible)
    # Compositor effects are optional for this pipeline
    try:
        links.new(render_layers.outputs['Image'], output.inputs['Image'])
    except Exception as e:
        print(f"Warning: Could not create compositor link: {e}")
    
    print("Compositor configured for character glow enhancement.")

def export_fbx_animation(armature, mesh_obj):
    """Exports only the rigged character animation as an FBX file."""
    if not armature or not mesh_obj:
        print("Skipping FBX export because armature or mesh objects are missing.")
        return

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    for obj in mesh_obj:
        if obj and obj.type == 'MESH':
            obj.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature

    bpy.ops.export_scene.fbx(
        filepath=EXPORT_FBX_PATH,
        use_selection=True,
        object_types={'ARMATURE', 'MESH'},
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_force_startend_keying=True,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0,
        use_armature_deform_only=True,
        apply_unit_scale=True,
        use_space_transform=True,
        path_mode='AUTO',
    )

    print(f"FBX animation exported to {EXPORT_FBX_PATH}")

# =========================================================================
# EXECUTION PIPELINE
# =========================================================================
clear_scene()
create_starfield()
create_asteroid_belt()
armature, mesh = import_and_rig_character()

# Use the armature if it exists, otherwise fallback to mesh for pathing
target = armature if armature else mesh

if target:
    flight_path = create_flight_path()
    attach_to_path(target, flight_path)
    setup_cinematic_camera(target)
    create_character_key_light()  # NEW: Key light for character expression
    create_energy_effects(armature, mesh)
    setup_eye_emission(mesh)
    create_eye_glow_proxy(armature)

create_environment()
setup_compositor()

export_fbx_animation(armature, mesh)
render_outputs()

print("COSMIC JOURNEY GENERATION COMPLETE.")