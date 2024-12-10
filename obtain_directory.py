import os


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

def obtain_thumbnails_dir(self):
    if not self.project_path:
        print("No project loaded")
        return
    return os.path.join(self.project_path, "thumbnails")

def obtain_tmp_dir(self):
    if not self.project_path:
        print("No project loaded")
        return
    return os.path.join(self.project_path, "tmp")

def obtain_tmp_output_dir(self):
    if not self.project_path:
        print("No project loaded")
        return
    return os.path.join(obtain_tmp_dir(self), "output")

def obtain_tmp_thumbnails_dir(self):
    if not self.project_path:
        print("No project loaded")
        return
    return os.path.join(obtain_tmp_dir(self), "thumbnails")
