#!/usr/bin/env python
# coding: utf-8


from numpy import sqrt, pi, exp, log, array, linspace
import matplotlib.pyplot as plt
from scipy import integrate
from scipy import stats
import pandas as pd


def getRiskFreeRate(T, ratePoints):
    ONPoint = ratePoints[0]
    oneMonthPoint = ratePoints[1]
    threeMonthPoint = ratePoints[2]
    sixMonthPoint = ratePoints[3]
    nineMonthPoint = ratePoints[4]
    oneYearPoint = ratePoints[5]
    twoYearPoint = ratePoints[6]
    threeYearPoint = ratePoints[7]
    fourYearPoint = ratePoints[8]
    fiveYearPoint = ratePoints[9]
    
    if ONPoint is None:
        ONPoint = oneMonthPoint
    if fiveYearPoint is None:
        fiveYearPoint = fourYearPoint
    
    if T <= 1:
        return ONPoint
    elif T > 1 and T <= 31:
        return (T - 1) * (oneMonthPoint - ONPoint) / 30.0 + ONPoint 
    elif T > 31 and T <= 95:
        return (T - 31) * (threeMonthPoint - oneMonthPoint) / 64.0 + oneMonthPoint 
    elif T > 95 and T <= 185:
        return (T - 95) * (sixMonthPoint - threeMonthPoint) / 90.0 + threeMonthPoint
    elif T > 185 and T <= 276:
        return (T - 185) * (nineMonthPoint - sixMonthPoint) / 91.0 + sixMonthPoint
    elif T > 276 and T <= 367:
        return (T - 276) * (oneYearPoint - nineMonthPoint) / 91.0 + nineMonthPoint
    elif T > 367 and T <= 731:
        return (T - 367) * (twoYearPoint - oneYearPoint) / 364.0 + oneYearPoint
    elif T > 731 and T <= 1096:
        return (T - 731) * (threeYearPoint - twoYearPoint) / 365.0 + twoYearPoint
    elif T > 1096 and T <= 1461:
        return (T - 1096) * (fourYearPoint - threeYearPoint) / 365.0 + threeYearPoint
    elif T > 1461 and T <= 1827:
        return (T - 1461) * (fiveYearPoint - fourYearPoint) / 366.0 + fourYearPoint
    else:
        return fiveYearPoint


