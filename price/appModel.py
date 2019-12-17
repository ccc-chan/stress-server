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
    sigmaDataPath = os.path.abspath(os.path.join(__file__, "../sigmaData.xls"))
    sigmaData = pd.read_excel(sigmaDataPath)
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


    historyDataPath = os.path.abspath(os.path.join(__file__, "../historyData.xls"))
    data = pd.read_excel(historyDataPath)
    data = data.where(data.notnull(), None)
    data.drop([0], axis = 0, inplace = True) #inplace means data = data.changed
    data.reset_index(drop = True, inplace = True)
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
            
        [idToFind, quantity, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, vegaExposure, vega_tmp, thetaExposure, theta_tmp] = others.greeksExposure(indexToFind, data, quantity, buy, st, price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp)
    
    else:
        st = None
        quantity = None
        buy = None
        #[price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp] = [None, None, None, None, None]
        [idToFind, quantity, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, vegaExposure, vega_tmp, thetaExposure, theta_tmp] = [None, None, None, None, None, None, None, None, None, None, None]
    
    #no quantity
    return [[idToFind], [price_tmp], [deltaExposure], [delta_tmp], [gammaExposure], [gamma_tmp], [vegaExposure], [vega_tmp], [thetaExposure], [theta_tmp]]

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
        
        [idToFind, quantity, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, vegaExposure, vega_tmp, thetaExposure, theta_tmp] = others.greeksExposure(indexToFind, data, quantity, buy, st, price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp)

        price_tmpSet.append(price_tmp)
        deltaExposureSet.append(deltaExposure)
        delta_tmpSet.append(delta_tmp)
        gammaExposureSet.append(gammaExposure)
        gamma_tmpSet.append(gamma_tmp)
        vegaExposureSet.append(vegaExposure)
        vega_tmpSet.append(vega_tmp)
        thetaExposureSet.append(thetaExposure) 
        theta_tmpSet.append(theta_tmp)
        idSet.append(idToFind)
        
    return [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, vegaExposureSet, vega_tmpSet, thetaExposureSet, theta_tmpSet]

def getHeatMapData(data, printType, fromID, IDOrWindID, ratePoints):
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
        elif printType == "Vega":
            indexChosen = 6
        elif printType == "Vega_Pct":
            indexChosen = 7
        elif printType == "Theta":
            indexChosen = 8
        elif printType == "Theta_Pct":
            indexChosen = 9
        else:
            indexChosen = 0

        if fromID is True:
            [id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, vegaExposure, vega_tmp, thetaExposure, theta_tmp] = getData(data, IDOrWindID, ratePoints, 1, 1)
            convertedData = others.convertDataSet(id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, vegaExposure, vega_tmp, thetaExposure, theta_tmp)
            benchMark = others.sumUpEachList(convertedData) #it is a benchmark list

            heatMapDataSet = []
            for y in range(0,11):
                for x in range(0,11):
                    # print(y,x)
                    sigmaShock = 0.95 + y * 0.01
                    s0Shock = 0.95 + x * 0.01
                    [id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, vegaExposure, vega_tmp, thetaExposure, theta_tmp] = getData(data, IDOrWindID, ratePoints, s0Shock, sigmaShock)
                    convertedData = others.convertDataSet(id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, vegaExposure, vega_tmp, thetaExposure, theta_tmp)
                    difference = others.sumUpEachList(convertedData)[indexChosen] - benchMark[indexChosen] #take care of the 0 case...
                    box = [y, x, difference]
                    heatMapDataSet.append(box)
        else:
            [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, vegaExposureSet, vega_tmpSet, thetaExposureSet, theta_tmpSet] = getDataWithWindID(data, IDOrWindID, ratePoints, 1, 1)
            convertedData = others.convertDataSet(idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, vegaExposureSet, vega_tmpSet, thetaExposureSet, theta_tmpSet)
            benchMark = others.sumUpEachList(convertedData) #it is a benchmark list

            heatMapDataSet = []
            for y in range(0,11):
                for x in range(0,11):
                    # print(y,x)
                    sigmaShock = 0.95 + y * 0.01
                    s0Shock = 0.95 + x * 0.01
                    [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, vegaExposureSet, vega_tmpSet, thetaExposureSet, theta_tmpSet] = getDataWithWindID(data, IDOrWindID, ratePoints, s0Shock, sigmaShock)
                    convertedData = others.convertDataSet(idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, vegaExposureSet, vega_tmpSet, thetaExposureSet, theta_tmpSet)
                    difference = others.sumUpEachList(convertedData)[indexChosen] - benchMark[indexChosen]
                    box = [y, x, difference]
                    heatMapDataSet.append(box)

        return heatMapDataSet

"""
def exportWholeExcel():
    return 0
"""



