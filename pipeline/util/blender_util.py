import bpy
from mathutils import Vector
from pathlib import Path
import numpy as np
import random
import math
import os

# Import all stl files from input folder
def import_stl_folder(input_dir):
    files = os.listdir(input_dir)
    for file in files:
        absolut = os.path.join(input_dir, file)
        bpy.ops.import_mesh.stl(
            filepath=absolut, axis_forward='Y', axis_up='Z')
        
# Calculate BBox of objects
def calcBoundingBox(objs):
    cornerApointsX = []
    cornerApointsY = []
    cornerApointsZ = []
    cornerBpointsX = []
    cornerBpointsY = []
    cornerBpointsZ = []

    for ob in objs:
        bbox_corners = [ob.matrix_world @
                        Vector(corner) for corner in ob.bound_box]
        cornerApointsX.append(bbox_corners[0].x)
        cornerApointsY.append(bbox_corners[0].y)
        cornerApointsZ.append(bbox_corners[0].z)
        cornerBpointsX.append(bbox_corners[6].x)
        cornerBpointsY.append(bbox_corners[6].y)
        cornerBpointsZ.append(bbox_corners[6].z)

    minA = Vector((min(cornerApointsX), min(
        cornerApointsY), min(cornerApointsZ)))
    maxB = Vector((max(cornerBpointsX), max(
        cornerBpointsY), max(cornerBpointsZ)))

    center_point = Vector(
        ((minA.x + maxB.x)/2, (minA.y + maxB.y)/2, (minA.z + maxB.z)/2))
    dimensions = Vector((maxB.x - minA.x, maxB.y - minA.y, maxB.z - minA.z))

    return center_point, dimensions

# Center objects in scene
def center_objects(objs):
    center_point, _ = calcBoundingBox(objs)
    for obj in objs:
        obj.location -= center_point
        obj.rotation_euler = (0.0, 0.0, 0.0)
        
# Unhide all objects in scene
def unhide_all():
    for object in bpy.data.objects:
        object.hide_viewport = False
        
# Unselect all objects in scene
def unselect_all():
    for obj in bpy.data.objects:
        obj.select_set(False)

# Select objects specified in objs list
def select_objs(objs):
    unselect_all()
    for obj in objs:
        obj.select_set(True)

# Rescale objects in scene
def rescale_all(objs, value=(1, 1, 1)):
    unselect_all()
    select_objs(objs)

    bpy.ops.transform.resize(value=value, orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, True), mirror=True,
                            use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)
    unselect_all()

# Re-size and center mesh objects
def norm_and_center(mesh_objs):
    unhide_all()
    center, dims = calcBoundingBox(mesh_objs)
    select_objs(mesh_objs)
    resize_factor = 1 / max(dims)
    rescale_all(mesh_objs, (resize_factor, resize_factor, resize_factor))
    center_objects(mesh_objs)
    return center, dims

def fibonacci_sphere(n, r):
    """
    This function generates n points evenly spaced on the surface of a sphere of radius r.
    Uses the fibonacci lattice / golden spiral method.

    :param n: number of points to generate.
    :param r: sphere radius.
    """
    from numpy import pi, cos, sin, arccos, arange

    # generate indices for each point
    indices = arange(0, n, dtype=float) + 0.5

    # Calculate angles phi and theta
    phi = arccos(1 - 2*indices/n)
    theta = pi * (1 + 5**0.5) * indices

    # calculate x,y,z cartersian coordinates
    x, y, z = cos(theta) * sin(phi), sin(theta) * sin(phi), cos(phi)

    # Scale coordinates by radius
    x, y, z = x * r, y * r, z * r

    # Round each coordinate to 3 decimal places
    round_3 = lambda x: round(x, 3)
    x = np.fromiter(map(round_3, x), dtype=float)
    y = np.fromiter(map(round_3, y), dtype=float)
    z = np.fromiter(map(round_3, z), dtype=float)

    # Combine x,y,z coordinates into list of tuples
    points = [(x[i], y[i], z[i]) for i in range(n)]
    
    return points

def random_sphere(n, r, seed=None):
    """
    This function generates n random points on the surface of a sphere of radius r.

    :param n: number of points to generate.
    :param r: sphere radius.
    :param seed: seed for the random number generator.
    """
    if seed is not None:
        np.random.seed(seed)

    # Generate n random points in spherical coordinates
    theta = np.random.uniform(0, 2 * np.pi, size=n)
    phi = np.random.uniform(0, np.pi, size=n)

    # Convert spherical coordinates to cartesian coordinates
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)

    # Combine x,y,z coordinates into list of tuples
    random_points = [(x[i], y[i], z[i]) for i in range(n)]

    return random_points

def uv_map():
    """Projects a model's surface to a 2D image to enable texture mapping of imported stls.
    """
    context = bpy.context
    scene = context.scene
    vl = context.view_layer

    # deselect all to make sure select one at a time
    bpy.ops.object.select_all(action='DESELECT')

    # loop through al meshes in scene
    for obj in scene.objects:
        if (obj.type == 'MESH'):
            vl.objects.active = obj
            obj.select_set(True)

            # create a new UV layer called "LightMap" if it doesn't already exist
            lm =  obj.data.uv_layers.get("LightMap")
            if not lm:
                lm = obj.data.uv_layers.new(name="LightMap")
            lm.active = True

             # set the new UV layer as active, toggle to edit mode, select all faces, and perform the UV mapping
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT') # for all faces
            bpy.ops.uv.smart_project(angle_limit=66, island_margin = 0.03)
            bpy.ops.object.editmode_toggle()
            obj.select_set(False)
            
def make_rgb_image_name(id: int, extension: str = ".png") -> str:
    """Creates a RGB image name given an integer id.
    Args:
        id (int): Integer id used in name creation.
        extension (str, optional): Extension for image. Defaults to '.png'.
    Returns:
        str: Image name.
    """
    return "rgb_image_%03d" % id + extension

def make_iseg_image_name(id: int, extension: str = ".png") -> str:
    """Creates a RGB image name given an integer id.
    Args:
        id (int): Integer id used in name creation.
        extension (str, optional): Extension for image. Defaults to '.png'.
    Returns:
        str: Image name.
    """
    return "iseg_image_%03d" % id + extension

def create_light(R, G, B, intensity):
    """Create a new point light object.
    Args:
        R (int): Intensity Red
        G (int): Intensity Green
        B (int): Intensity Blue
        intensity (int): Power of light in Watts.
    Returns:
        obj: light
    """
    light_data = bpy.data.lights.new(name="PointLight", type='POINT')
    light = bpy.data.objects.new(name="PointLight", object_data=light_data)

    color = (R, G, B)

    # Set light color and intensity
    light_data.color = color
    light_data.energy = intensity

    # Add the light to the scene
    bpy.context.collection.objects.link(light)

    # Set the light's location
    light.location = (0, 0, 2)

    return light

def create_random_light(intensity_min, intensity_max, color):
    """Create a new point light object.
    Args:
        intensity_min (int): Minimum light intensity value in Watts.
        intensity_max (int): Maximum light intensity value in Watts.
    Returns:
        obj: light
    """

    light_data = bpy.data.lights.new(name="PointLight", type='POINT')
    light = bpy.data.objects.new(name="PointLight", object_data=light_data)

    intensity = random.randint(intensity_min, intensity_max)

    # Set light color and intensity
    light_data.color = color
    light_data.energy = intensity

    # Add the light to the scene
    bpy.context.collection.objects.link(light)

    # Set the light's location
    light.location = (1, 1, 1)

    return light


def generate_position_vector(r_min, r_max, seed=None):
    """
    Generates a random position vector within a sphere of radius between r_min and r_max.

    :param r_min: minimum radius of the sphere.
    :param r_max: maximum radius of the sphere.
    :return: a 3D vector representing the position.
    """
    if seed is not None:
        random.seed(seed)

    # generate random spherical coordinates
    radius = random.uniform(r_min, r_max)
    theta = random.uniform(0, 2*math.pi)
    phi = random.uniform(0, math.pi)

    # convert to cartesian coordinates
    x = radius * math.sin(phi) * math.cos(theta)
    y = radius * math.sin(phi) * math.sin(theta)
    z = radius * math.cos(phi)

    return Vector((x, y, z))


def create_distractors(r_min, r_max, n_min, n_max, seed=None):
    """
    Creates random distractors within a sphere of minimum radius r_min and maximum radius r_max.

    :param r_min: minimum radius of the sphere.
    :param r_max: maximum radius of the sphere.
    :param n_min: minimum number of distractors to create.
    :param n_max: maximum number of distractors to create.
    """

    if seed is not None:
        random.seed(seed)

    # create dictionary of shape names to function names
    shape_functions = {
        'cube': bpy.ops.mesh.primitive_cube_add,
        'cylinder': bpy.ops.mesh.primitive_cylinder_add,
        'cone': bpy.ops.mesh.primitive_cone_add,
        'torus': bpy.ops.mesh.primitive_torus_add
    }

    # generate random number of distractors
    num_distractors = random.randint(n_min, n_max)

    # create distractor objects
    for i in range(num_distractors):
        # choose random shape and position
        shape = random.choice(list(shape_functions.keys()))
        position = generate_position_vector(r_min, r_max)
        orientation = Vector([random.uniform(0, 2 * math.pi) for i in range(3)])

        # create object and set its location and orientation
        shape_functions[shape](location=position)
        obj = bpy.context.object
        obj.rotation_euler = orientation

def scale_distractors(min_scale_factor, max_scale_factor):
    """
    Scales down all the distractors in the scene by a random factor between the given minimum and maximum scale factors.

    :param min_scale_factor: the minimum scale factor to apply.
    :param max_scale_factor: the maximum scale factor to apply.
    """
    # get a reference to the current scene
    scene = bpy.context.scene

    # iterate over all objects in the scene
    for obj in scene.objects:
        # check if the object is a distractor (i.e., has a shape name in the shape_functions dictionary)
        if obj.name.startswith('Cube') or obj.name.startswith('Cylinder') or obj.name.startswith('Cone') or obj.name.startswith('Torus'):
            # generate a random scale factor between min_scale_factor and max_scale_factor
            scale_factor = random.uniform(min_scale_factor, max_scale_factor)

            # scale down the object by the random factor
            obj.scale *= scale_factor

def remove_distractors():
    """
    Removes all distractors in the scene.
    """
    # select all objects with names starting with "Cube", "Cylinder", "Cone", or "Torus"
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name.startswith('Cube') or obj.name.startswith('Cylinder') \
                or obj.name.startswith('Cone') or obj.name.startswith('Torus'):
            obj.select_set(True)
    # delete selected objects
    bpy.ops.object.delete()


def remove_lights():
    """
    Removes all point lights in the scene.
    """
    # select all objects starting with "PointLight"
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name.startswith('PointLight'):
            obj.select_set(True)
    # delete selected objects
    bpy.ops.object.delete()
