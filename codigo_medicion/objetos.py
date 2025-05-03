import pyvisa
import numpy as np
import os
from lakeshore import Model425
import serial
    
rm = pyvisa.ResourceManager()

## Página 140 del manual https://www.ameteksi.jp/-/media/ameteksi/download_links/documentations/supportcenter/signalrecovery/instruction_manuals/190284-a-mnl-c.pdf?dmc=1
class Lockin:
    def __init__(self, resource_name = '/dev/ttyUSB0'):
        self.instrument = serial.Serial(resource_name)
        self.instrument.write(f'IE 1') ## Referencia externa TTL
        self.instrument.write('TC 11') ## Contante de tiempo 100 ms
        self.instrument.write_termination = '\r\n'
        self.instrument.read_termination = '\r\n'
        self.instrument.write('DD 59') # separador de lectura entre dos magnitudes ';'
        self.instrument.write('IE 1') # referencia externa TTL, rear panel
        self.instrument.write('IMODE 0') # desactivo modo corriente y selecciono entrada A
        self.instrument.write('VMODE 1') # desactivo modo corriente y selecciono entrada A
        self.instrument.write('FET 1') # amp bipolar
        self.instrument.write('FLOAT 1') # conector flotado a tierra con resistencia de 1k
        self.instrument.write('LF 1 1') # filtro notch a 50 Hz
    def set_reference(self, tipo):
        n = 0 # default interno
        if tipo == 'TTL':
            n = 1
        if tipo == 'external':
            n = 2
        self.instrument.write(f'IE {n}')
    def set_time_constant(self, n):
        self.instrument.write(f'TC {n}')
    def set_input_mode(self, n):
        self.instrument.write(f'IMODE {n}')
    def set_sens(self, n):
        self.instrument.write(f' SEN {n}')
    def get_x(self):
        return float(self.instrument.query('X.'))
    def get_y(self):
        return float(self.instrument.query('Y.'))
    def get_mag(self):
        return float(self.instrument.query('MAG.'))
    def get_phase(self):
        return float(self.instrument.query('PHA.'))
    def get_frec(self):
        return self.instrument.query('FRQ.')
    def read_MP(self):
        self.l.write('MP.')
        #sleep(0.01)
        M,P = self.l.read().split(';')
        if M == '0.0E+00\x00':
            M = 0
        if P == '0.0E+00\x00':
            P = 0
        return float(M),float(P)
    def auto_fase(self):
        self.l.write('AQN') # auto fase - maximiza X y minimiza Y
class GPD3303S:
    """Class to control the GW Instek GPD-3303S power supply"""
    def __init__(self, resource_name):
        self.instrument = rm.open_resource(resource_name)
        self.instrument.read_termination = '\n'
        self.instrument.write_termination = '\n'
    def set_voltage(self, channel, voltage):
        self.instrument.write(f"VSET1:{voltage:.2f}")
    def get_voltage(self, channel):
        return float(self.instrument.query(f"VOUT{channel}?").rstrip("V\r\n"))
    def set_output(self, state):
        state_value = "1" if state else "0"
        self.instrument.write(f"OUT{state_value}")
    def set_current(self, current):
        self.instrument.write(f"ISET1:{current:.2f}")
    def enable_output(self, state=True):
        self.instrument.write(f"OUT {'1' if state else '0'}")
    def close(self):
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

## Da la corriente necesaria para obtener el campo objetivo
def CorrienteObj(campo):
    pen = 3.49954244
    cord = -0.00422761
    return campo * pen

## Da el campo medido a partir de la tensión Hall
def CampoMag(Vhall, dHall):
    if not dHall:
        dHall = 0.001

    pen = 4.331286718960056
    err_pen = 0.006123006020318645
    cord = 0.09368764551836478
    err_coord = 0.00024506874726457143

    campo = pen * Vhall + cord
    err_campo = np.sqrt(
        (pen * dHall)**2 +
        (err_pen * Vhall)**2 +
        (err_coord)**2)
    # f = ax + b
    # df = sqrt{(a dx)**2 + (da * x)**2 + db**2}

    return (campo, err_campo)