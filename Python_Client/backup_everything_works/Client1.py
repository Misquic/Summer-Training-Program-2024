import requests
import numpy as np
import pandas as pd
import os
import time
from io import StringIO
#import matplotlib.pyplot as plt


def measure_and_save(dir, name): # function used to measure only once and immidiately save results in <dir>/<name>.csv
    r = requests.get("http://192.168.0.2:8000/spectr/get/IntTime")

    print(r.text)
    print()

    r = requests.get("http://192.168.0.2:8000/spectr/measure")

    trans = str.maketrans({"{": None, "}": None})
    text = r.text.translate(trans) # 123 -> "{", 125 -> "}" ,   GOTOWE DO ZAPISU DO PLIKU, JESLI BRAK OBROBKI TERAZ TO LEPIEJ ZAPISAC TO, BEDZIE SYZYBCIEJ?
                                                                #READY TO SAVE TO FILE, IF NO DATA MANIPULATION NOW THEN IT IS BETTER TO SAVE THAT STRING, FASTER?

    data = list(map(str.strip, text.split(','))) # string to list
    data = np.array(data, dtype = int)
    pixels = data.size

    pd_data = pd.DataFrame(data)
    if(not os.path.exists(dir)):
        os.mkdir(dir)
    pd_data.to_csv(dir + name + ".csv", header=False, index=False )   #zapis do pliku, ale nie oplaca sie go robic, bo wcześniej już mamy w tej formie 
                                                                #SAVE TO FILE, BUT NOT WORTH? PREVIOUS(8 LINES ABOVE) APPROACH FASTER?

def measure(): #function used to measure and get numpy array from measurement for further use
    r = requests.get("http://192.168.0.2:8000/spectr/measure")

    trans = str.maketrans({"{": None, "}": None})
    text = r.text.translate(trans)

    data = list(map(str.strip, text.split(','))) # string to list
    data = np.array(data, dtype = int)
    data = np.reshape(data, (data.size, 1))
    #print(data)
    time.sleep(get_IntTime()/1_000_000)

    print("Done acquiring spectr data")
    return data
    
def measure_and_concat(data_big): # function to measure and concatenate overwrites the array in the argument
    data = measure()
    data_big = np.concat([data_big, data], axis = 1)
    return data_big

def get_pixels():
    data = measure()
    return len(data)

def set_IntTime(IntTime): # set time in microseconds
    if(type(IntTime) != type( int(23))):
        print("Error: type of IntTime invalid, use int")
        return
    if(IntTime < 10_000 | IntTime > 10_000_000):
        print("Error: IntTime too big or too small, make sure: 10_000 <= IntTime <= 10_000_000")
    r = requests.get("http://192.168.0.2:8000/spectr/set/IntTime?x=" + str(int(IntTime)))
    print("/set/IntTime?x=" + str(int(IntTime)) + " result: " + r.text)

def get_IntTime(): #in us
    r = requests.get("http://192.168.0.2:8000/spectr/get/IntTime")
    # print(pd.read_json(StringIO(r.text)))
    return np.array(pd.read_json(StringIO(r.text)))[0,0]

def get_wavelength():
    wave = pd.read_csv("./wavelength.csv")
    wave = np.array(wave)
    return wave




# print(data[1] + data[2])

# [fig, ax] = plt.subplots()
# x = np.linspace(320, 1000, pixels)
# ax.plot(x,data, '.', ms = 1)
# ax.set( xlim = [x.min(), x.max()], ylim = [0, data.max()])
# ax.set(xlabel ="wavelength [nm]", ylabel = "intensity [-]")


# plt.show()