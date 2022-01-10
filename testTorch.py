import torch
x = torch.rand(5, 3)
print(x)
print("torch.cuda.is_available=" +str(torch.cuda.is_available()))
