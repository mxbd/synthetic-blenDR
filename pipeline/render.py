import os
import sys
import subprocess
import argparse

from util import helpers
from util import config as conf

# set root dir and ensure modules/packages can be imported by script
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(ROOT_DIR)

# set up default values for cwd, blender.exe, blenderscript.py, config.json
CWD_PATH = os.getcwd()
BP_DEFAULT = r'C:/Program Files/Blender Foundation/Blender 2.92/blender.exe'
S_DEFAULT = os.path.join(ROOT_DIR, 'blenderscript.py')
CONFIG_PATH = os.path.join(ROOT_DIR,'config.json')

# Load config file
config = conf.Config(CONFIG_PATH)

def main(blender_path, python_script, cwd=ROOT_DIR):
    """Main function that runs the Blender process using the provided blender path, script path and working directory.

    Args:
        blender_path (str): Path to the blender.exe file.
        python_script (str): Path to the python script that will be used in blender.
        cwd (str, optional): The current working directory, default is ROOT_DIR.

    Returns:
        None
    """

    # Set the directory 
    dir_path = cwd

    # Set blender file path and check if exists
    blender_file = os.path.join(dir_path,'renderfile.blend')
    if not os.path.exists(blender_file):
        raise Exception('Blender file not found: {}'.format(blender_file))
    
    # Set the path to the python script and check if exists
    script_path = os.path.join(dir_path, python_script)
    if not os.path.exists(script_path):
        raise Exception('Python script not found: {}'.format(script_path))

    # Define the arguments to be passed to blender.exe and run
    args = [blender_path, '-b', blender_file, '--python', script_path]
    subprocess.run(args)

    
# Set up the argument parser for the script cmd line args
parser = argparse.ArgumentParser(description='Render Modeldata via Blender')
parser.add_argument('-bp', '--blender-path', help='path for blender.exe', default=BP_DEFAULT, required=False)
parser.add_argument('-s', '--python-script', help='path for py script to be used in blender', default=S_DEFAULT, required=False)
parser.add_argument('-wd', '--working-dir', help='working dir if not cwd', default=ROOT_DIR)

args = parser.parse_args()

# Check if the script is being run as the main module
if __name__ == '__main__':

    # generate synthetic dataset
    main(args.blender_path, args.python_script, args.working_dir)

    # move rgb and iseg images to folders
    helpers.move_images_to_folder(config.output_dir)
    
    # define labels and iseg path
    labels_path = os.path.join(config.output_dir, 'labels')    
    iseg_path = os.path.join(config.output_dir, 'iseg')

    # Create the 'labels' folder
    os.makedirs(labels_path)

    # Extract bbox annots from iseg images
    helpers.extract_bbox_annots(iseg_path, labels_path)