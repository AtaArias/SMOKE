# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 15:35:20 2025

@author: lauta
"""

import pyvisa
import pandas as pd
import numpy as np
import os
import time
from lakeshore import Model425
    
class GPD3303S:
    """Class to control the GW Instek GPD-3303S power supply"""

    def __init__(self, resource_name):
        self.instrument = rm.open_resource(resource_name)
        self.instrument.read_termination = '\n'
        self.instrument.write_termination = '\n'

    def set_voltage(self, channel, voltage):
        """Set the voltage for a specific channel"""
        self.instrument.write(f"VSET1:{voltage:.2f}")

    def get_voltage(self, channel):
        """Read the set voltage for a specific channel"""
        return float(self.instrument.query(f"VOUT{channel}?").rstrip("V\r\n"))

    def set_output(self, state):
        """Enable or disable output for a specific channel"""
        state_value = "1" if state else "0"
        self.instrument.write(f"OUT{state_value}")

    def set_current(self, current):
        """Setea la corriente de salida"""
        self.instrument.write(f"ISET1:{current:.2f}")

    def enable_output(self, state=True):
        """Activa o desactiva la salida de la fuente"""
        self.instrument.write(f"OUT {'1' if state else '0'}")
        
    def close(self):
        """Close the instrument connection"""
        self.instrument.close()


class Rigol:
    
    def __init__(self, adress):
        self.instrument = rm.open_resource(adress)
        self.instrument.read_termination = '\n'
        self.instrument.write_termination = '\n'
        self.instrument.write("VOLT:DC:RANGE AUTO")
        
    def read_voltage(self):
        return float(self.instrument.query("MEAS:VOLT:DC?"))

    def close(self):
        self.instrument.close()
        
rm = pyvisa.ResourceManager()
print(rm.list_resources())
input('Pausa')

rigol = Rigol('USB0::0x1AB1::0x0C94::DM3O163050343::INSTR')
fuente = GPD3303S('ASRL4::INSTR')
gausim = Model425()

carpeta_salida = "./"
os.makedirs(carpeta_salida, exist_ok=True)

calibracion_numero = 0
calibracion_numero = input("Inserte el número de calibración: ")
archivo_salida = os.path.join(carpeta_salida, "calibracion.dat")

fuente.set_voltage(1, 32)  # Setea 32V
fuente.set_output(1) 

corrientes_subida = np.linspace(0, 0.52, 50)  # 50 pasos de 0A a 0.52A
corrientes_bajada = np.linspace(0.52, 0, 50)  # 50 pasos de 0.52A a 0A
corrientes_total = np.concatenate((corrientes_subida, corrientes_bajada))  # Juntar subida y bajada

datos = []

#corriente de 1mA en punta hall

## Loop de mediciones
time.sleep(2)
try:
    for i, corriente in enumerate(corrientes_total):
        fuente.set_current(corriente)
        time.sleep(2)
        
        voltaje_rigol = rigol.read_voltage()
        campo_gaussimetro = gausim.query('RDGFIELD?')
        
        datos.append([corriente, voltaje_rigol, campo_gaussimetro])
       # print(f'Paso {i+1}/100 -> I = {corriente:.3f} A | V = {voltaje_rigol:.3f} V | B = {campo_gaussimetro:.3f} G')
except ValueError:
    print(ValueError)
    gausim.disconnect_usb()
    
## Creo el archivo
df = pd.DataFrame(datos, columns=["Corriente (A)", "Voltaje_Rigol (V)", "Campo_Gaussimetro (G)"])
df.to_csv(archivo_salida, sep='\t', index=False)


## Apago todo
rigol.close()
fuente.enable_output(False)  # Apaga la salida de la fuente
fuente.close()
gausim.disconnect_usb()