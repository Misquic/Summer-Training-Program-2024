import sys
sys.path.append('./') # to use current directory modules
import numpy as np
import pandas as pd
import time
import os
import matplotlib.pyplot as plt
from func import *

import Client1 as Client
import Supply1
import RedLab1 as RL
#from Client1 import measure_and_save, measure_and_concat, measure, get_pixels, save_data_big
# from Supply1 import get_plasma_ready, supply_setup
# from Oscilator import scope_setup, get_waveform

########################################################################################
time1 = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime(time.time()))
dir = "./Data/" 
if(not os.path.exists(dir)):
    os.mkdir(dir)
dir = dir + str(time1) #directory in which data will be saved

Client.set_IntTime(500_000)
supply = setup()
del_bckg = True
voltages_given = np.arange(0,21,1)
voltages_gotten = np.zeros(voltages_given.size)
redlab_time = 2 # sec

measurement_n = len(voltages_given)

background = measure_background(supply)

bad_pixels = find_peaks(background)
background = del_bad_pixels(bad_pixels, background)
try:
    for measurement_i in range(measurement_n):
        supply.set_voltage(voltages_given[measurement_i])
        supply.read()
        time.sleep(3)


        for i in range(10): # 10 measuremendts of spectrum to average its
            if(i == 0):
                data_spectr = Client.measure()
                # data_red = RL.measure(rate = 50_000, chan = 0, buffer_size_seconds = redlab_time)
                # data_red_len = len(data_red)
            else:
                data_spectr = Client.measure_and_concat(data_spectr)
                # data_red = RL.measure_and_concat(data_red, rate = 50_000, chan = 0,  buffer_size_seconds = redlab_time)
        
        data_mean = data_spectr.mean(axis = 1)
        data_mean = np.reshape(data_mean, (data_mean.size, 1))
        data_mean = del_bad_pixels(bad_pixels, data_mean)
        if(del_bckg == True):
            data_mean = data_mean - background
        if(measurement_i == 0):
            data_save = data_mean
        else:
            data_save = np.concat([data_save, data_mean], axis = 1)



        print(("{:.3f}%" + " of all measurements done\n").format((measurement_i+1)/measurement_n*100))
        #print(data_save)  
        #print(data_save.shape)
finally:
    supply.set_voltage(0)  

#print("data_spectr.shape: ", data_spectr.shape)
print("Saving data")
save_data_big(data_save, dir, data_len = Client.get_pixels(), name = "spectr_all", cols=voltages_given, cols_bool= True)    
try:
    save_data_big(background, dir, data_len = Client.get_pixels(), name = "background", cols= np.array(["bckg"]), cols_bool= True)    
finally:
    print("Done")

bad_pixels = pd.DataFrame(bad_pixels[0])
bad_pixels.to_csv(dir + "/" + "zbad_pixels" + ".csv", index=False, header = None)

# save_data_big(data_red, dir, data_len = data_red_len, name = "red_all", cols=voltages_given)
# save_data_big(data_spectr, dir, data_len = Client.get_pixels(), name = "spectr_10_all", cols=voltages_given)    
# save_data_big(data_red, dir, data_len = data_red_len, name = "red_all", cols=voltages_given)
print("Done")
