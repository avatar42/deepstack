import torch
x = torch.rand(5, 3)
print(x)
print("torch.version=" + str(torch.version.__version__))

print("torch.cuda_version=" + str(torch.cuda_version))
print("torch.cuda.is_available=" + str(torch.cuda.is_available()))
print("torch.cuda.get_device_name()=" + str(torch.cuda.get_device_name()))
print("torch.cuda.get_device_properties(0)=" + str(torch.cuda.get_device_properties(0)))
print("torch.cuda.is_available()=" + str(torch.cuda.is_available()))
print("torch.cuda.is_initialized()=" + str(torch.cuda.is_initialized()))
print("torch.cuda._check_capability (warn)=" + str(torch.cuda._check_capability()))
