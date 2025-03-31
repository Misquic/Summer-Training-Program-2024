import sys
sys.path.append('./') # to use current directory modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
import func

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

def plot_all_data(data1: _ArrayLike, col_names: _ArrayLike, path: str, data2: _ArrayLike = None, show: bool = False):
    path = path + "normal"
    wave = get_wavelength()
    cmap = cm._colormaps["jet"]
    if(data2 is None):
        fig, ax = plt.subplots()
        fig.set_size_inches(12, 6)
        colors = np.arange(0,len(data1[0,:])+1, 1)
        colors = colors / colors.max()
        norm = Normalize(vmin=0, vmax=1)
        colors = cmap(norm(colors))
        for i in range(col_names.size):
            #ax.plot(ys = np.arange(1, 2049, 1),xs = data1[:,col_names.size - 1-i], zs = i, label = round(col_names[col_names.size - 1-i], 2), ms = 0.2)
            if(type(col_names[0]) == type("str")):
                ax.plot(wave, data1[:,col_names.size - 1-i], label = str(col_names[col_names.size - 1-i]) + " [V]", ms = 0.2, color = colors[i])
            else:
                ax.plot(wave, data1[:,col_names.size - 1-i], label = str(round(col_names[col_names.size - 1-i], 2)) + " [V]", ms = 0.2, color = colors[i])
            print("\r   ", end = "")
            print(str(round((i+1)*100/col_names.size, 2)) + "%", end = "")
        ax.set_xticks(np.arange(int(wave.min()/100)*100, wave.max()+1, 100))
        ax.set(xlabel = "wavelength [nm]", ylabel = "intensity")
        ax.legend()
        print()
        fig.savefig(path + ".png", dpi = 350)        
        if(show):
            plt.show()
        print("saved plot: " + path + ".png")
    else:
        fig, ax = plt.subplots(2,1)
        fig.set_size_inches(10, 10)
        for i in range(col_names.size):
            ax[0].plot(data1[:,i], label = round(col_names[i], 2))
            ax[1].plot(data2[:,i], label = round(col_names[i], 2))
            ax[0].legend()
            ax[1].legend()
            print("\r   ", end = "")
            print(str(round((i+1)*100/col_names.size, 2)) + "%", end = "")

        print()
        fig.savefig( path + ".png", dpi = 350)

        if(show):
            plt.show()
        print("saved plot: " + path + ".png")

def boxplot_all_data(data1: _ArrayLike, col_names: _ArrayLike, path: str, data2: _ArrayLike = None, show: bool = False):

    path = path + "box"
    cmap = cm._colormaps["jet"]
    fig, ax = plt.subplots(projection='3d')
    # fig = plt.figure()
    # ax = fig.add_subplot(projection='3d')
    fig.set_size_inches(10, 5)
    Y = get_wavelength()
    if(type(col_names[0]) == type("str")):
        X = np.arange(1,col_names.size + 1, 1)
    else:
        X = col_names
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
    fig.savefig( path + ".png", dpi = 350)        

    if(show):
        plt.show()
    print("saved plot: " + path + ".png")

def surfplot_all_data(data1: _ArrayLike, col_names: _ArrayLike, path: str, start = 0, stop = -1, data2: _ArrayLike = None, show: bool = False):
    path = path + "sufr"
    cmap = cm._colormaps["jet"]
    fig, ax = plt.subplots(projection = "3d")
    fig.set_size_inches(10, 5)
    Y = get_wavelength()[start:stop]
    if(type(col_names[0]) == type("str")):
        X = np.arange(1,col_names.size + 1, 1)
    else:
        X = col_names
    X, Y = np.meshgrid(X,Y)
    Z = data1[start:stop, :]
    surf = ax.plot_surface(X, Y, Z, cmap = cmap, antialiased = False, rcount = Z.shape[0], ccount = Z.shape[1])
    fig.colorbar(surf, cmap = cmap)
    ax.set(xlabel = "voltqages [V]", ylabel = "wavelength [nm]", zlabel = "counts")
    fig.savefig( path + ".png", dpi = 350)  

    if(show):
        plt.show()
    print("saved plot: " + path + ".png")

def contourplot_all_data(data1: _ArrayLike, col_names: _ArrayLike, path: str, start = 0, stop = -1, data2: _ArrayLike = None, show: bool = False):
    path = path + "contour"
    cmap = cm._colormaps["jet"]
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 5)
    X = get_wavelength()[start:stop]
    Y = col_names
    if(type(col_names[0]) == type("str")):
        Y = np.arange(1,col_names.size + 1, 1)
    else:
        Y = col_names
    X, Y = np.meshgrid(X,Y)
    Z = data1[start:stop, :].transpose()
    surf = ax.contour(X, Y, Z, cmap = cmap, antialiased = False)
    fig.colorbar(surf, cmap = cmap)
    ax.set(ylabel = "voltqages [V]", xlabel = "wavelength [nm]")
    fig.savefig( path + ".png", dpi = 350)  

    if(show):
        plt.show()
    print("saved plot: " + path + ".png")

def pcolorplot_all_data(data1: _ArrayLike, col_names: _ArrayLike, path: str, start = 0, stop = -1, data2: _ArrayLike = None, show: bool = False):
    path = path + "pcolor"
    cmap = cm._colormaps["jet"]
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 5)
    X = get_wavelength()[start:stop]
    if(type(col_names[0]) == type("str")):
        Y = np.arange(1,col_names.size + 1, 1)
    else:
        Y = col_names
    X, Y = np.meshgrid(X,Y)
    Z = data1[start:stop, :].transpose()
    surf = ax.pcolormesh(X, Y, Z, cmap = cmap, antialiased = True)
    fig.colorbar(surf, cmap = cmap)
    ax.set(ylabel = "voltqages [V]", xlabel = "wavelength [nm]")
    fig.savefig( path + ".png", dpi = 350)  

    if(show):
        plt.show()
    print("saved plot: " + path + ".png")

def peaks_plot(data1: _ArrayLike, col_names: _ArrayLike, path: str, start = 0, stop = -1, out = 3, show: bool = False):
    path = path + "peaks"
    cmap = cm._colormaps["jet"]
    wave = get_wavelength()[start:stop, 0]
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 5)
   
    find = np.reshape(data1[start:stop,int(col_names.size/2)], (data1[start:stop,int(col_names.size/2)].size,1))
    find2 = np.reshape(data1[start:stop,-1], (data1[start:stop,-1].size,1))


    print("peaks: ")
    peaks_i = func.find_peaks(find, out = out)[0][0] # 
    peaks_i2 = func.find_peaks(find2, out = out)[0][0] # 
    print(peaks_i)
    print(peaks_i2)



    peaks_i = func.append_non_repeating(peaks_i, peaks_i2)

    print(peaks_i)
    print("peaks: ")



    colors = np.arange(0,len(peaks_i)+1, 1)
    #print(colors)
    colors = colors / colors.max()
    #print(colors)
    norm = Normalize(vmin=0, vmax=1)
    colors = cmap(norm(colors))
    #print(colors)
    for i in range(len(peaks_i)):
        peaks = []
        for j in range(len(data1[0,:])):
            peaks.append(data1[peaks_i[i]+ start,j]) #################### tu problem
            #print("jsda, ", data1[peaks_i[i]][j]) ##################
        #print(peaks)
        #print(peaks_i)
        #print("{i: >3}) {mess: >{len_max}}\'  ".format(i="("+str(i), mess = ("\'"+str(dirs[i])), len_max = len_max+1), end = "")
        ax.plot(col_names, peaks, label = str(round(wave[peaks_i[i]], 2)) + " [nm]", color = colors[i])
        #print(colors[i])
    ax.legend(loc = "upper left")
    ax.set(xlabel = "voltage [V]", ylabel = "intensity [-]")
    fig.savefig( path + ".png", dpi = 350)
    print("saved plot: " + path + ".png")
    if(show):
        plt.show()

# def del_bckg(data, background, path: str):
#     for i in range(data.shape[1]):
#         data[:,i] = data[:, 1] - background
#     func.save_data_big(data_big = data, dir = path, data_len = len(background), name = "deleted_background")


x = "q"
while(x == "q"): #beznadziejnie zrobione
    dir = "./"
    dirs = list_directory(dir, only_dir=True)
    x = input("Which directory to use? ")
    if(x == "l"):
        break
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
if(x!= "l"):
    x = int(x)
    print("opening " + dirs[x])
    path1 = dir + "/" + dirs[x]
    name1 = dirs[x]
    x2 = (x+1)%len(dirs)
    path2 = dir + "/" + dirs[x2]
    name2 = dirs[x2]

    with open("last_path.txt", "w") as lp:
        save = [dir, path1, name1, path2, name2]
        for i in range(len(save)):
            lp.write(save[i])
            lp.write("\n")
else:
    with open("last_path.txt", "r") as lp:
        dir = lp.readline()[:-1]
        path1 = lp.readline()[:-1]
        name1 = lp.readline()[:-1]
        path2 = lp.readline()[:-1]
        name2 = lp.readline()[:-1]   


print(dir, path1, path2)
# normal ################
data_voltages = pd.read_csv(path1, header=None, skiprows = lambda x: x!=0)
data_voltages = np.array(data_voltages)[0]
data1 = pd.read_csv(path1)
data1 = np.array(data1)
# for i in range(len(data1[0,:])):
#     print(i)
#     data1[:,i] = data1[:,i]/data1[:,i].max()

data1 = data1/data1.max()
for j in range(len(data_voltages)):
    info = func.find_peaks(np.reshape(data1[:,j], (data1[:,j].size,1)), out = 2, down = 1)
    for i in range(len(data_voltages)):
        data1[:,i] = func.del_bad_pixels(info, np.reshape(data1[:,i], (data1[:,i].size,1)))[:,0]

info = func.find_peaks(np.reshape(data1[:,0], (data1[:,0].size,1)), out = 2)
for i in range(len(data_voltages)):
    data1[:,i] = func.del_bad_pixels(info, np.reshape(data1[:,i], (data1[:,i].size,1)))[:,0]



data2_names = pd.read_csv(path2, header=None, skiprows = lambda x: x!=0)
data2_names = np.array(data2_names)[0]
data2 = pd.read_csv(path2)
data2 = np.array(data2)

peaks_plot(data1, col_names=data_voltages, start = 0, stop = -1, out = 5, path = dir + "/", show = 0 )
plot_all_data(data1 = data1, col_names=data_voltages, path = dir + "/", show = 0)
plot_all_data(data1 = data2, col_names=data2_names, path = dir + "/bckg_", show = 1)
# plt.close()
# pcolorplot_all_data(data1 = data1, start = 20, stop = -20, col_names=data_voltages, path = dir + "/", show = 1)
# #plot_all_data(data1 = data1, data2 = data2, col_names=data_voltages, path = dir + "/both", show = 0)














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
