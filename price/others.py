#!/usr/bin/env python
# coding: utf-8


from numpy import *
import matplotlib.pyplot as plt
from scipy import integrate
from scipy import stats
import pandas as pd

from datetime import datetime, timedelta

from price import pricingModel as pm

def setT(data, today):
    T_tmp = []
    setDay = datetime.strptime(today, '%Y-%m-%d') #fixed format
    for daysDelta in (data["期末定价日"] - setDay):
        if type(daysDelta.days) != type(int(1)): #should be type.int
            T_tmp.append(int(0))
        elif daysDelta.days < 0:
            T_tmp.append(int(0))
        else:
            T_tmp.append(daysDelta.days)
    data["T"] = T_tmp #it means from the chosen date to the end date, it also determines the term structure
    return data

def computePrice(data, dataType, indexToFind, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    if dataType == "DBC":
        [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp] = pm.computeDBCData(data, indexToFind, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock)
    elif dataType == "DBP":
        [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp] = pm.computeDBPData(data, indexToFind, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock)
    elif dataType == "VPUT":
        [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp] = pm.computePutData(data, indexToFind, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock)
    elif dataType == "VCALL":
        [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp] = pm.computeCallData(data, indexToFind, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock)
    elif dataType == "UOC":
        [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp] = pm.computeUOCData(data, indexToFind, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock)
    elif dataType == "DOP":
        [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp] = pm.computeDOPData(data, indexToFind, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock)
    elif dataType == "BCALL":
        [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp] = pm.computeBCallData(data, indexToFind, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock)
    else:
        [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp] = [None, None, None, None, None]
        
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]


def greeksExposure(indexToFind, data, quantity, buy, st, price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp):
    
    if quantity is not None and delta_tmp is not None and st is not None:
        deltaExposure = quantity * delta_tmp * st
        if data["类型"][indexToFind] == "BCALL":
            limit = data.loc[indexToFind, "Digital amount"]
            limit = float(limit[:-1]) / 100
            deltaExposure = deltaExposure * data["startingPrice"][indexToFind] * limit
    else:
        deltaExposure = None
    
    if quantity is not None and gamma_tmp is not None and st is not None:
        gammaExposure = quantity * gamma_tmp * st**2
        if data["类型"][indexToFind] == "BCALL":
            limit = data.loc[indexToFind, "Digital amount"]
            limit = float(limit[:-1]) / 100
            gammaExposure = gammaExposure * data["startingPrice"][indexToFind] * limit
    else:
        gammaExposure = None
    
    if quantity is not None and vega_tmp is not None:
        vegaExposure = quantity * vega_tmp
        if data["类型"][indexToFind] == "BCALL":
            limit = data.loc[indexToFind, "Digital amount"]
            limit = float(limit[:-1]) / 100
            vegaExposure = vegaExposure * data["startingPrice"][indexToFind] * limit
    else:
        vegaExposure = None
    
    if quantity is not None and theta_tmp is not None:
        thetaExposure = quantity * theta_tmp / 365
        if data["类型"][indexToFind] == "BCALL":
            limit = data.loc[indexToFind, "Digital amount"]
            limit = float(limit[:-1]) / 100
            thetaExposure = thetaExposure * data["startingPrice"][indexToFind] * limit
    else:
        thetaExposure = None
        
    if delta_tmp is not None:
        delta_tmp = round(delta_tmp * 100, 10)
    if gamma_tmp is not None:
        gamma_tmp = round(gamma_tmp * 100, 10)
    if vega_tmp is not None:
        vega_tmp = round(vega_tmp, 10)
    if theta_tmp is not None:
        theta_tmp = round(theta_tmp * 100, 10)
    if deltaExposure is not None:
        deltaExposure = round(deltaExposure, 10)
    if gammaExposure is not None:
        gammaExposure = round(gammaExposure * 0.01, 10)
    if vegaExposure is not None:
        vegaExposure = round(vegaExposure * 0.01, 10)
    if thetaExposure is not None:
        thetaExposure = round(thetaExposure, 10)
        
    if buy is not None and buy == False:
        if price_tmp is not None:
            price_tmp = -1 * price_tmp
        if deltaExposure is not None:
            deltaExposure = -1 * deltaExposure
        if delta_tmp is not None:
            delta_tmp = -1 * delta_tmp
        if gammaExposure is not None:
            gammaExposure = -1 * gammaExposure
        if gamma_tmp is not None:
            gamma_tmp = -1 * gamma_tmp
        if vegaExposure is not None:
            vegaExposure = -1 * vegaExposure
        if vega_tmp is not None:
            vega_tmp = -1 * vega_tmp
        if thetaExposure is not None:
            thetaExposure = -1 * thetaExposure
        if theta_tmp is not None:
            theta_tmp = -1 * theta_tmp
    
    idToFind = data["AGGREGATION BUNDLE"][indexToFind]
    return [idToFind, quantity, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, vegaExposure, vega_tmp, thetaExposure, theta_tmp]

def convertDataSet(idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, vegaExposureSet, vega_tmpSet, thetaExposureSet, theta_tmpSet):
    dataExport = [] #fixed format
    dataExport.append(idSet)
    dataExport.append(price_tmpSet)
    dataExport.append(deltaExposureSet)
    dataExport.append(delta_tmpSet)
    dataExport.append(gammaExposureSet)
    dataExport.append(gamma_tmpSet)
    dataExport.append(vegaExposureSet)
    dataExport.append(vega_tmpSet)
    dataExport.append(thetaExposureSet)
    dataExport.append(theta_tmpSet)
    return dataExport

def extractDataSet(dataExport):
    return [dataExport[0], dataExport[1], dataExport[2], dataExport[3], dataExport[4], dataExport[5], dataExport[6], dataExport[7], dataExport[8], dataExport[9]]
    
def sumUpEachList(dataExport):
    [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, vegaExposureSet, vega_tmpSet, thetaExposureSet, theta_tmpSet] = extractDataSet(dataExport)
    priceSum = 0.0
    deltaExposureSum = 0.0
    deltaSum = 0.0
    gammaExposureSum = 0.0
    gammaSum = 0.0
    vegaExposureSum = 0.0
    vegaSum = 0.0
    thetaExposureSum = 0.0
    thetaSum = 0.0
    
    for i in range(len(idSet)):
        if price_tmpSet[i] is not None:
            priceSum = priceSum + price_tmpSet[i]
            deltaExposureSum = deltaExposureSum + deltaExposureSet[i]
            deltaSum = deltaSum + delta_tmpSet[i]
            gammaExposureSum = gammaExposureSum + gammaExposureSet[i]
            gammaSum = gammaSum + gamma_tmpSet[i]
            vegaExposureSum = vegaExposureSum + vegaExposureSet[i]
            vegaSum = vegaSum + vega_tmpSet[i]
            thetaExposureSum = thetaExposureSum + thetaExposureSet[i]
            thetaSum = thetaSum + theta_tmpSet[i]
 
    return [None, priceSum, deltaExposureSum, deltaSum, gammaExposureSum, gammaSum, vegaExposureSum, vegaSum, thetaExposureSum, thetaSum]




