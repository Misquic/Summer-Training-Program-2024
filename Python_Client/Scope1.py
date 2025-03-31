import pyvisa
import numpy as np
from struct import unpack
import matplotlib.pyplot as plt

def setup(): # initialise connection with scope
    rm = pyvisa.ResourceManager()
    rm.list_resources()
    inst = rm.open_resource('USB0::0x0699::0x0423::C010510::INSTR')
    return inst

def get_waveform(inst): # get waveform, returns time(x axis) and wave (values, y axis)
    inst.write('DATA:SOU CH4')

    ymult = float(inst.query('WFMPRE:YMULT?'))
    yzero = float(inst.query('WFMPRE:YZERO?'))
    yoff = float(inst.query('WFMPRE:YOFF?'))
    xincr = float(inst.query('WFMPRE:XINCR?'))

    print( ymult, yzero, yoff, xincr)

    inst.write('CURV?')
    data = inst.read_raw() # screenshot z urządzenia
    headerlen = 2+ int(data[1])
    header = data[:headerlen]
    wave = data[headerlen:-1]

    wave1 = np.array(unpack('%sb' % len(wave), wave)) #osmiobitowy ze znakiem -127 +127, współrzędne screenshotu

    volts = (wave1 - yoff) * ymult + yzero

    time = np.arange(0, xincr * len(volts), xincr)

    plt.plot(time, wave1, '.', ms = 0.8)
    plt.show()

    print(wave1)

    return (time, wave1)