#!/usr/bin/env python
# coding: utf-8


from numpy import sqrt, pi, exp, log, array, linspace
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
            T_tmp.append(int(-1))
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

#Switch theta & vega positions here.
def greeksExposure(indexToFind, data, quantity, buy, st, price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp):
    
    if quantity is not None and delta_tmp is not None and st is not None:
        deltaExposure = quantity * delta_tmp * st
        if data["类型"][indexToFind] == "BCALL":
            limit = data.loc[indexToFind, "Digital amount"]
            if limit is not None:
                limit = float(limit[:-1]) / 100
            else:
                limit = 1
            deltaExposure = deltaExposure * data["startingPrice"][indexToFind] * limit
    else:
        deltaExposure = None
    
    if quantity is not None and gamma_tmp is not None and st is not None:
        gammaExposure = quantity * gamma_tmp * st**2
        if data["类型"][indexToFind] == "BCALL":
            limit = data.loc[indexToFind, "Digital amount"]
            if limit is not None:
                limit = float(limit[:-1]) / 100
            else:
                limit = 1
            gammaExposure = gammaExposure * data["startingPrice"][indexToFind] * limit
    else:
        gammaExposure = None
    
    if quantity is not None and vega_tmp is not None:
        vegaExposure = quantity * vega_tmp
        if data["类型"][indexToFind] == "BCALL":
            limit = data.loc[indexToFind, "Digital amount"]
            if limit is not None:
                limit = float(limit[:-1]) / 100
            else:
                limit = 1
            vegaExposure = vegaExposure * data["startingPrice"][indexToFind] * limit
    else:
        vegaExposure = None
    
    if quantity is not None and theta_tmp is not None:
        thetaExposure = quantity * theta_tmp / 365
        if data["类型"][indexToFind] == "BCALL":
            limit = data.loc[indexToFind, "Digital amount"]
            if limit is not None:
                limit = float(limit[:-1]) / 100
            else:
                limit = 1
            thetaExposure = thetaExposure * data["startingPrice"][indexToFind] * limit
    else:
        thetaExposure = None

    if quantity is not None and price_tmp is not None:
        PV = quantity * price_tmp
    else:
        PV = None
        
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
    if PV is not None:
        PV = round(PV, 10)
        
    if buy is not None and buy == False:
        if price_tmp is not None:
            ######Warning: To be Fixed...
            if data["类型"][indexToFind] == "VCALL" or data["类型"][indexToFind] == "VPUT":
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
        if PV is not None:
            PV = -1 * PV
    
    idToFind = data["AGGREGATION BUNDLE"][indexToFind]
    #Up to here, theta then vega only
    return [idToFind, quantity, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, thetaExposure, theta_tmp, vegaExposure, vega_tmp, PV]

def convertDataSet(idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet):
    dataExport = [] #fixed format
    dataExport.append(idSet)
    dataExport.append(price_tmpSet)
    dataExport.append(deltaExposureSet)
    dataExport.append(delta_tmpSet)
    dataExport.append(gammaExposureSet)
    dataExport.append(gamma_tmpSet)
    dataExport.append(thetaExposureSet)
    dataExport.append(theta_tmpSet)
    dataExport.append(vegaExposureSet)
    dataExport.append(vega_tmpSet)
    dataExport.append(PVSet)
    return dataExport

def extractDataSet(dataExport):
    return [dataExport[0], dataExport[1], dataExport[2], dataExport[3], dataExport[4], dataExport[5], dataExport[6], dataExport[7], dataExport[8], dataExport[9], dataExport[10]]
    
def sumUpEachList(dataExport):
    [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet] = extractDataSet(dataExport)
    priceSum = 0.0
    deltaExposureSum = 0.0
    deltaSum = 0.0
    gammaExposureSum = 0.0
    gammaSum = 0.0
    thetaExposureSum = 0.0
    thetaSum = 0.0
    vegaExposureSum = 0.0
    vegaSum = 0.0
    PVSum = 0.0
    
    for i in range(len(idSet)):
        if price_tmpSet[i] is not None:
            priceSum = priceSum + price_tmpSet[i]
        if deltaExposureSet[i] is not None:
            deltaExposureSum = deltaExposureSum + deltaExposureSet[i]
        if delta_tmpSet[i] is not None:
            deltaSum = deltaSum + delta_tmpSet[i]
        if gammaExposureSet[i] is not None:
            gammaExposureSum = gammaExposureSum + gammaExposureSet[i]
        if gamma_tmpSet[i] is not None:
            gammaSum = gammaSum + gamma_tmpSet[i]
        if thetaExposureSet[i] is not None:
            thetaExposureSum = thetaExposureSum + thetaExposureSet[i]
        if theta_tmpSet[i] is not None:
            thetaSum = thetaSum + theta_tmpSet[i]
        if vegaExposureSet[i] is not None:
            vegaExposureSum = vegaExposureSum + vegaExposureSet[i]
        if vega_tmpSet[i] is not None:
            vegaSum = vegaSum + vega_tmpSet[i]
        if PVSet[i] is not None:
            PVSum = PVSum + PVSet[i]
 
    return [None, 
        outputFormatter(priceSum, False), 
        outputFormatter(deltaExposureSum, True), 
        outputFormatter(deltaSum, False), 
        outputFormatter(gammaExposureSum, True), 
        outputFormatter(gammaSum, False), 
        outputFormatter(thetaExposureSum, True), 
        outputFormatter(thetaSum, False), 
        outputFormatter(vegaExposureSum, True), 
        outputFormatter(vegaSum, False), 
        outputFormatter(PVSum, True)]

def computeCondition(s0_tmp, k_tmp, sigma, T_tmp):
    if s0_tmp is not None and k_tmp is not None and sigma is not None and T_tmp is not None:
        if s0_tmp > 0 and k_tmp > 0 and sigma > 0 and T_tmp >= 0: #can be excercised on the same day
            return True
        else:
            return False
    else:
        return False

##Deprecated...
def isNormalID(idToIdentify):
    if len(idToIdentify) == 8 and idToIdentify.isdigit():
        return True
    else:
        return False

def outputFormatter(floatNumber, isTenThousand):
    if floatNumber is not None:
        stringNumber = str(floatNumber)
        if isTenThousand:
            if len(stringNumber.split(".")[0]) <= 4:
                floatNumber = round(floatNumber, 2)
            else:
                floatNumber = round(floatNumber, 2)
        else:
            floatNumber = round(floatNumber, 4)
    return floatNumber

def listFormatter(floatList, isTenThousand):
    newList = []
    for item in floatList:
        if isTenThousand and item is not None:
            item = item / 10000
        newList.append(outputFormatter(item, isTenThousand))
    return newList






