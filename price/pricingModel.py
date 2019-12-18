#!/usr/bin/env python
# coding: utf-8


from numpy import sqrt, pi, exp, log, array, linspace
from scipy import integrate
from scipy import stats
import pandas as pd
from datetime import timedelta

from price import optionPricingFormulas2 as opf2
from price import optionGreeksFormulas as ogf
from price import others as others


def computeCallData(vcallData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, sigma, amplifier, windID = vcallData.loc[i, ["k", "s0", "T", "sigma", "合同参与率", "WIND代码"]]
    if windID[-2:] == "SH" or windID[-2:] == "SZ":
        q = 0
    else:
        q = rf
    sigma = sigma * sigmaShock
    s0_tmp = s0_tmp * s0Shock
    a = float(amplifier[:-1]) / 100
    a = 1  #############
    T_tmp = T_tmp - timeShift
    T_tmp = T_tmp / 365
    if s0IsOne is True:
        k_tmp = k_tmp / s0_tmp
        s0_tmp = 1.0
     
    if others.computeCondition(s0_tmp, k_tmp, sigma, T_tmp):
        price_tmp = (opf2.call(s0_tmp, k_tmp, sigma, rf, T_tmp, q) * a)
        delta_tmp = (ogf.callDelta(s0_tmp, k_tmp, T_tmp, rf, sigma, q) * a)
        #gamma affected by s0IsOne?
        gamma_tmp = (ogf.callGamma(s0_tmp, k_tmp, T_tmp, rf, sigma, q) * a)
        vega_tmp = (ogf.callVega(s0_tmp, k_tmp, T_tmp, rf, sigma, q) * a)

        if (T_tmp - 1/365) > 0:
            p_tmp = opf2.call(s0_tmp, k_tmp, sigma, rf, T_tmp, q) * a
            pBoost_tmp = opf2.call(s0_tmp, k_tmp, sigma, rf, T_tmp - 1/365, q) * a
            theta_tmp = (pBoost_tmp - p_tmp) / (1/365)
        else:
            p_tmp = opf2.call(s0_tmp, k_tmp, sigma, rf, T_tmp, q) * a
            pBoost_tmp = opf2.call(s0_tmp, k_tmp, sigma, rf, T_tmp - 0.5/365, q) * a
            theta_tmp = (pBoost_tmp - p_tmp) / (0.5/365)

    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]



def computePutData(vputData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, sigma, amplifier, windID = vputData.loc[i, ["k", "s0", "T", "sigma", "合同参与率", "WIND代码"]]
    if windID[-2:] == "SH" or windID[-2:] == "SZ":
        q = 0
    else:
        q = rf
    sigma = sigma * sigmaShock
    s0_tmp = s0_tmp * s0Shock
    a = float(amplifier[:-1]) / 100
    a = 1
    T_tmp = T_tmp - timeShift
    T_tmp = T_tmp / 365
    if s0IsOne is True:
        k_tmp = k_tmp / s0_tmp
        s0_tmp = 1.0
        
    if others.computeCondition(s0_tmp, k_tmp, sigma, T_tmp):
        price_tmp = (opf2.put(s0_tmp, k_tmp, sigma, rf, T_tmp, q) * a)
        delta_tmp = (ogf.putDelta(s0_tmp, k_tmp, T_tmp, rf, sigma, q) * a)
        gamma_tmp = (ogf.putGamma(s0_tmp, k_tmp, T_tmp, rf, sigma, q) * a)
        vega_tmp = (ogf.putVega(s0_tmp, k_tmp, T_tmp, rf, sigma, q) * a)

        if (T_tmp - 1/365) > 0:
            p_tmp = opf2.put(s0_tmp, k_tmp, sigma, rf, T_tmp, q) * a
            pBoost_tmp = opf2.put(s0_tmp, k_tmp, sigma, rf, T_tmp - 1/365, q) * a
            theta_tmp = (pBoost_tmp - p_tmp) / (1/365)
        else:
            p_tmp = opf2.put(s0_tmp, k_tmp, sigma, rf, T_tmp, q) * a
            pBoost_tmp = opf2.put(s0_tmp, k_tmp, sigma, rf, T_tmp - 0.5/365, q) * a
            theta_tmp = (pBoost_tmp - p_tmp) / (0.5/365)

    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]


def computeBCallData(bcallData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, sigma, amplifier, limit, windID = bcallData.loc[i, ["k", "s0", "T", "sigma", "合同参与率", "Digital amount", "WIND代码"]]
    if windID[-2:] == "SH" or windID[-2:] == "SZ":
        q = 0
    else:
        q = rf                                                                    
    sigma = sigma * sigmaShock
    s0_tmp = s0_tmp * s0Shock
    limit = float(limit[:-1]) / 100
    a = float(amplifier[:-1]) / 100
    a = 1
    T_tmp = T_tmp - timeShift
    T_tmp = T_tmp / 365
    if s0IsOne is True:
        k_tmp = k_tmp / s0_tmp
        s0_tmp = 1.0
        
    if others.computeCondition(s0_tmp, k_tmp, sigma, T_tmp):
        price_tmp = (opf2.bcall(s0_tmp, k_tmp, sigma, rf, T_tmp, q) * a * limit)
        delta_tmp = (ogf.binaryCallDelta(s0_tmp, k_tmp, T_tmp, rf, sigma, q) * a)

        pd_tmp = ogf.binaryCallDelta(s0_tmp*0.9999, k_tmp, T_tmp, rf, sigma, q) * a
        pdBoost_tmp = ogf.binaryCallDelta(s0_tmp*1.0001, k_tmp, T_tmp, rf, sigma, q) * a
        gamma_tmp = ((pdBoost_tmp - pd_tmp) / (s0_tmp*0.0002))

        p_tmp = opf2.bcall(s0_tmp, k_tmp, sigma, rf, T_tmp, q) * a * limit
        pBoost_tmp = opf2.bcall(s0_tmp, k_tmp, sigma+0.01, rf, T_tmp, q) * a * limit
        vega_tmp = ((pBoost_tmp - p_tmp) / (0.01)) / limit

        if (T_tmp - 1/365) > 0:
            p_tmp = opf2.bcall(s0_tmp, k_tmp, sigma, rf, T_tmp, q) * a * limit
            pBoost_tmp = opf2.bcall(s0_tmp, k_tmp, sigma, rf, T_tmp - 1/365, q) * a * limit
            theta_tmp = ((pBoost_tmp - p_tmp) / (1/365)) / limit
        else:
            p_tmp = opf2.bcall(s0_tmp, k_tmp, sigma, rf, T_tmp, q) * a * limit
            pBoost_tmp = opf2.bcall(s0_tmp, k_tmp, sigma, rf, T_tmp - 0.5/365, q) * a * limit
            theta_tmp = ((pBoost_tmp - p_tmp) / (0.5/365)) / limit

    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]



def computeUOCData(uocData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, barrier_tmp, rebate_tmp, sigma, amplifier, windID = uocData.loc[i, ["k", "s0", "T", "上障碍价格", "Option Rebate", "sigma", "合同参与率", "WIND代码"]]
    if windID[-2:] == "SH" or windID[-2:] == "SZ":
        q = 0
    else:
        q = rf
    sigma = sigma * sigmaShock
    s0_tmp = s0_tmp * s0Shock
    a = float(amplifier[:-1]) / 100
    a = 1
    T_tmp = T_tmp - timeShift
    T_tmp = T_tmp / 365
    rebate_tmp = rebate_tmp * uocData["startingPrice"][i] / a
    if s0IsOne is True:
        k_tmp = k_tmp / s0_tmp
        barrier_tmp = barrier_tmp / s0_tmp
        rebate_tmp = rebate_tmp / s0_tmp
        s0_tmp = 1.0
    
    if others.computeCondition(s0_tmp, k_tmp, sigma, T_tmp):
        price_tmp = (opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a)
        #Note: uoc(rebate * s0 / s0) * s0

        p_tmp = opf2.uoc(s0_tmp*0.99, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pBoost_tmp = opf2.uoc(s0_tmp*1.01, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        delta_tmp = ((pBoost_tmp - p_tmp) / (s0_tmp*0.02))

        p_tmp = opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pBoost_tmp = opf2.uoc(s0_tmp*1.01, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        #print("Up: ", pBoost_tmp)
        pShrink_tmp = opf2.uoc(s0_tmp*0.99, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        #print("Down: ", pShrink_tmp)
        gamma_tmp = ((pBoost_tmp + pShrink_tmp - 2*p_tmp) / ((s0_tmp*0.01)**2))

        p_tmp = opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pBoost_tmp = opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma+0.01, rf, T_tmp, dt, q) * a
        #print("Sigma Up: ", pBoost_tmp)
        vega_tmp = ((pBoost_tmp - p_tmp) / (0.01))

        if (T_tmp - 1/365) > 0:
            p_tmp = opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
            pBoost_tmp = opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp - 1/365, dt, q) * a
            #print("t - 1: ", pBoost_tmp)
            theta_tmp = (pBoost_tmp - p_tmp) / (1/365)
        else:
            p_tmp = opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
            pBoost_tmp = opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp - 0.5/365, dt, q) * a
            #print("t - 1: ", pBoost_tmp)
            theta_tmp = (pBoost_tmp - p_tmp) / (0.5/365)

    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]



def computeDOPData(dopData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, barrier_tmp, rebate_tmp, sigma, amplifier, windID = dopData.loc[i, ["k", "s0", "T", "下障碍价格", "Option Rebate", "sigma", "合同参与率", "WIND代码"]]
    if windID[-2:] == "SH" or windID[-2:] == "SZ":
        q = 0
    else:
        q = rf
    sigma = sigma * sigmaShock
    s0_tmp = s0_tmp * s0Shock
    a = float(amplifier[:-1]) / 100
    a = 1
    T_tmp = T_tmp - timeShift
    T_tmp = T_tmp / 365
    rebate_tmp = rebate_tmp * dopData["startingPrice"][i] / a
    if s0IsOne is True:
        k_tmp = k_tmp / s0_tmp
        barrier_tmp = barrier_tmp / s0_tmp
        rebate_tmp = rebate_tmp / s0_tmp
        s0_tmp = 1.0
    
    if others.computeCondition(s0_tmp, k_tmp, sigma, T_tmp):
        price_tmp = (opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a)

        p_tmp = opf2.dop(s0_tmp*0.99, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pBoost_tmp = opf2.dop(s0_tmp*1.01, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        delta_tmp = ((pBoost_tmp - p_tmp) / (s0_tmp*0.02))

        p_tmp = opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pBoost_tmp = opf2.dop(s0_tmp*1.01, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pShrink_tmp = opf2.dop(s0_tmp*0.99, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        gamma_tmp = ((pBoost_tmp + pShrink_tmp - 2*p_tmp) / ((s0_tmp*0.01)**2))

        p_tmp = opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pBoost_tmp = opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma+0.01, rf, T_tmp, dt, q) * a
        vega_tmp = ((pBoost_tmp - p_tmp) / (0.01))

        if (T_tmp - 1/365) > 0:
            p_tmp = opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
            pBoost_tmp = opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp - 1/365, dt, q) * a
            theta_tmp = (pBoost_tmp - p_tmp) / (1/365)
        else:
            p_tmp = opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
            pBoost_tmp = opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp - 0.5/365, dt, q) * a
            theta_tmp = (pBoost_tmp - p_tmp) / (0.5/365)

    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]



def computeDBCData(dbcData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, amplifier, windID = dbcData.loc[i, ["k", "s0", "T", "下障碍价格", "上障碍价格", "Option Rebate", "sigma", "合同参与率", "WIND代码"]]
    if windID[-2:] == "SH" or windID[-2:] == "SZ":
        q = 0
    else:
        q = rf
    sigma = sigma * sigmaShock
    s0_tmp = s0_tmp * s0Shock
    a = float(amplifier[:-1]) / 100
    a = 1
    T_tmp = T_tmp - timeShift
    T_tmp = T_tmp / 365
    rebate_tmp = rebate_tmp * dbcData["startingPrice"][i] / a
    if s0IsOne is True:
        k_tmp = k_tmp / s0_tmp
        barrierL_tmp = barrierL_tmp / s0_tmp
        barrierU_tmp = barrierU_tmp / s0_tmp
        rebate_tmp = rebate_tmp / s0_tmp
        s0_tmp = 1.0
    
    if others.computeCondition(s0_tmp, k_tmp, sigma, T_tmp):
        price_tmp = (opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a)

        p_tmp = opf2.dboc(s0_tmp*0.99, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pBoost_tmp = opf2.dboc(s0_tmp*1.01, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        delta_tmp = ((pBoost_tmp - p_tmp) / (s0_tmp*0.02))

        p_tmp = opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pBoost_tmp = opf2.dboc(s0_tmp*1.01, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pShrink_tmp = opf2.dboc(s0_tmp*0.99, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        gamma_tmp = ((pBoost_tmp + pShrink_tmp - 2*p_tmp) / ((s0_tmp*0.01)**2))

        p_tmp = opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a 
        pBoost_tmp = opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma+0.01, rf, T_tmp, dt, q) * a
        vega_tmp = ((pBoost_tmp - p_tmp) / (0.01))

        if (T_tmp - 1/365) > 0:
            p_tmp = opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
            pBoost_tmp = opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp - 1/365, dt, q) * a
            theta_tmp = (pBoost_tmp - p_tmp) / (1/365)
        else:
            p_tmp = opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
            pBoost_tmp = opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp - 0.5/365, dt, q) * a
            theta_tmp = (pBoost_tmp - p_tmp) / (0.5/365)

    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]



def computeDBPData(dbpData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, amplifier, windID = dbpData.loc[i, ["k", "s0", "T",  "下障碍价格",  "上障碍价格", "Option Rebate", "sigma", "合同参与率", "WIND代码"]]
    if windID[-2:] == "SH" or windID[-2:] == "SZ":
        q = 0
    else:
        q = rf
    sigma = sigma * sigmaShock
    s0_tmp = s0_tmp * s0Shock
    a = float(amplifier[:-1]) / 100
    a = 1
    T_tmp = T_tmp - timeShift
    T_tmp = T_tmp / 365
    rebate_tmp = rebate_tmp * dbpData["startingPrice"][i] / a
    if s0IsOne is True:
        k_tmp = k_tmp / s0_tmp
        barrierL_tmp = barrierL_tmp / s0_tmp
        barrierU_tmp = barrierU_tmp / s0_tmp
        rebate_tmp = rebate_tmp / s0_tmp
        s0_tmp = 1.0
        
    if others.computeCondition(s0_tmp, k_tmp, sigma, T_tmp):
        price_tmp = (opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a)

        p_tmp = opf2.dbop(s0_tmp*0.99, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pBoost_tmp = opf2.dbop(s0_tmp*1.01, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        delta_tmp = ((pBoost_tmp - p_tmp) / (s0_tmp*0.02))

        p_tmp = opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pBoost_tmp = opf2.dbop(s0_tmp*1.01, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pShrink_tmp = opf2.dbop(s0_tmp*0.99, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        gamma_tmp = ((pBoost_tmp + pShrink_tmp - 2*p_tmp) / ((s0_tmp*0.01)**2))

        p_tmp = opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
        pBoost_tmp = opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma+0.01, rf, T_tmp, dt, q) * a
        vega_tmp = ((pBoost_tmp - p_tmp) / (0.01))

        if (T_tmp - 1/365) > 0:
            p_tmp = opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
            pBoost_tmp = opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp - 1/365, dt, q) * a
            theta_tmp = (pBoost_tmp - p_tmp) / (1/365)
        else:
            p_tmp = opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt, q) * a
            pBoost_tmp = opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp - 0.5/365, dt, q) * a
            theta_tmp = (pBoost_tmp - p_tmp) / (0.5/365)

    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]



