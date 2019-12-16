#!/usr/bin/env python
# coding: utf-8


from numpy import sqrt, pi, exp, log, array, linspace
import matplotlib.pyplot as plt
from scipy import integrate
from scipy import stats
import pandas as pd

def NFunction(x):
    return integrate.quad((lambda a: 1/sqrt(2.0*pi) * exp(-1 * a ** 2 / 2.0)), -20.0, x)[0]

def callDelta(s0, k, T, rf, sigma, q):
    d1 = (log(s0 / k) + (rf - q) * T) / (sigma * sqrt(T)) + sigma * sqrt(T) / 2.0
    return exp(-1 * q * T) * NFunction(d1)

def callGamma(s0, k, T, rf, sigma, q):
    d1 = (log(s0 / k) + (rf - q) * T) / (sigma * sqrt(T)) + sigma * sqrt(T) / 2.0
    gamma = 1 / sqrt(2 * pi) * exp(-1 * q * T - 1 * d1 ** 2 / 2.0) / (sigma * sqrt(T) * s0)
    return gamma

def callVega(s0, k, T, rf, sigma, q):
    d1 = (log(s0 / k) + (rf - q) * T) / (sigma * sqrt(T)) + sigma * sqrt(T) / 2.0
    vega = exp(-1 * q * T - 1 * d1**2 / 2) * s0 * sqrt(T) / sqrt(2 * pi)
    return vega

def putDelta(s0, k, T, rf, sigma, q):
    d1 = (log(s0 / k) + (rf - q) * T) / (sigma * sqrt(T)) + sigma * sqrt(T) / 2.0
    delta = exp(-1 * q * T) * (NFunction(d1) - 1)
    return delta

def putGamma(s0, k, T, rf, sigma, q):
    d1 = (log(s0 / k) + (rf - q) * T) / (sigma * sqrt(T)) + sigma * sqrt(T) / 2.0
    gamma = 1 / sqrt(2 * pi) * exp(-1 * q * T - 1 * d1 ** 2 / 2.0) / (sigma * sqrt(T) * s0)
    return gamma

def putVega(s0, k, T, rf, sigma, q):
    d1 = (log(s0 / k) + (rf - q) * T) / (sigma * sqrt(T)) + sigma * sqrt(T) / 2.0
    vega = exp(-1 * q * T - 1 * d1**2 / 2) * s0 * sqrt(T) / sqrt(2 * pi)
    return vega

def binaryCallDelta(s0, k, T, rf, sigma, q):
    d2 = (log(s0/k) + (rf - q) * T) / (sigma * sqrt(T)) - (sigma * sqrt(T)) / 2.0
    delta = exp(-1 * rf * T) / (sqrt(2 * pi * T) * sigma * s0) * exp(-1 * d2**2 / 2)
    return delta

def binaryPutDelta(s0, k, T, rf, sigma, q):
    d2 = (log(s0/k) + (rf - q) * T) / (sigma * sqrt(T)) - (sigma * sqrt(T)) / 2.0
    delta = -1 * exp(-1 * rf * T) / (sqrt(2 * pi * T) * sigma * s0) * exp(-1 * d2**2 / 2)
    return delta






