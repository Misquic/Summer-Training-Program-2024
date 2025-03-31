from voltcraft.pps import PPS
import time

def set_plasma_ready(supply): #TO DO
    print("TO DO!! get plasma ready")
    print("voltage: " + str(supply.reading()[0]) + " current: " + str(supply.reading()[1]))

class supply:
    def __init__(self, port = "COM5", reset=False):
        self.supp = PPS(port=port, reset = reset)
        
    def set_voltage(self, voltage):
        self.supp.voltage(voltage)

    def set_current(self, current):
        self.supp.current(current)

    def read(self):
        time.sleep(1)
        print("voltage: " + str(self.supp.reading()[0]) + " current: " + str(self.supp.reading()[1]))
    


# in Windows change string to COMx (eg COM4)

# for i in range(0, 24, 1):
#     supply.voltage(i)
#     time.sleep(1)
#     print("voltage: " + str(supply.reading()[0]) + " current: " + str(supply.reading()[1]))

# supply.voltage(24.0)
#supply.output(1)