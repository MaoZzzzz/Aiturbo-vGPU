from scipy.optimize import nnls
import numpy as np
import math

from scipy.optimize import leastsq

def cpu_efficiency_ps(a, b, d, x) -> float:
    cpu_eff = float(a) * math.exp(float(b) * float(x) * -1) + float(d)
    return cpu_eff


vgg11_cpu_ps = [-7.74, 2.3719, 8.795]
vgg16_cpu_ps = [-7.03, 3.6715, 5.598]
vgg19_cpu_ps = [-6.68, 4.2738, 5.652]
lenet_cpu_ps = [-11.94, 3.7612, 7.619]
googlenet_cpu_ps = [-0.89, 1.4462, 1.909]
overfeat_cpu_ps = [-3.65, 3.742, 5.213]
alexnet_cpu_ps = [-14.38, 1.639, 15.734]
trivial_cpu_ps = [-19.65, 2.291, 21.532]
inception3_cpu_ps = [-1.837, 1.477, 2.813]
inception4_cpu_ps = [-4.806, 2.853, 5.236]
resnet50_cpu_ps = [-1.975, 1.884, 2.799]
resnet101_cpu_ps = [-2.433, 2.349, 3.395]
resnet152_cpu_ps = [-3.975, 2.784, 4.817]
mobilenet_cpu_ps = [2.723, 2.212, 3.671]

a = cpu_efficiency_ps(
    vgg11_cpu_ps[0], vgg11_cpu_ps[1], vgg11_cpu_ps[2], 5)
vgg11 = [[128, 1, 1, a, 1, 1, 1], [
    128, 1, 1, a, 1, 1, 2], [128/2, 1, 2, a*2, 2, 1, 2], [128/3, 1, 3, a*3, 3, 1, 3], [128, 1, 0.5, a*0.5, 1, 2, 1], [128, 1, 0.5, a*0.5, 1, 2, 2], [128/2, 1, 1, a*1, 2, 2, 2]]
vgg11_speed = [2042.30529040333, 1972.033736476333, 1011.7693367447351, 967.2233634009108, 1788.542569405014, 1794.412762996497, 903.7540698019911]
vgg16 = []
vgg19 = []
lenet = []
googlenet = []
overfeat = []
a = cpu_efficiency_ps(
    alexnet_cpu_ps[0], alexnet_cpu_ps[1], alexnet_cpu_ps[2], 5)
alexnet = [[1024, 1, 1, a, 1, 1, 1], [
    1024, 1, 1, a, 1, 1, 2], [1024/2, 1, 2, a*2, 2, 1, 2], [1024/3, 1, 3, a*3, 3, 1, 3], [1024, 1, 0.5, a*0.5, 1, 2, 1], [1024, 1, 0.5, a*0.5, 1, 2, 2], [1024/2, 1, 1, a*1, 2, 2, 2]]
trivial = []
inception3 = []
inception4 = []
resnet50 = []
resnet101 = []
resnet152 = []
nasnet = []
mobilenet = []

print(alexnet)
A = np.array(vgg11)
b = np.array(vgg11_speed)
print(nnls(A, b, 100000000))
# def error(p,x,y):
#     return p[0]*x**2+p[1]*x+p[2]-y 
# p0 = [5,2,10]
# ret = leastsq(error, p0, args = (A, b))
# print(ret) 
