import os
inst = os.open('/dev/usbtmc0', os.O_RDWR)
os.write(inst, b':MEAS:VOLT:DC?\n\r')
print(os.read(inst, 128))