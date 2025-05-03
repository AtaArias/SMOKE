import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

dir = './datos/'
files = os.listdir(dir)

def lineal(x, a, b):
    return x * a + b

x = np.empty(0)
y = np.empty(0)

for file in files:
    datos = pd.read_csv(dir + file, sep = '\t')

    #Corriente y tension a 3 decimales
    datos['Corriente (A)'] = np.round(datos['Corriente (A)'], 3)

    if "negat" in file:
        datos['Corriente (A)'] = -datos['Corriente (A)']

    # plt.scatter(datos['Corriente (A)'], datos['Campo_Gaussimetro (mT)'])
    x = np.append(x, datos['Campo_Gaussimetro (T)'])
    y = np.append(y, datos['Corriente (A)'])
    plt.plot(datos['Campo_Gaussimetro (T)'], datos['Corriente (A)'], marker = '.', label = file)
    plt.xlabel('Campo [T]')
    plt.ylabel('Corriente [A]')

args, cov = curve_fit(lineal, x, y)
err = np.sqrt(np.diag(cov))
print(args)
print(err)
# a 1mA de corriente
# V_hall en V
# B en T
# B(V_hall) = (4.3355 +- 0.0005) * V_hall + (0.093851 +- 0.000009) T
# pendiente = 4.33554273 +- 4.26148165e-04
# ord = 0.09385182 +- 8.99724520e-06

# CorrienteVsCampoObj
# pendiente = 3.48 T/A
# coord = 0.0006

plt.plot(x, lineal(x, *args), label = 'aju lineal', color = 'red', linestyle = '--')
plt.legend()
plt.show()