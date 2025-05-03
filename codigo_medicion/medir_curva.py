from objetos import GPD3303S as Fuente
from objetos import Rigol as Multimetro
from objetos import Lockin as LIA
from objetos import rm
from objetos import CampoMag
from objetos import CorrienteObj
import os
from time import time, sleep
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import threading
from math import copysign

print(rm.list_resources())

## Crear virtual instruments
mult_Vhall = Multimetro('adress_multimetro')
lockin = LIA('adress_lockin')
fuente = Fuente('adress_fuente')

## Crear variables
nombre_medicion = 'medicion'
num_medicion = input('Inserte el número de la medición: ')
nombre_medicion += num_medicion
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title(nombre_medicion)
ax.set_xlabel('Campo Bobinas[T]')
ax.set_ylabel('Tension Diodo [V]')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-10, 10)
grafica, = ax.plot([], [])

## Crear data
data = pd.DataFrame(columns=['t', 'Vhall', 'err_Vhall', 'I_fuente', 'B', 'err_B', 'Vdiodo', 'err_Vdiodo', 'frec_TTL'])

## Funciones auxiliares
def leer_datos(t0, corriente):
    ## Leer datos y armar el row
    row = {
        't': time() - t0,
        'err_Vhall': 0.001, # mv
        'I_fuente': corriente # viene de lo último que se seteo
    }

    row['err_Vdiodo'] = 0
    row['frec_TTL'] = 600

    B, err_B = CampoMag(row['Vhall'], row['err_Vhall'])
    row['B'] = B
    row['err_B'] = err_B
    
    hilo_Vhall = threading.Thread(target=lambda: row.update({'Vhall':mult_Vhall.read_voltage()}))
    hilo_Vdido = threading.Thread(target=lambda: row.update({'Vdiodo':lockin.get_mag()}))

    hilo_Vhall.start()
    hilo_Vdido.start()

    hilo_Vhall.join()
    hilo_Vdido.join()

    B, err_B = CampoMag(row['Vhall'], 0.001)
    row['err_B'] = err_B
    data.loc[len(data)] = row

def guardar_datos():
    return data.to_csv(nombre_medicion + '.dat', sep = '\t') # guardar datos

def update_plot():
    grafica.set_xdata(data['B'])
    grafica.set_ydata(data['Vdiodo'])
    fig.canvas.draw()
    fig.canvas.flush_events()

## Setup previo
fuente.set_voltage(1, 32)  # Setea 32V
fuente.set_current(0) # Corriente en 0amp
fuente.set_output(1) # output activo
Iactual = 0
Bactual = 0

## mediciones
t_inicial = time()
minB = -1.5
maxB = 1.5
try:
    Binicial = float(input('Inserte el campo inicial[T]: '))
    if Binicial < minB or Binicial > maxB:
        print('El campo no se encuentra en el rango obtenible')
    Iactual = CorrienteObj(Binicial)
    if Iactual < 0:
        input("Está por colocar una corriente negativa, asegurese de que los cables están en la posición correcta")
    fuente.set_current(np.abs(Iactual))
    sleep(3)
    while True:
        Bnext = float(input('A qué campo[T] quiere llegar?: '))
        if Bnext < minB or Bnext > maxB:
            print('El campo no se encuentra en el rango obtenible')
            continue
        pasos = input('En cuantos pasos quiere llegar?: ')

        ## Campos por los que tengo que pasar
        campos = np.linspace(float(Bactual), float(Bnext), int(pasos))
        corrientes = CorrienteObj(campos)
        corrientes = np.round(corrientes, 3)
        
        for indice, I in enumerate(corrientes):
            if copysign(1, Iactual) != copysign(1, I): # Se va a realizar un paso por el 0, ponga la fuente en 0
                fuente.set_current(0) # baja la corriente
                fuente.set_output(0) # apaga la fuente
                respuesta = input(f'Va a realizar un cambio de valor de corriente, de {Iactual} a {I}, invierta los cables, presione enter para continuar: ')
                fuente.set_output(1)
                # lectura en 0
            fuente.set_current(np.abs(I))
            Iactual = I
            sleep(2)
            leer_datos(t_inicial, I)
            update_plot()
finally:
    guardar_datos()