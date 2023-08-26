import bpy
import zpy
from pathlib import Path
from mathutils import Vector
import random
import os
import sys


# Set root dir and ensure modules/packages can be imported by script
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(ROOT_DIR)

# Import additional custom functions from util package
from util import blender_util
from util import config as conf

# Get current working directory and config path
CWD_PATH = os.getcwd()
CONFIG_PATH = os.path.join(ROOT_DIR,'config.json')

# Check if config file exists
if not os.path.exists(CONFIG_PATH):
    raise Exception('config.json not found')

# Load config file
config = conf.Config(CONFIG_PATH)

# Get input and output directories from config
input_dir = config.input_dir

# Get various params from config
n_images = config.n_images
r_camera = config.r_camera
r_light = config.r_light
intensity_min_light = config.intensity_min_light
intensity_max_light = config.intensity_max_light
light_properties_random = config.light_properties_random
light_position_random = config.light_position_random
n_distractors_min = config.n_distractors_min
n_distractors_max = config.n_distractors_max
r_distractors_min = config.r_distractors_min
r_distractors_max = config.r_distractors_max
scale_distractors_min = config.scale_distractors_min
scale_distractors_max = config.scale_distractors_max
add_distractors = config.add_distractors
random_seed = config.random_seed

# Import STL files from the input directory
blender_util.import_stl_folder(input_dir)

# Create a dictionary of all components
components = {}
for c in config.components:
    components[c['name']] = c['stl-filename'], c['R'], c['G'], c['B'], c['category'], c['sub-category']

# add stls to ignore / not needed if analyzing all parts of assembly!
ignore = ['QC - auslegerbuchse-1', 'QC - auslegerbuchse-2', 'QC - auslegerbuchse-3', 'QC - auslegerbuchse-4', 'QC - ESC-1', 'QC - ESC-2', 'QC - ESC-3', 'QC - ESC-4', 'QC - FC', 'QC - m3-buchse-1', 'QC - m3-buchse-2', 'QC - m3-buchse-3', 'QC - m3-buchse-4', 'QC - m3-buchse-unten-1', 'QC - m3-buchse-unten-2', 'QC - m3-buchse-unten-3', 'QC - m3-buchse-unten-4', 'QC - mutter-m3-1', 'QC - mutter-m3-2', 'QC - mutter-m3-3', 'QC - mutter-m3-4', 'QC - mutter-m4-1', 'QC - mutter-m4-2', 'QC - mutter-m4-3', 'QC - mutter-m4-4', 'QC - mutter-m6-1', 'QC - mutter-m6-2', 'QC - mutter-m6-3', 'QC - mutter-m6-4', 'QC - PDB', 'QC - schraube-m3x18-1', 'QC - schraube-m3x18-2', 'QC - schraube-m3x18-3', 'QC - schraube-m3x18-4', 'QC - schraube-m4x6-1', 'QC - schraube-m4x6-2', 'QC - schraube-m4x6-3', 'QC - schraube-m4x6-4', 'QC - schraube-m4x6-5', 'QC - schraube-m4x6-6', 'QC - schraube-m4x10-1', 'QC - schraube-m4x10-2', 'QC - schraube-m4x10-3', 'QC - schraube-m4x10-4', 'QC - schraube-m4x16-1', 'QC - schraube-m4x16-2', 'QC - schraube-m4x16-3', 'QC - schraube-m4x16-4', 'QC - spannungstester']

def run(num_steps: int = n_images):
    
    # remove distractors and lights if any in scene
    blender_util.remove_distractors()
    blender_util.remove_lights()

    # random seed 
    zpy.blender.set_seed(random_seed)
    
    # saver object to store all images, annotations etc.
    # detect and segmentation dataset so ImageSaver is used
    saver = zpy.saver_image.ImageSaver(description="DR dataset", output_dir=config.output_dir)
    
    # get handle to camera and light
    camera = bpy.data.objects['Camera']
    
    # Create dictionaries to store categories and subcategories
    category_dict = {}
    subcategory_dict = {}

    # Loop through dictionary to get handle to objects and their color values
    for obj_name, (stl_name, R, G, B, main_category, sub_category) in components.items():
        obj = bpy.data.objects[stl_name]
    
        # Add category if needed
        if main_category not in category_dict:
            category_dict[main_category] = len(category_dict)
            category_id = category_dict[main_category]
            subcategory_dict[category_id] = {}

        # Add subcategory if needed
        if sub_category and sub_category not in subcategory_dict[category_id]:
            subcategory_dict[category_id][sub_category] = len(subcategory_dict[category_id])
    
        # Segment object
        zpy.objects.segment(obj, name=obj_name, color=(R, G, B))
        
    # Create categories and subcategories
    for main_category, category_id in category_dict.items():
        subcategories = []
        for sub_category, subcategory_id in subcategory_dict[category_id].items():
            subcategories.append(sub_category)
        saver.add_category(name=main_category, subcategories=subcategories)

    # list of hdris for background
    background_files = os.listdir(config.backgrounds_dir)
    background_paths = []
    for file in background_files:
        background_paths.append(Path(config.backgrounds_dir) / file)
    
    # list of textures for obj mat
    texture_files = os.listdir(config.textures_dir)
    texture_paths = []
    for file in texture_files:
        texture_paths.append(Path(config.textures_dir) / file)

    fib_points = blender_util.fibonacci_sphere(n=num_steps, r=r_camera)
    random_points = blender_util.random_sphere(n=num_steps, r=r_light)

    # GENERATION LOOP
    for image_id in range(num_steps):

        # remove old distractors
        blender_util.remove_distractors()

        # create new set if required
        if add_distractors == 1:
            blender_util.create_distractors(r_distractors_min, r_distractors_max, n_distractors_min, n_distractors_max)
            blender_util.scale_distractors(scale_distractors_min, scale_distractors_max)

        light_color = random.choice([(0.9440666514472968, 0.5833314064014211, 0.8620217891113732), (0.10667940786362784, 0.6366501465055134, 0.8283463249515829), (0.3302847843832679, 0.6345777588778184, 0.1404223675732703), (0.7401648553552618, 0.8317902032242835, 0.10106199897902346), (0.45295583701408515, 0.5915025303641542, 0.6465851385385122), (0.7123306351550376, 0.5129631064977251, 0.21762394723865053), (0.09130264158123913, 0.5537163541914795, 0.16064870877864545), (0.6707118865158586, 0.18080553053619286, 0.6469992264673323), (0.43314508229358095, 0.9122424851506655, 0.11356637786000401), (0.7862445863417918, 0.4991837341778049, 0.8092578403062234), (0.51256704292842, 0.11446145740590452, 0.377651670065407), (0.6092571721767102, 0.9609982643235238, 0.3617614595169364), (0.41775889785188935, 0.5887628033917193, 0.3653242029611167), (0.08168563243279225, 0.20787113902796528, 0.853123892762489), (0.728912072767947, 0.007843865205733658, 0.44430589288037026), (0.4227426992503953, 0.4819567510637641, 0.9994331877106425), (0.43845994505785546, 0.3206641860930485, 0.18213702509162955), (0.14302450174817516, 0.34570045520043546, 0.09624042133049515), (0.06851751916568105, 0.9504095026623458, 0.4436218941396267), (0.44803137650648206, 0.9420336857811692, 0.7011742274582891), (0.9044282823872661, 0.06018959064986862, 0.6672269895484276), (0.17929559468586476, 0.05729827561742895, 0.49895105147336904), (0.7264269847796142, 0.1724740290693172, 0.5732874557940236), (0.23126506532015478, 0.4739532054786436, 0.7826173889280275), (0.9605147974634811, 0.22367623177522433, 0.05426495060923542), (0.9917333698192003, 0.42190722736389363, 0.6050487503476861), (0.05329161480666911, 0.12026604183618406, 0.5627467879416354), (0.7226263870851404, 0.2542508788398701, 0.8884488745881918), (0.6076647881760615, 0.08606657900248538, 0.8287388948003354), (0.5671128089332944, 0.9573173892199068, 0.4108142077323873)])

        # create light of random color and access through handle
        if light_properties_random == 1:
            blender_util.create_random_light(intensity_min_light, intensity_max_light, light_color)
        else:
            blender_util.create_light(0.5, 0.5, 0.5, 5000)


        light = bpy.data.objects['PointLight']
        
        x_cam = fib_points[image_id][0]
        y_cam = fib_points[image_id][1]
        z_cam = fib_points[image_id][2]
        
        x_light = random_points[image_id][0]
        y_light = random_points[image_id][1]
        z_light = random_points[image_id][2]
        
        if light_position_random == 1:
            # jitter Light
            light.location = (x_light, y_light, z_light)

        # jitter Camera
        camera.location = (x_cam,y_cam,z_cam)

        
        # make sure obj is always in view of cam
        zpy.camera.look_at(camera, bpy.data.objects[components[list(components.keys())[0]][0]].location)
        
        # randomize background using locally saved hdris
        zpy.hdris.load_hdri(random.choice(background_paths))
        
        # Add random texture to obj
        for obj_name, (stl_name, R, G, B, main_category, sub_category) in components.items():
            obj = bpy.data.objects[stl_name]
            texture = zpy.material.make_mat_from_texture(random.choice(texture_paths))
            zpy.material.set_mat(obj, texture)
            zpy.objects.segment(obj, name=obj_name, color=(R, G, B))
            zpy.material.jitter(obj.active_material)

        # Add random textures of objects to ignore in annots
        for obj in ignore:
            obj_ignore = bpy.data.objects[obj]
            texture_ignore = zpy.material.make_mat_from_texture(random.choice(texture_paths))
            zpy.material.set_mat(obj_ignore, texture_ignore)
            zpy.material.jitter(obj_ignore.active_material)

        # Add random texture to flying distractors
        for obj in bpy.data.objects:
            if obj.name.startswith('Cube') or obj.name.startswith('Cylinder') \
                or obj.name.startswith('Cone') or obj.name.startswith('Torus'):
                    texture = zpy.material.make_mat_from_texture(random.choice(texture_paths))
                    zpy.material.set_mat(obj, texture)
                    
        
        # name images -> based on image id
        rgb_image_name = blender_util.make_rgb_image_name(image_id)
        iseg_image_name = blender_util.make_iseg_image_name(image_id)

        # render image
        zpy.render.render_aov(
            rgb_path = saver.output_dir / rgb_image_name,
            iseg_path = saver.output_dir / iseg_image_name,
            width=640,
            height=640,
        ) 
            
        # add images to saver object (saver object --> json)
        saver.add_image(
            name = rgb_image_name,
            style='default',
            output_path=saver.output_dir / rgb_image_name,
            frame=image_id,
            width=640,
            height=640,
        )
        saver.add_image(
            name = iseg_image_name,
            style='segmentation',
            output_path=saver.output_dir / iseg_image_name,
            frame=image_id,
            width=640,
            height=640,
        )

        blender_util.remove_lights()

# Get all mesh objects and center them
mesh_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH']
       
blender_util.norm_and_center(mesh_objs)
blender_util.uv_map()

run()