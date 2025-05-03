import pyvisa

class Rigol: #RIGOL DM3058  https://www.batronix.com/pdf/Rigol/ProgrammingGuide/DM3058_ProgrammingGuide_EN.pdf
    def __init__(self,adress,scale = -1):  #es un constructor que inicializa con las direcciones de los inst
    
        self.inst = rm.open_resource(adress) #abre la conexion
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'
        #le dice que lea voltaje
        self.inst.write('FUNC:VOLT:DC') #The command FUNC:VOLT:DC enables the DC voltage measurement
        if scale > -1:
            self.inst.write('MEAS MANU')
            self.inst.write('MEAS:VOLT:DC %f'%scale) #The corresponding resultion will be set automatically after you set the range.
                                                     #The measurement type will change into ―Manual‖ automaticlly as you set the range.
                                                     #scale es el parameter range, si scale=2 entonces range=20V y resolution=10microV (ver más p53 del manual del multimetro)
        else: self.inst.write('MEAS AUTO')
        self.inst.write(':RATE:VOLT:DC M') #Sets the desired measuring rate of DC voltage. M(Medium) corresponde a 20Hz, 20readings/s o 1reading cada 0.05s (ver mas p71 del manual)
        self.inst.write(':TRIG:SOUR AUTO')

    def write(self,msg):  #metodo para enviar mensajes (msg) al inst
        self.inst.write(msg)

    def read(self):   #para leer del inst
        return (self.inst.read_ascii_values()[0])
            # leer volt 'MEAS:VOLT:DC?'
    
    def read_v(self):
        self.inst.write('MEAS:VOLT:DC?') #The command returns the measured DC voltage value in scientific notation, the unit is V. 
        return float(self.inst.read_ascii_values()[0])
    

class GPD3303S:
    """Class to control the GW Instek GPD-3303S power supply"""

    def __init__(self, resource_name):
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(resource_name)

    def set_voltage(self, channel, voltage):
        """Set the voltage for a specific channel"""
        self.instrument.write(f"VSET{channel}:{voltage:.2f}")

    def get_voltage(self, channel):
        """Read the set voltage for a specific channel"""
        return float(self.instrument.query(f"VOUT{channel}?").rstrip("V\r\n"))

    def set_output(self, state):
        """Enable or disable output for a specific channel"""
        state_value = "1" if state else "0"
        self.instrument.write(f"OUT{state_value}")

    def close(self):
        """Close the instrument connection"""
        self.instrument.close()

rm = pyvisa.ResourceManager()
print(rm.list_resources())