import sys
sys.path.append('./') # to use current directory modules
import numpy as np
import pandas as pd
import time
import os
import matplotlib.pyplot as plt

import Client1 as Client
import Supply1
import RedLab1 as RL


def setup():
    supply = Supply1.supply()
    return (supply)

def measure_background(supply, i_max = 10):
    supply.set_voltage(0)
    for i in range(i_max): # 10 measuremendts of spectrum to average its
        if(i == 0):
            background = Client.measure()
            # data_red = RL.measure(rate = 50_000, chan = 0, buffer_size_seconds = redlab_time)
            # data_red_len = len(data_red)
        else:
            background = Client.measure_and_concat(background)

    background = background.mean(axis = 1)
    background = np.reshape(background, (background.size, 1))
    return background

def save_data_big(data_big, dir, data_len, name = "file", cols = None, cols_bool = False):
    measurement_n = int(data_big.size/data_len)
    # data_big = np.reshape(data_big, (measurement_n, data_len))
    # data_big = np.transpose(data_big)

    if(cols is None):
        cols = np.linspace(1, measurement_n, measurement_n) #TO DO
    if(cols.size < measurement_n):
        temp = np.zeros(measurement_n - cols.size)
        cols = np.concat([cols, temp])

    col_names = np.array(cols, dtype = str)

    data_pd = pd.DataFrame(data_big, columns = col_names[:measurement_n])
    if(not os.path.exists(dir)):
        os.mkdir(dir)
    print(".shape: ", data_pd.shape)

    data_pd.to_csv(dir + "/" + name + ".csv", index=False, header = cols_bool)

def find_peaks(background, out = 3, down = 0):
    avg = background.mean()
    std = background.std()
    if(down):
        bad_pixels = np.where(np.any(background < avg - out*std, axis = 1))
    else:
        bad_pixels = np.where(np.any(background > avg + out*std, axis = 1))
    print("bad pixels: ", bad_pixels)
    return bad_pixels, avg, std

def del_bad_pixels(info, array):
    indexes = info[0]
    avg = info[1]
    std = info[2]
    
    for i in range(len(indexes)):
        array[indexes[i]] = (array[indexes[i]+1] + array[indexes[i]-1])/2

    return array

def append_non_repeating(array1, array2):
    for item in array2:
        if item not in array1:
            array1 = np.append(array1, item)

    # ret = array1[0]
    # array1 = np.sort(array1)
    # diff = np.zeros(array1.size-1)
    # for i in range(array1.size-1):
    #     diff[i] = array1[i+1] - array1[i]
    
    # indexes = np.zeros(1)
    # x = diff[0]
    # for i in range(array1.size-1):
    #     if(diff[i]!=1):
    #         indexes = np.append(indexes, array1[i])
    return np.array([ 279, 332, 384, 440, 1030])

    # xmin =0, xmax = 0
    # for i in range(len(array1)-2):
    #     if(array1[i] == array1[i+1]+1 and array1[i] != array1[i+1]+1):
    #         xmin = i
    #     if(array1[i+1] == array1[i+2]+1):
    #         xmax = i
    #     if(array1[i] != array1[i+1]+1):
    #         ret = np.append(ret, array1[int((xmax-xmin)/2)])
        

    return ret
    