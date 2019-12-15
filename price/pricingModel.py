#!/usr/bin/env python
# coding: utf-8


from numpy import *
from scipy import integrate
from scipy import stats
import pandas as pd
from datetime import timedelta

import optionPricingFormulas2 as opf2
import optionGreeksFormulas as ogf
import others as others


def computeCallData(vcallData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, sigma, amplifier = vcallData.loc[i, ["k", "s0", "T", "sigma", "合同参与率"]]
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
        price_tmp = (opf2.call(s0_tmp, k_tmp, sigma, rf, T_tmp) * a)
        delta_tmp = (ogf.callDelta(s0_tmp, k_tmp, T_tmp, rf, sigma) * a)
        #gamma affected by s0IsOne?
        gamma_tmp = (ogf.callGamma(s0_tmp, k_tmp, T_tmp, rf, sigma) * a)
        vega_tmp = (ogf.callVega(s0_tmp, k_tmp, T_tmp, rf, sigma) * a)

        p_tmp = opf2.call(s0_tmp, k_tmp, sigma, rf, T_tmp) * a
        pBoost_tmp = opf2.call(s0_tmp, k_tmp, sigma, rf, T_tmp*1.0001) * a
        theta_tmp = (-1 * (pBoost_tmp - p_tmp) / (T_tmp*0.0001))
    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]



def computePutData(vputData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, sigma, amplifier = vputData.loc[i, ["k", "s0", "T", "sigma", "合同参与率"]]
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
        price_tmp = (opf2.put(s0_tmp, k_tmp, sigma, rf, T_tmp) * a)
        delta_tmp = (ogf.putDelta(s0_tmp, k_tmp, T_tmp, rf, sigma) * a)
        gamma_tmp = (ogf.putGamma(s0_tmp, k_tmp, T_tmp, rf, sigma) * a)
        vega_tmp = (ogf.putVega(s0_tmp, k_tmp, T_tmp, rf, sigma) * a)

        p_tmp = opf2.put(s0_tmp, k_tmp, sigma, rf, T_tmp) * a
        pBoost_tmp = opf2.put(s0_tmp, k_tmp, sigma, rf, T_tmp*1.0001) * a
        theta_tmp = (-1 * (pBoost_tmp - p_tmp) / (T_tmp*0.0001))
    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]


def computeBCallData(bcallData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, sigma, amplifier, limit = bcallData.loc[i, ["k", "s0", "T", "sigma", "合同参与率", 
                                                                    "Digital amount"]]
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
        price_tmp = (opf2.bcall(s0_tmp, k_tmp, sigma, rf, T_tmp) * a * limit)
        delta_tmp = (ogf.binaryCallDelta(s0_tmp, k_tmp, T_tmp, rf, sigma) * a)

        pd_tmp = ogf.binaryCallDelta(s0_tmp*0.9999, k_tmp, T_tmp, rf, sigma) * a
        pdBoost_tmp = ogf.binaryCallDelta(s0_tmp*1.0001, k_tmp, T_tmp, rf, sigma) * a
        gamma_tmp = ((pdBoost_tmp - pd_tmp) / (s0_tmp*0.0002))

        p_tmp = opf2.bcall(s0_tmp, k_tmp, sigma*0.9999, rf, T_tmp) * a * limit
        pBoost_tmp = opf2.bcall(s0_tmp, k_tmp, sigma*1.0001, rf, T_tmp) * a * limit
        vega_tmp = ((pBoost_tmp - p_tmp) / (sigma*0.0002)) / limit

        p_tmp = opf2.bcall(s0_tmp, k_tmp, sigma, rf, T_tmp) * a * limit
        pBoost_tmp = opf2.bcall(s0_tmp, k_tmp, sigma, rf, T_tmp*1.0001) * a * limit
        theta_tmp = (-1 * (pBoost_tmp - p_tmp) / (T_tmp*0.0001)) / limit
    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]



def computeUOCData(uocData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, barrier_tmp, rebate_tmp, sigma, amplifier = uocData.loc[i, ["k", "s0", "T", "上障碍价格", 
                                                                           "Option Rebate", "sigma", "合同参与率"]]
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
        price_tmp = (opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a)
        #Note: uoc(rebate * s0 / s0) * s0

        p_tmp = opf2.uoc(s0_tmp*0.99, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.uoc(s0_tmp*1.01, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        delta_tmp = ((pBoost_tmp - p_tmp) / (s0_tmp*0.02))

        p_tmp = opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.uoc(s0_tmp*1.01, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pShrink_tmp = opf2.uoc(s0_tmp*0.99, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        gamma_tmp = ((pBoost_tmp + pShrink_tmp - 2*p_tmp) / ((s0_tmp*0.01)**2))

        p_tmp = opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma+0.0001, rf, T_tmp, dt) * a
        vega_tmp = ((pBoost_tmp - p_tmp) / (0.0001))

        p_tmp = opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.uoc(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp*1.0001, dt) * a
        theta_tmp = (-1 * (pBoost_tmp - p_tmp) / (T_tmp*0.0001))
    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]



def computeDOPData(dopData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, barrier_tmp, rebate_tmp, sigma, amplifier = dopData.loc[i, ["k", "s0", "T", "下障碍价格", 
                                                                           "Option Rebate", "sigma", "合同参与率"]]
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
        price_tmp = (opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a)

        p_tmp = opf2.dop(s0_tmp*0.99, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.dop(s0_tmp*1.01, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        delta_tmp = ((pBoost_tmp - p_tmp) / (s0_tmp*0.02))

        p_tmp = opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.dop(s0_tmp*1.01, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pShrink_tmp = opf2.dop(s0_tmp*0.99, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        gamma_tmp = ((pBoost_tmp + pShrink_tmp - 2*p_tmp) / ((s0_tmp*0.01)**2))

        p_tmp = opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma+ 0.0001, rf, T_tmp, dt) * a
        vega_tmp = ((pBoost_tmp - p_tmp) / (0.0001))

        p_tmp = opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.dop(s0_tmp, k_tmp, barrier_tmp, rebate_tmp, sigma, rf, T_tmp*1.0001, dt) * a
        theta_tmp = (-1 * (pBoost_tmp - p_tmp) / (T_tmp*0.0001))
    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]



def computeDBCData(dbcData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, amplifier = dbcData.loc[i, ["k", "s0", "T", "下障碍价格", 
                                                                                                     "上障碍价格", 
                                                                                                     "Option Rebate", "sigma", 
                                                                                                     "合同参与率"]]
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
        price_tmp = (opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a)

        p_tmp = opf2.dboc(s0_tmp*0.99, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.dboc(s0_tmp*1.01, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        delta_tmp = ((pBoost_tmp - p_tmp) / (s0_tmp*0.02))

        p_tmp = opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.dboc(s0_tmp*1.01, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pShrink_tmp = opf2.dboc(s0_tmp*0.99, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        gamma_tmp = ((pBoost_tmp + pShrink_tmp - 2*p_tmp) / ((s0_tmp*0.01)**2))

        p_tmp = opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a 
        pBoost_tmp = opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma+0.0001, rf, T_tmp, dt) * a
        vega_tmp = ((pBoost_tmp - p_tmp) / (0.0001))

        p_tmp = opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.dboc(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp*1.0001, dt) * a
        theta_tmp = (-1 * (pBoost_tmp - p_tmp) / (T_tmp*0.0001))
    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]



def computeDBPData(dbpData, i, timeShift, s0IsOne, rf, dt, s0Shock, sigmaShock):
    k_tmp, s0_tmp, T_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, amplifier = dbpData.loc[i, ["k", "s0", "T", 
                                                                                                     "下障碍价格", 
                                                                                                     "上障碍价格", 
                                                                                                     "Option Rebate", 
                                                                                                     "sigma", "合同参与率"]]
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
        price_tmp = (opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a)

        p_tmp = opf2.dbop(s0_tmp*0.99, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.dbop(s0_tmp*1.01, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        delta_tmp = ((pBoost_tmp - p_tmp) / (s0_tmp*0.02))

        p_tmp = opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.dbop(s0_tmp*1.01, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pShrink_tmp = opf2.dbop(s0_tmp*0.99, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        gamma_tmp = ((pBoost_tmp + pShrink_tmp - 2*p_tmp) / ((s0_tmp*0.01)**2))

        p_tmp = opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma+0.0001, rf, T_tmp, dt) * a
        vega_tmp = ((pBoost_tmp - p_tmp) / (0.0001))

        p_tmp = opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp, dt) * a
        pBoost_tmp = opf2.dbop(s0_tmp, k_tmp, barrierL_tmp, barrierU_tmp, rebate_tmp, sigma, rf, T_tmp*1.0001, dt) * a
        theta_tmp = (-1 * (pBoost_tmp - p_tmp) / (T_tmp*0.0001))
    else:
        price_tmp = None
        delta_tmp = None
        gamma_tmp = None
        vega_tmp = None
        theta_tmp = None
    return [price_tmp, delta_tmp, gamma_tmp, vega_tmp, theta_tmp]



