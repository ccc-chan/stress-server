#!/usr/bin/env python
# coding: utf-8

from numpy import sqrt, pi, exp, log, array, linspace
import matplotlib.pyplot as plt
from scipy import integrate
from scipy import stats
import pandas as pd
import os

from datetime import datetime, timedelta

from price import pricingModel as pm
from price import others as others
from price import riskFreeRate as rate



def readData():
    sigmaDataPath = os.path.abspath(os.path.join(__file__, "../data.xls"))
    sigmaData = pd.read_excel(sigmaDataPath, sheet_name="EOD Position Report")
    sigmaData = sigmaData.where(sigmaData.notnull(), None)
    defaultSigma = None
    defaultTodayPrice = None
    defaultQuantity = None
    
    sigmaDic = {}
    todayPriceDic = {} #todayPrice is the input file day's price and has no relation to the input T
    quantityDic = {}
    liveID = []
    
    for i in range(len(sigmaData)):
        if sigmaData["Unnamed: 1"][i] is not None:
            liveID.append(sigmaData["Unnamed: 1"][i].split()[-1])
            if sigmaData["Vol"][i] is not None:
                sigmaDic[sigmaData["Unnamed: 1"][i].split()[-1]] = (sigmaData["Vol"][i] / 100.0)
            else:
                sigmaDic[sigmaData["Unnamed: 1"][i].split()[-1]] = defaultSigma
            
            if sigmaData["Underlying_Spot"][i] is not None:
                todayPriceDic[sigmaData["Unnamed: 1"][i].split()[-1]] = sigmaData["Underlying_Spot"][i]
            else:
                todayPriceDic[sigmaData["Unnamed: 1"][i].split()[-1]] = defaultTodayPrice
                
            if sigmaData["Quantity"][i] is not None:
                quantityDic[sigmaData["Unnamed: 1"][i].split()[-1]] = sigmaData["Quantity"][i]
            else:
                quantityDic[sigmaData["Unnamed: 1"][i].split()[-1]] = defaultQuantity


    historyDataPath = os.path.abspath(os.path.join(__file__, "../data.xls"))
    data = pd.read_excel(historyDataPath, sheet_name="Bundle Reports")
    data = data.where(data.notnull(), None)
    #data.drop([0], axis = 0, inplace = True) #inplace means data = data.changed
    #data.reset_index(drop = True, inplace = True)
    data.rename(columns = {"AGGREGATION":"AGGREGATION BUNDLE"}, inplace = True)
    
    liveIDBoolSet = []
    for ID in data["AGGREGATION BUNDLE"]:
        if ID in liveID:
            liveIDBoolSet.append(True)
        else:
            liveIDBoolSet.append(False)
    data = data[liveIDBoolSet]
    data.reset_index(drop = True, inplace = True) #include live options only

    
    data["k"] = data["执行价格"]
    data["startingPrice"] = data["期初价格"]
    
    s0Set = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in todayPriceDic:
            s0Set.append(todayPriceDic[data["AGGREGATION BUNDLE"][i]])
        else:
            s0Set.append(defaultTodayPrice)
    data["s0"] = s0Set #this is the real st

    sigmaSet = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in sigmaDic:
            sigmaSet.append(sigmaDic[data["AGGREGATION BUNDLE"][i]])
        else:
            sigmaSet.append(defaultSigma)
    data["sigma"] = sigmaSet
    
    quantitySet = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in quantityDic:
            quantitySet.append(quantityDic[data["AGGREGATION BUNDLE"][i]])
        else:
            quantitySet.append(defaultQuantity)
    data["quantity"] = quantitySet
    
    buySet = []
    for i in range(len(data)):
        if data["Buy/Sell"][i] == "Buy":
            buySet.append(True)
        else:
            buySet.append(False)
    data["buy"] = buySet
    
    data["Price"] = None  #The data can be stored here later
    data["Delta"] = None
    data["Delta_Pct"] = None
    data["Gamma"] = None
    data["Gamma_Pct"] = None
    data["Theta"] = None  
    data["Theta_Pct"] = None
    data["Vega"] = None
    data["Vega_Pct"] = None
    data["PV"] = None
     #up to here, None only, no "None"
    return data

def getData(data, idToFind, ratePoints, s0Shock, sigmaShock):
    s0Shock = float(s0Shock)
    sigmaShock = float(sigmaShock)
    
    if len(data[data["AGGREGATION BUNDLE"] == idToFind].index) != 0:
        indexToFind = (data[data["AGGREGATION BUNDLE"] == idToFind].index)[0]
        dataType = data["类型"][indexToFind]
        s0IsOne = False  ############
        T = data["T"][indexToFind]
        rf = rate.getRiskFreeRate(T, ratePoints)
        dt = 1/365
        
        st = data["s0"][indexToFind]
        quantity = data["quantity"][indexToFind]
        buy = data["buy"][indexToFind]
        #computePrice(data, dataType, indexToFind, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock)
        [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp] = others.computePrice(data, dataType, indexToFind, 0, s0IsOne, rf, dt, s0Shock, sigmaShock)
        
        if price_tmp is not None and dataType != "BCALL":
            price_tmp = round(price_tmp / data["startingPrice"][indexToFind], 10)
            
        [idToFind, quantity, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, thetaExposure, theta_tmp, vegaExposure, vega_tmp, PV_tmp] = others.greeksExposure(indexToFind, data, quantity, buy, st, price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp)

        if PV_tmp is not None:
            PV_tmp = round(PV_tmp * data["startingPrice"][indexToFind], 10) ##don't forget here.
    
    else:
        st = None
        quantity = None
        buy = None
        #[price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp] = [None, None, None, None, None]
        [idToFind, quantity, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, thetaExposure, theta_tmp, vegaExposure, vega_tmp, PV_tmp] = [None, None, None, None, None, None, None, None, None, None, None, None]
    
    #no quantity
    return [[idToFind], 
        others.listFormatter([price_tmp], False), 
        others.listFormatter([deltaExposure], True), 
        others.listFormatter([delta_tmp], False), 
        others.listFormatter([gammaExposure], True), 
        others.listFormatter([gamma_tmp], False), 
        others.listFormatter([thetaExposure], True),
        others.listFormatter([theta_tmp], False),
        others.listFormatter([vegaExposure], True),
        others.listFormatter([vega_tmp], False),
        others.listFormatter([PV_tmp], True)]

def getDataWithWindID(data, windID, ratePoints, s0Shock, sigmaShock):
    s0Shock = float(s0Shock)
    sigmaShock = float(sigmaShock)
    
    indexSet = (data[data["WIND代码"] == windID].index)
    price_tmpSet = []
    deltaExposureSet = []
    delta_tmpSet = []
    gammaExposureSet = []
    gamma_tmpSet = []
    vegaExposureSet = []
    vega_tmpSet = []
    thetaExposureSet = []
    theta_tmpSet = []
    idSet = []
    PVSet = []
    for indexToFind in indexSet:
        dataType = data["类型"][indexToFind]
        s0IsOne = False  ############
        T = data["T"][indexToFind]
        rf = rate.getRiskFreeRate(T, ratePoints)
        dt = 1/365

        st = data["s0"][indexToFind]
        quantity = data["quantity"][indexToFind]
        buy = data["buy"][indexToFind]
        #computePrice(data, dataType, indexToFind, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock)
        [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp] = others.computePrice(data, dataType, indexToFind, 0, s0IsOne, rf, dt, s0Shock, sigmaShock)
        
        if price_tmp is not None and dataType != "BCALL":
            price_tmp = round(price_tmp / data["startingPrice"][indexToFind], 10) 
        
        [idToFind, quantity, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, thetaExposure, theta_tmp, vegaExposure, vega_tmp, PV_tmp] = others.greeksExposure(indexToFind, data, quantity, buy, st, price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp)

        if PV_tmp is not None:
            PV_tmp = round(PV_tmp * data["startingPrice"][indexToFind], 10)

        if price_tmp is not None:
            price_tmpSet.append(price_tmp)
            deltaExposureSet.append(deltaExposure)
            delta_tmpSet.append(delta_tmp)
            gammaExposureSet.append(gammaExposure)
            gamma_tmpSet.append(gamma_tmp)
            thetaExposureSet.append(thetaExposure)
            theta_tmpSet.append(theta_tmp)
            vegaExposureSet.append(vegaExposure)
            vega_tmpSet.append(vega_tmp)
            PVSet.append(PV_tmp)
            idSet.append(idToFind)
        
    return [idSet, 
        others.listFormatter(price_tmpSet, False), 
        others.listFormatter(deltaExposureSet, True), 
        others.listFormatter(delta_tmpSet, False), 
        others.listFormatter(gammaExposureSet, True), 
        others.listFormatter(gamma_tmpSet, False), 
        others.listFormatter(thetaExposureSet, True),
        others.listFormatter(theta_tmpSet, False),
        others.listFormatter(vegaExposureSet, True),
        others.listFormatter(vega_tmpSet, False),
        others.listFormatter(PVSet, True)]

def getBenchMarkList(data, fromID, IDOrWindID, ratePoints):
    if fromID:
        [id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, thetaExposure, theta_tmp, vegaExposure, vega_tmp, PV_tmp] = getData(data, IDOrWindID, ratePoints, 1, 1)
        convertedData = others.convertDataSet(id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, thetaExposure, theta_tmp, vegaExposure, vega_tmp, PV_tmp)
        benchMark = others.sumUpEachList(convertedData) #it is a benchmark list
    else:
        [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet] = getDataWithWindID(data, IDOrWindID, ratePoints, 1, 1)
        convertedData = others.convertDataSet(idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet)
        benchMark = others.sumUpEachList(convertedData) #it is a benchmark list
    return benchMark


def getHeatMapData(data, benchMark, printType, fromID, IDOrWindID, ratePoints):
        if printType == "Price":
            indexChosen = 1
        elif printType == "Delta":
            indexChosen = 2
        elif printType == "Delta_Pct":
            indexChosen = 3
        elif printType == "Gamma":
            indexChosen = 4
        elif printType == "Gamma_Pct":
            indexChosen = 5
        elif printType == "Theta":
            indexChosen = 6
        elif printType == "Theta_Pct":
            indexChosen = 7
        elif printType == "Vega":
            indexChosen = 8
        elif printType == "Vega_Pct":
            indexChosen = 9
        elif printType == "PV":
            indexChosen = 10
        else:
            indexChosen = 101

        if fromID is True:
            differenceList = []
            heatMapDataSet = []
            for y in range(0,11):
                for x in range(0,11):
                    # print(y,x)
                    sigmaShock = 0.95 + y * 0.01
                    s0Shock = 0.95 + x * 0.01
                    [id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, thetaExposure, theta_tmp, vegaExposure, vega_tmp, PV_tmp] = getData(data, IDOrWindID, ratePoints, s0Shock, sigmaShock)
                    convertedData = others.convertDataSet(id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, thetaExposure, theta_tmp, vegaExposure, vega_tmp, PV_tmp)
                    difference = others.sumUpEachList(convertedData)[indexChosen] - benchMark[indexChosen] #take care of the 101 case...
                    difference = others.outputFormatter(difference, (indexChosen % 2 == 0))
                    differenceList.append(difference)
                    box = [y, x, difference]
                    heatMapDataSet.append(box)
        else:
            differenceList = []
            heatMapDataSet = []
            for y in range(0,11):
                for x in range(0,11):
                    # print(y,x)
                    sigmaShock = 0.95 + y * 0.01
                    s0Shock = 0.95 + x * 0.01
                    [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet] = getDataWithWindID(data, IDOrWindID, ratePoints, s0Shock, sigmaShock)
                    convertedData = others.convertDataSet(idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet)
                    difference = others.sumUpEachList(convertedData)[indexChosen] - benchMark[indexChosen]
                    difference = others.outputFormatter(difference, (indexChosen % 2 == 0))
                    differenceList.append(difference)
                    box = [y, x, difference]
                    heatMapDataSet.append(box)

        return [heatMapDataSet, max(differenceList), min(differenceList)]

"""
def exportWholeExcel():
    return 0
"""



