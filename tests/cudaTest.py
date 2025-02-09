import torch
import torchvision

print(torch.cuda.is_available())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No CUDA device found")

print("")
print(torch.__version__, torch.cuda.is_available())
print(torchvision.__version__)
