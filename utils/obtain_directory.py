import os
from costants import *

def obtain_input_dir(self):
    if not self.project_path:
        print("No project loaded")
        return
    return os.path.join(self.project_path, "input")

def obtain_output_dir(self):
    if not self.project_path:
        print("No project loaded")
        return
    return os.path.join(self.project_path, "output")

def obtain_project_dir(self):
    if not self.project_path:
        print("Error: No project loaded")
        return
    return self.project_path

def obtain_jsons_dir(path_output_video):
    # Obtain the project directory
    project_dir = os.path.dirname(os.path.dirname(path_output_video))
    
    # Build the jsons directory
    jsons_dir = os.path.join(project_dir, 'jsons')
    
    return jsons_dir
    

def obtain_base_name(self):
    processed_path = os.path.join(obtain_output_dir(self), PROCESSED)
    pre_processed_path = os.path.join(obtain_output_dir(self), PRE_PROCESSED)
    if os.path.isfile(processed_path):
        return PROCESSED
    elif os.path.isfile(pre_processed_path):
        return PRE_PROCESSED
    else:
        print("Error: No base name found")
        return None