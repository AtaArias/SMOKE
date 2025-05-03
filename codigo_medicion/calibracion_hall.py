import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

dir = './datos/'
files = os.listdir(dir)

def lineal(x, a, b):
    return x * a + b

pendientes = np.empty(0)
err_pendientes = np.empty(0)
coord_origenes = np.empty(0)
err_coord_origenes = np.empty(0)

for file in files:
    datos = pd.read_csv(dir + file, sep = '\t')

    #Corriente y tension a 3 decimales
    datos['Corriente (A)'] = np.round(datos['Corriente (A)'], 3)

    if "negat" in file:
        datos['Corriente (A)'] = -datos['Corriente (A)']

    # plt.scatter(datos['Corriente (A)'], datos['Campo_Gaussimetro (mT)'])
    x = datos['Voltaje_Rigol (V)']
    y = datos['Campo_Gaussimetro (T)']

    aju, cov = curve_fit(lineal, x, y)
    err = np.sqrt(np.diag(cov))
    
    a = aju[0]
    erra = err[0]

    b = aju[1]
    errb = err[1]

    pendientes = np.append(pendientes, a)
    err_pendientes = np.append(err_pendientes, erra)

    coord_origenes = np.append(coord_origenes, b)
    err_coord_origenes = np.append(err_coord_origenes, errb)

    plt.scatter(datos['Voltaje_Rigol (V)'], datos['Campo_Gaussimetro (T)'], marker = '.', label = file)
    # plt.xlabel('Campo [T]')
    # plt.ylabel('Corriente [A]')
    plt.show()

# promedio y desviación estandard
pen = np.average(pendientes)
err_pen = np.std(pendientes)

coord = np.average(coord_origenes)
err_coord = np.std(coord_origenes)

print(pen, err_pen)
print(coord, err_coord)