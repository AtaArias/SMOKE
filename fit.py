import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.interpolate import UnivariateSpline
from scipy.optimize import curve_fit



def normalize(data):
    range = np.ptp(data['Vdiodo'])
    data['Vdiodo'] = (((data['Vdiodo'] - np.min(data['Vdiodo'])) / range) * 2) - 1

def cubic_spline_opt(x_data, y_data):
    def func(x, s):
        spline = UnivariateSpline(x_data, y_data, s=s)  # s=suavizado: más alto = más liso, s=0 interpola exactamente
        return spline(x)
    return func
        
def smooth(y, box_pts):
    padded_data = np.pad(y, (box_pts//2, box_pts//2), mode='reflect')
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(padded_data, box, mode='valid')
    return y_smooth

def lineal(x, a, b):
    return x * a + b

def spline_length(grupo):
    if grupo == '15nm':
        return 0.1
    if grupo == '24nm':
        return 0.2
    if grupo == '55nm':
        return 0.2
    if grupo == '158nm':
        return 0.4

    return 0.1

dir = "datos/muestras/"
dirs = os.listdir(dir)

for d in dirs:
    print(d)
    files = os.listdir(dir + d)
    dist = np.empty(0)
    for file in files:

        # Salteate las carpetas
        if not file.__contains__('.dat'):
            continue
        data = pd.read_csv(dir + d + '/' + file, sep = '\t')
        data['B'] = data['B'] - data['B'].iloc[0]
        data['t'] = data['t'] - data['t'].iloc[0]

        normalize(data)

        dif_i = np.diff(data['I_fuente'])
        signo_dif_i = np.sign(dif_i)

        # Detectar cambios de signo (esquinas del lazo de histéresis)
        cambios = np.where(signo_dif_i[1:] != signo_dif_i[:-1])[0] + 1

        # Cortar el DataFrame en segmentos
        segmentos = np.split(data.to_numpy(), cambios)
        segmentos = [pd.DataFrame(d, columns=data.columns) for d in segmentos]

        plt.grid()
        plt.scatter(data['B'], data['Vdiodo'], label = 'Usando Vhall', marker = 'o', fc = 'none', edgecolors='gray')

        raices = np.empty(0)

        for subdata in segmentos[-3:]:
            if len(subdata) < 10:
                continue
            # subdata['absI'] = np.abs(subdata['I_fuente'])
            subdata = subdata.sort_values(by = 'B')
            # diff = np.abs(np.diff(subdata['Vdiodo']))
            # indx = np.argmax(diff, axis = 0)
            # subdata = subdata[indx -3: indx + 3]
            x = subdata['B']
            y = subdata['Vdiodo']
            y = smooth(y, 3)

            # No funciona muy bien
            # popt, pcov = curve_fit(lineal, x, y)
            # corte = - popt[1] / popt[0]
            # raices = np.append(raices, corte)
            # ax + b = 0 => x = -b/a

            # func = cubic_spline_opt(x, y)
            # popt, pcov = curve_fit(func, x, y, p0=[1], bounds = (0.05, 2))
            # print(popt)
            # print(pcov)
            # Elergir s por grupo
            spline = UnivariateSpline(x, y, s=spline_length(d))  # s=suavizado: más alto = más liso, s=0 interpola exactamentes
            if len(spline.roots()) > 0:
                raices = np.append(raices, np.max(spline.roots()))

            x_fino = np.linspace(x.min(), x.max(), 200)
            y_fino = spline(x_fino)

            plt.plot(x_fino, y_fino, label='Corte histéresis')

        if len(raices) == 2:
            plt.scatter(raices, np.zeros(len(raices)))
            dist = np.append(dist, (raices[1] - raices[0]) / 2)
        plt.title(file)
        plt.legend()
        plt.savefig(dir + d + '/figures/' + file.split('.')[0] + '.png')
        plt.close()
        # plt.show()
    print(np.mean(dist))
    print(np.std(dist) / np.sqrt(len(dist)))
    print()