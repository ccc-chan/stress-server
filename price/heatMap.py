#!/usr/bin/env python
# coding: utf-8


from numpy import *
import matplotlib.pyplot as plt
from scipy import integrate
from scipy import stats
import pandas as pd

import seaborn as sns

from datetime import datetime, timedelta

from price import appModel as model
from price import others as others


def plotHeatMap(idNumber, today, ratePoints):
    #ratePoints = [None, 0.023, 0.0251, 0.0256, 0.0257, 0.0259, 0.0265, 0.0271, 0.028, 0.0288]
    #idNumber = "19461157"
    #today = "2019-07-08"
    data = model.readData()
    data = others.setT(data,today)
    scale = ["-5%", "-4%", "-3%", "-2%", "-1%", "0%", "1%", "2%", "3%", "4%", "5%"]
    
    #x is in s0, y is in sigma
    priceSet = []
    deltaExposureSet = [] 
    deltaSet = []
    gammaExposureSet = []
    gammaSet = []
    vegaExposureSet = [] 
    vegaSet = []
    thetaExposureSet = []
    thetaSet =[]

    for y in linspace(0.95, 1.05, 11):
        priceSubSet = []
        deltaExposureSubSet = [] 
        deltaSubSet = []
        gammaExposureSubSet = []
        gammaSubSet = []
        vegaExposureSubSet = [] 
        vegaSubSet = []
        thetaExposureSubSet = []
        thetaSubSet =[]
        for x in linspace(0.95, 1.05, 11):
            [idToFind, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, 
             vegaExposure, vega_tmp, thetaExposure, theta_tmp] = model.getData(data, idNumber, ratePoints, x, y)
            priceSubSet.append(price_tmp[0])
            deltaExposureSubSet.append(deltaExposure[0])
            deltaSubSet.append(delta_tmp[0])
            gammaExposureSubSet.append(gammaExposure[0])
            gammaSubSet.append(gamma_tmp[0])
            vegaExposureSubSet.append(vegaExposure[0])
            vegaSubSet.append(vega_tmp[0])
            thetaExposureSubSet.append(thetaExposure[0])
            thetaSubSet.append(theta_tmp[0])
        priceSet.append(priceSubSet)
        deltaExposureSet.append(deltaExposureSubSet)
        deltaSet.append(deltaSubSet)
        gammaExposureSet.append(gammaExposureSubSet)
        gammaSet.append(gammaSubSet)
        vegaExposureSet.append(vegaExposureSubSet)
        vegaSet.append(vegaSubSet)
        thetaExposureSet.append(thetaExposureSubSet)
        thetaSet.append(thetaSubSet)
    
    priceMap = pd.DataFrame(priceSet, index = scale, columns = scale)
    deltaExposureMap = pd.DataFrame(deltaExposureSet, index = scale, columns = scale)
    deltaMap = pd.DataFrame(deltaSet, index = scale, columns = scale)
    gammaExposureMap = pd.DataFrame(gammaExposureSet, index = scale, columns = scale)
    gammaMap = pd.DataFrame(gammaSet, index = scale, columns = scale)
    vegaExposureMap = pd.DataFrame(vegaExposureSet, index = scale, columns = scale)
    vegaMap = pd.DataFrame(vegaSet, index = scale, columns = scale)
    thetaExposureMap = pd.DataFrame(thetaExposureSet, index = scale, columns = scale)
    thetaMap = pd.DataFrame(thetaSet, index = scale, columns = scale)
    
    #plt.figure(figsize=(18, 18))
    #plt.subplot(331)
    plt.figure()
    plt.title("Price")
    sns.heatmap(priceMap, cmap='rainbow') 
    plt.xlabel("S0")
    plt.ylabel("Sigma")
    plt.plot()

    plt.figure()
    #plt.subplot(332)
    plt.title("DeltaExposure")
    sns.heatmap(deltaExposureMap, cmap='rainbow') 
    plt.xlabel("S0")
    plt.ylabel("Sigma")
    plt.plot()

    plt.figure()
    #plt.subplot(333)
    plt.title("Delta_Pct")
    sns.heatmap(deltaMap, cmap='rainbow') 
    plt.xlabel("S0")
    plt.ylabel("Sigma")
    plt.plot()

    plt.figure()
    #plt.subplot(334)
    plt.title("GammaExposure")
    sns.heatmap(gammaExposureMap, cmap='rainbow') 
    plt.xlabel("S0")
    plt.ylabel("Sigma")
    plt.plot()

    plt.figure()
    #plt.subplot(335)
    plt.title("Gamma_Pct")
    sns.heatmap(gammaMap, cmap='rainbow') 
    plt.xlabel("S0")
    plt.ylabel("Sigma")
    plt.plot()

    plt.figure()
    #plt.subplot(336)
    plt.title("VegaExposure")
    sns.heatmap(vegaExposureMap, cmap='rainbow') 
    plt.xlabel("S0")
    plt.ylabel("Sigma")
    plt.plot()

    plt.figure()
    #plt.subplot(337)
    plt.title("Vega_Pct")
    sns.heatmap(vegaMap, cmap='rainbow') 
    plt.xlabel("S0")
    plt.ylabel("Sigma")
    plt.plot()

    plt.figure()
    #plt.subplot(338)
    plt.title("ThetaExposure")
    sns.heatmap(thetaExposureMap, cmap='rainbow') 
    plt.xlabel("S0")
    plt.ylabel("Sigma")
    plt.plot()

    plt.figure()
    #plt.subplot(339)
    plt.title("Theta_Pct")
    sns.heatmap(thetaMap, cmap='rainbow') 
    plt.xlabel("S0")
    plt.ylabel("Sigma")
    plt.plot()
    
    #plt.savefig("HeatMap.jpg")
    plt.show()





