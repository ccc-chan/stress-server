from multiprocessing import Pool, Manager
from numpy import sqrt, pi, exp, log, array, linspace
import matplotlib.pyplot as plt
from scipy import integrate
from scipy import stats
import pandas as pd
import os

from price import appModel as model
from price import others as others

def getDataBoosted(i, data, inputSearch, ratePoints, s0Shock, sigmaShock, return_dict):
    [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet] = model.getDataWithSearch(data, inputSearch, ratePoints, s0Shock, sigmaShock)
    convertedData = others.convertDataSet(idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet)
    #print(os.getpid())
    return_dict[i] = convertedData