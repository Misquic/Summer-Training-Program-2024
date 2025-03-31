import sys
sys.path.append('./') # to use current directory modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize


import os
from numpy._typing import _ArrayLike
from typing import overload
from Client1 import get_wavelength

def check_ext(path, ext: str):
    list = path.split(".")
    if(list[-1] == ext):
        return True
    return False

def list_directory(dir: str, only_dir: bool = False, ext: str = ""):
    #dirs = os.listdir(dir)
    if(only_dir):
        ext = ""
        dirs = [f for f in os.listdir(dir) if os.path.isdir(dir + "/" + f)]
    else:
        if(ext == ""):
            dirs = os.listdir(dir)
        else:
            dirs = [f for f in os.listdir(dir) if check_ext(dir + "/" + f, ext)]

    dirs.sort(reverse=True)

    g = 0
    len_max = 0
    for i,x in enumerate(dirs):
        len_max = max(len_max, len(x))

    for i in range(len(dirs)):
        print("{i: >3}) {mess: >{len_max}}\'  ".format(i="("+str(i), mess = ("\'"+str(dirs[i])), len_max = len_max+1), end = "")
        g = g + 1
        if(g == 5 or i == len(dirs)-1):
            g = 0
            print()
    return dirs

def plot_all_data(data1: _ArrayLike, data_voltages: _ArrayLike, path: str, data2: _ArrayLike = None, show: bool = False):
    if(data2 is None):
        fig = plt.figure()
        ax = fig.add_subplot()
        fig.set_size_inches(10, 5)
        for i in range(data_voltages.size):
            #ax.plot(ys = np.arange(1, 2049, 1),xs = data1[:,data_voltages.size - 1-i], zs = i, label = round(data_voltages[data_voltages.size - 1-i], 2), ms = 0.2)
            ax.plot(data1[:,data_voltages.size - 1-i], label = round(data_voltages[data_voltages.size - 1-i], 2), ms = 0.2)
            print("\r   ", end = "")
            print(str(round((i+1)*100/data_voltages.size, 2)) + "%", end = "")
        ax.legend()
        print()
        if(show):
            plt.show()
        print("saved plot: " + path + ".png")
        plt.savefig(path + ".png", dpi = 350)        
    else:
        fig, ax = plt.subplots(2,1)
        fig.set_size_inches(10, 10)
        for i in range(data_voltages.size):
            ax[0].plot(data1[:,i], label = round(data_voltages[i], 2))
            ax[1].plot(data2[:,i], label = round(data_voltages[i], 2))
            ax[0].legend()
            ax[1].legend()
            print("\r   ", end = "")
            print(str(round((i+1)*100/data_voltages.size, 2)) + "%", end = "")

        print()

        if(show):
            plt.show()
        print("saved plot: " + path + ".png")
        plt.savefig(path + ".png", dpi = 350)

def boxplot_all_data(data1: _ArrayLike, data_voltages: _ArrayLike, path: str, data2: _ArrayLike = None, show: bool = False):
    path = path = "box"
    cmap = cm._colormaps["jet"]
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    fig.set_size_inches(10, 5)
    Y = get_wavelength()
    X = data_voltages
    X, Y = np.meshgrid(X,Y)
    X = np.ravel(X)
    Y = np.ravel(Y)
    dX = np.ones_like(X)
    dY = np.ones_like(Y)
    Z = np.zeros_like(data1)
    Z = np.ravel(Z)
    dZ = data1
    dZ = np.ravel(dZ)
    #print(dZ)
    norm = Normalize(vmin=data1.min(), vmax=data1.max())
    colors = cmap(norm(dZ))
    bar = ax.bar3d(X, Y, Z, dX, dY, dZ, color = colors)
    #print(colors)
    ax.set(xlabel = "voltqages [V]", ylabel = "wavelength [nm]", zlabel = "counts")
    fig.colorbar(bar, cmap = cmap)
    print()
    if(show):
        plt.show()
    print("saved plot: " + path + ".png")
    plt.savefig(path + ".png", dpi = 350)        

def surfplot_all_data(data1: _ArrayLike, data_voltages: _ArrayLike, path: str, start = 0, stop = -1, data2: _ArrayLike = None, show: bool = False):
    path = path = "sufr"
    cmap = cm._colormaps["jet"]
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    fig.set_size_inches(10, 5)
    Y = get_wavelength()[start:stop]
    X = data_voltages
    X, Y = np.meshgrid(X,Y)
    Z = data1[start:stop, :]
    surf = ax.plot_surface(X, Y, Z, cmap = cmap, antialiased = False, rcount = Z.shape[0], ccount = Z.shape[1])
    fig.colorbar(surf, cmap = cmap)
    ax.set(xlabel = "voltqages [V]", ylabel = "wavelength [nm]", zlabel = "counts")
    if(show):
        plt.show()
    print("saved plot: " + path + ".png")
    plt.savefig(path + ".png", dpi = 350)  

def contourplot_all_data(data1: _ArrayLike, data_voltages: _ArrayLike, path: str, start = 0, stop = -1, data2: _ArrayLike = None, show: bool = False):
    path = path = "contour"
    cmap = cm._colormaps["jet"]
    fig = plt.figure()
    ax = fig.add_subplot()
    fig.set_size_inches(10, 5)
    X = get_wavelength()[start:stop]
    Y = data_voltages
    X, Y = np.meshgrid(X,Y)
    Z = data1[start:stop, :].transpose()
    surf = ax.contour(X, Y, Z, cmap = cmap, antialiased = False)
    fig.colorbar(surf, cmap = cmap)
    ax.set(ylabel = "voltqages [V]", xlabel = "wavelength [nm]")
    if(show):
        plt.show()
    print("saved plot: " + path + ".png")
    plt.savefig(path + ".png", dpi = 350)  

def pcolorplot_all_data(data1: _ArrayLike, data_voltages: _ArrayLike, path: str, start = 0, stop = -1, data2: _ArrayLike = None, show: bool = False):
    path = path = "pcolor"
    cmap = cm._colormaps["jet"]
    fig = plt.figure()
    ax = fig.add_subplot()
    fig.set_size_inches(10, 5)
    X = get_wavelength()[start:stop]
    Y = data_voltages
    X, Y = np.meshgrid(X,Y)
    Z = data1[start:stop, :].transpose()
    surf = ax.pcolormesh(X, Y, Z, cmap = cmap, antialiased = True)
    fig.colorbar(surf, cmap = cmap)
    ax.set(ylabel = "voltqages [V]", xlabel = "wavelength [nm]")
    if(show):
        plt.show()
    print("saved plot: " + path + ".png")
    plt.savefig(path + ".png", dpi = 350)  

x = "q"
while(x == "q"): #beznadziejnie zrobione
    dir = "./"
    dirs = list_directory(dir, only_dir=True)
    x = input("Which directory to use? ")
    x = int(x)
    print("opening " + dirs[x])

    dir = dir + dirs[x]

    dirs = list_directory(dir, only_dir=True)
    x = input("Which directory to use? ")
    x = int(x)
    print("opening " + dirs[x])

    dir = dir + "/" + dirs[x]
    print()
    print(dir)
    print()
    dirs = list_directory(dir, only_dir = False, ext = "csv")
    x = input("Which file to use? q to exit this directory ")

x = int(x)
print("opening " + dirs[x])
path1 = dir + "/" + dirs[x]
name1 = dirs[x]

# put in for loop?
x2 = (x+1)%len(dirs)

# normal ################
data_voltages = pd.read_csv(path1, header=None, skiprows = lambda x: x!=0)
data_voltages = np.array(data_voltages)[0]
data1 = pd.read_csv(path1)
data1 = np.array(data1)

path2 = dir + "/" + dirs[x2]
name2 = dirs[x2]
data2 = pd.read_csv(path2)
data2 = np.array(data2)

plot_all_data(data1 = data1, data_voltages=data_voltages, path = dir + "/" + name1, show = 1)
pcolorplot_all_data(data1 = data1, start = 20, stop = -20, data_voltages=data_voltages, path = dir + "/", show = 1)
#plot_all_data(data1 = data1, data2 = data2, data_voltages=data_voltages, path = dir + "/both", show = 0)














# # data kula
# data1 = pd.read_csv(path1, header = None)
# data1 = np.array(data1)

# ### do uśredniania
# mean = data1.mean(axis = 1)
# mean = np.reshape(mean, (mean.size, 1))
# print(mean.shape)
# # pd_data = pd.DataFrame(mean)
# # if(not os.path.exists(dir)):
# #     os.mkdir(dir)
# # pd_data.to_csv(dir +  "/mean2.csv", header=False, index=False )   #zapis do pliku, ale nie oplaca sie go robic, bo wcześniej już mamy w tej formie 
# bckg = pd.read_csv("D:/Python_Client/Data_kula/2024_08_05_11_24_48/bckq_mean.csv",header = None)
# bckg = np.array(bckg)
# print(bckg.shape)
# ready = mean - bckg
# print(ready.shape)
# #### do dokładania wavelength
# #data1 = data1[:,0]
# wave = get_wavelength()
# print(wave.shape)
# ready = np.concat([wave, ready], axis = 0)
# ready = np.reshape(ready, (2, wave.size))
# ready = ready.transpose()
# pd_data = pd.DataFrame(ready)
# if(not os.path.exists(dir)):
#     os.mkdir(dir)
# pd_data.to_csv(dir +  "/ready2.csv", header=False, index=False )   #zapis do pliku, ale nie oplaca sie go robic, bo wcześniej już mamy w tej formie 
