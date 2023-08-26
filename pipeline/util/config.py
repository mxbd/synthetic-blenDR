import json
import os

class Config():
    def __init__(self,config_path):

        # Check if the config file exists
        if not os.path.exists(config_path):
            raise FileNotFoundError(f'{config_path} not found')

        # Open the config file and load it as a JSON object
        with open(config_path, 'r') as file:
            json_config = json.load(file)

        # Load data from the config file
        self.input_dir = json_config['input_dir']
        self.output_dir = json_config['output_dir']
        self.textures_dir = json_config['textures_dir']
        self.backgrounds_dir = json_config['backgrounds_dir']
        self.components = json_config['components']

        render_settings=json_config['render_settings']
        self.n_images= render_settings['n_images']
        self.r_camera= render_settings['r_camera']
        self.r_light= render_settings['r_light']
        self.intensity_min_light = render_settings['intensity_min_light']
        self.intensity_max_light = render_settings['intensity_max_light']
        self.light_properties_random = render_settings['light_properties_random']
        self.light_position_random = render_settings['light_position_random']
        self.n_distractors_min = render_settings["n_distractors_min"]
        self.n_distractors_max = render_settings["n_distractors_max"]
        self.r_distractors_min = render_settings["r_distractors_min"]
        self.r_distractors_max = render_settings["r_distractors_max"]
        self.scale_distractors_min = render_settings["scale_distractors_min"]
        self.scale_distractors_max = render_settings["scale_distractors_max"]
        self.add_distractors = render_settings["add_distractors"]
        self.random_seed = render_settings["random_seed"]
        