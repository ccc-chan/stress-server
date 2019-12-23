from multiprocessing import Process, Pool, freeze_support, Manager
import os, time, random
from numpy import pi, sin
from price import appModel as model
from price import others as others
from price import heatMap as heatMap


def long_time_task(name):
 
    print('Run task %s (%s)...' % (name, os.getpid()))
 
    start = time.time()
 
    time.sleep(1)
 
    end = time.time()
 
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))


def test():
    print('Run task %s...' % (os.getpid()))

def worker(i, data, inputSearch, ratePoints, s0Shock, sigmaShock, return_dict):
    result = model.getDataWithSearch(data, inputSearch, ratePoints, s0Shock, sigmaShock)
    return_dict[i] = result[1][0]
    print('Run task %s (%s)...' % (i, os.getpid()))