#!/usr/bin/env python
# coding: utf-8

from multiprocessing import Pool, Manager
from numpy import sqrt, pi, exp, log, array, linspace
import matplotlib.pyplot as plt
from scipy import integrate
from scipy import stats
import pandas as pd
import os
import time

from datetime import datetime, timedelta

from price import pricingModel as pm
from price import others as others
from price import riskFreeRate as rate
from price import getDataBoosted

def getTodayDate():
    todayPath = os.path.abspath(os.path.join(__file__, "../data.xls"))
    try:
        todayData = pd.read_excel(todayPath, sheet_name="当日交易")
        today = todayData.columns[1]
        if type(today) == type("string"):
            today = datetime.strptime(today, '%Y/%m/%d')
    except:
        today = datetime.strptime("2017/07/01", '%Y/%m/%d')
        print("Error occurs while getTodayDate()")
    return (str(today.year) + "-" + str(today.month) + "-" + str(today.day))
    

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

    #For the benchmark
    PriceDic = {}
    DELTADic = {}
    DELTA_PCTDic = {}
    GAMMADic = {}
    GAMMA_PCTDic = {}
    THETADic = {}
    THETA_PCTDic = {}
    VEGADic = {}
    VEGA_PCTDic = {}
    PVDic = {}
    
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

            if sigmaData["Price"][i] is not None:
                PriceDic[sigmaData["Unnamed: 1"][i].split()[-1]] = sigmaData["Price"][i]
            else:
                PriceDic[sigmaData["Unnamed: 1"][i].split()[-1]] = None #None for the default
            
            if sigmaData["DELTA"][i] is not None:
                DELTADic[sigmaData["Unnamed: 1"][i].split()[-1]] = sigmaData["DELTA"][i]
            else:
                DELTADic[sigmaData["Unnamed: 1"][i].split()[-1]] = None
            
            if sigmaData["DELTA_PCT"][i] is not None:
                DELTA_PCTDic[sigmaData["Unnamed: 1"][i].split()[-1]] = sigmaData["DELTA_PCT"][i]
            else:
                DELTA_PCTDic[sigmaData["Unnamed: 1"][i].split()[-1]] = None
            
            if sigmaData["GAMMA"][i] is not None:
                GAMMADic[sigmaData["Unnamed: 1"][i].split()[-1]] = sigmaData["GAMMA"][i]
            else:
                GAMMADic[sigmaData["Unnamed: 1"][i].split()[-1]] = None
            
            if sigmaData["GAMMA_PCT"][i] is not None:
                GAMMA_PCTDic[sigmaData["Unnamed: 1"][i].split()[-1]] = sigmaData["GAMMA_PCT"][i]
            else:
                GAMMA_PCTDic[sigmaData["Unnamed: 1"][i].split()[-1]] = None
            
            if sigmaData["THETA"][i] is not None:
                THETADic[sigmaData["Unnamed: 1"][i].split()[-1]] = sigmaData["THETA"][i]
            else:
                THETADic[sigmaData["Unnamed: 1"][i].split()[-1]] = None
            
            if sigmaData["THETA_PCT"][i] is not None:
                THETA_PCTDic[sigmaData["Unnamed: 1"][i].split()[-1]] = sigmaData["THETA_PCT"][i]
            else:
                THETA_PCTDic[sigmaData["Unnamed: 1"][i].split()[-1]] = None
            
            if sigmaData["VEGA"][i] is not None:
                VEGADic[sigmaData["Unnamed: 1"][i].split()[-1]] = sigmaData["VEGA"][i]
            else:
                VEGADic[sigmaData["Unnamed: 1"][i].split()[-1]] = None
            
            if sigmaData["VEGA_PCT"][i] is not None:
                VEGA_PCTDic[sigmaData["Unnamed: 1"][i].split()[-1]] = sigmaData["VEGA_PCT"][i]
            else:
                VEGA_PCTDic[sigmaData["Unnamed: 1"][i].split()[-1]] = None
            
            if sigmaData["PV"][i] is not None:
                PVDic[sigmaData["Unnamed: 1"][i].split()[-1]] = sigmaData["PV"][i]
            else:
                PVDic[sigmaData["Unnamed: 1"][i].split()[-1]] = None


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

    PriceSet = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in PriceDic:
            PriceSet.append(PriceDic[data["AGGREGATION BUNDLE"][i]])
        else:
            PriceSet.append(None)
    data["Price"] = PriceSet

    DELTASet = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in DELTADic:
            DELTASet.append(DELTADic[data["AGGREGATION BUNDLE"][i]])
        else:
            DELTASet.append(None)
    data["DELTA"] = DELTASet

    DELTA_PCTSet = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in DELTA_PCTDic:
            DELTA_PCTSet.append(DELTA_PCTDic[data["AGGREGATION BUNDLE"][i]])
        else:
            DELTA_PCTSet.append(None)
    data["DELTA_PCT"] = DELTA_PCTSet

    GAMMASet = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in GAMMADic:
            GAMMASet.append(GAMMADic[data["AGGREGATION BUNDLE"][i]])
        else:
            GAMMASet.append(None)
    data["GAMMA"] = GAMMASet

    GAMMA_PCTSet = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in GAMMA_PCTDic:
            GAMMA_PCTSet.append(GAMMA_PCTDic[data["AGGREGATION BUNDLE"][i]])
        else:
            GAMMA_PCTSet.append(None)
    data["GAMMA_PCT"] = GAMMA_PCTSet

    THETASet = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in THETADic:
            THETASet.append(THETADic[data["AGGREGATION BUNDLE"][i]])
        else:
            THETASet.append(None)
    data["THETA"] = THETASet

    THETA_PCTSet = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in THETA_PCTDic:
            THETA_PCTSet.append(THETA_PCTDic[data["AGGREGATION BUNDLE"][i]])
        else:
            THETA_PCTSet.append(None)
    data["THETA_PCT"] = THETA_PCTSet

    VEGASet = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in VEGADic:
            VEGASet.append(VEGADic[data["AGGREGATION BUNDLE"][i]])
        else:
            VEGASet.append(None)
    data["VEGA"] = VEGASet

    VEGA_PCTSet = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in VEGA_PCTDic:
            VEGA_PCTSet.append(VEGA_PCTDic[data["AGGREGATION BUNDLE"][i]])
        else:
            VEGA_PCTSet.append(None)
    data["VEGA_PCT"] = VEGA_PCTSet

    PVSet = []
    for i in range(len(data)):
        if data["AGGREGATION BUNDLE"][i] in PVDic:
            PVSet.append(PVDic[data["AGGREGATION BUNDLE"][i]])
        else:
            PVSet.append(None)
    data["PV"] = PVSet
    
    buySet = []
    for i in range(len(data)):
        if data["Buy/Sell"][i] == "Buy":
            buySet.append(True)
        else:
            buySet.append(False)
    data["buy"] = buySet
    
     #up to here, None only, no "None"
    return data

def searchForIndexSet(data, inputSearch):
    originalInputSet = inputSearch.split(",")
    inputSet = []
    for item in originalInputSet:
        inputSet.append(item.strip())

    typeSet = ["VCALL", "VPUT", "BCALL", "UOC", "DOP", "DBC", "DBP"]
    typeList = []
    for item in inputSet:
        if item in typeSet:
            typeList.append(item)
    if len(typeList) == 0:
        typeList = typeSet
    
    if "all" in inputSet:
        indexSet = list(range(len(data)))
    else:
        indexSet = []
        for inputString in inputSet:
            if len(inputString) == 8 and inputString.isdigit():
                for element in data[data["AGGREGATION BUNDLE"] == inputString].index:
                    indexSet.append(element)
            else:
                for element in data[data["WIND代码"] == inputString].index:
                    indexSet.append(element)
                for element in data[data["Internal Reference"] == inputString].index:
                    if data["Book"][element] == "GFS 广发-股销-股销1-客户":
                        indexSet.append(element)
    
    removedDuplicateSet = []
    for index in indexSet:
        if index not in removedDuplicateSet:
            removedDuplicateSet.append(index)

    includedIndexSet = []
    for index in removedDuplicateSet:
        ####To be expanded later...
        if data["类型"][index] is not None and data["类型"][index] in typeList:
            includedIndexSet.append(index)
    
    return includedIndexSet

def getDataWithSearch(data, indexSet, ratePoints, s0Shock, sigmaShock):
    s0Shock = float(s0Shock)
    sigmaShock = float(sigmaShock)
    
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

        #########
        ##price_tmp is None means compute error like T < 0
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

def getBenchMarkList(indexSet): #just from the Excel
    data = readData() #No T data
    today = getTodayDate()

    idSet = []
    price_tmpSet = []
    deltaExposureSet = []
    delta_tmpSet = []
    gammaExposureSet = []
    gamma_tmpSet = []
    thetaExposureSet = []
    theta_tmpSet = []
    vegaExposureSet = []
    vega_tmpSet = []
    PVSet = []

    for index in indexSet:
        if data["AGGREGATION BUNDLE"][index] is not None:
            idSet.append(data["AGGREGATION BUNDLE"][index])
        else:
            idSet.append(None)

        if data["Price"][index] is not None:
            price_tmpSet.append(data["Price"][index])
        else:
            price_tmpSet.append(0)

        if data["DELTA"][index] is not None:
            deltaExposureSet.append(data["DELTA"][index])
        else:
            deltaExposureSet.append(0)

        if data["DELTA_PCT"][index] is not None:
            delta_tmpSet.append(data["DELTA_PCT"][index])
        else:
            delta_tmpSet.append(0)

        if data["GAMMA"][index] is not None:
            gammaExposureSet.append(data["GAMMA"][index])
        else:
            gammaExposureSet.append(0)

        if data["GAMMA_PCT"][index] is not None:
            gamma_tmpSet.append(data["GAMMA_PCT"][index])
        else:
            gamma_tmpSet.append(0)

        if data["THETA"][index] is not None:
            thetaExposureSet.append(data["THETA"][index])
        else:
            thetaExposureSet.append(0)

        if data["THETA_PCT"][index] is not None:
            theta_tmpSet.append(data["THETA_PCT"][index])
        else:
            theta_tmpSet.append(0)

        if data["VEGA"][index] is not None:
            vegaExposureSet.append(data["VEGA"][index])
        else:
            vegaExposureSet.append(0)

        if data["VEGA_PCT"][index] is not None:
            vega_tmpSet.append(data["VEGA_PCT"][index])
        else:
            vega_tmpSet.append(0)

        if data["PV"][index] is not None:
            PVSet.append(data["PV"][index])
        else:
            PVSet.append(0)

    price_tmpSet = others.listFormatter(price_tmpSet, False)
    deltaExposureSet = others.listFormatter(deltaExposureSet, True)
    delta_tmpSet = others.listFormatter(delta_tmpSet, False)
    gammaExposureSet = others.listFormatter(gammaExposureSet, True)
    gamma_tmpSet = others.listFormatter(gamma_tmpSet, False) 
    thetaExposureSet = others.listFormatter(thetaExposureSet, True)
    theta_tmpSet = others.listFormatter(theta_tmpSet, False)
    vegaExposureSet = others.listFormatter(vegaExposureSet, True)
    vega_tmpSet = others.listFormatter(vega_tmpSet, False)
    PVSet = others.listFormatter(PVSet, True)

    convertedData = others.convertDataSet(idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet)
    benchMark = others.sumUpEachList(convertedData) #it is a benchmark list
    benchMark[0] = today #Set the ID to be today's string
    return benchMark

def getHeatMapData(data, benchMark, printType, indexSet, ratePoints):
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

    differenceList = []
    heatMapDataSet = []

    if __name__ == "price.appModel": ######################
        manager = Manager()
        return_dict = manager.dict()
        pool = Pool(os.cpu_count())
        sigmaShockList = []
        s0ShockList = []
        
        for y in range(0,11):
            for x in range(0,11):
                # print(y,x)
                sigmaShockList.append(0.95 + y * 0.01)
                s0ShockList.append(0.95 + x * 0.01)

        for i in range(121):
            pool.apply_async(getDataBoosted.getDataBoosted, (i, data, indexSet, ratePoints, s0ShockList[i], sigmaShockList[i], return_dict,))
            #print(i)
        
        pool.close()
        pool.join()
        pool.terminate()

        i = -1
        for y in range(0,11):
            for x in range(0,11):
                i = i + 1
                difference = others.sumUpEachList(return_dict[i])[indexChosen] - benchMark[indexChosen]
                difference = others.outputFormatter(difference, (indexChosen % 2 == 0))
                differenceList.append(difference)
                box = [y, x, difference]
                heatMapDataSet.append(box)

        return [heatMapDataSet, max(differenceList), min(differenceList)]
    
    else:
        print("Process Error!!!")
        return [[], 0, 0]




"""
def exportWholeExcel():
    return 0
"""



