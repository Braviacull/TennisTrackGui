import os

def add_string_to_basename(path, string):
        # esempio: path = "C:/video.mp4", string = "_processed"
        # output = "C:/video_processed.mp4"
        base_name = os.path.basename(path)
        base_name, extension = os.path.splitext(base_name)
        res_name = base_name + string + extension
        res_dir = os.path.dirname(path)
        return os.path.join(res_dir, res_name)

path = "C:/video.mp4"
string = "_processed"
print(add_string_to_basename(path, string))
# expected output: C:/video_processed.mp4