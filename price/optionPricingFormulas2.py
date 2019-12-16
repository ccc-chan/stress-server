#!/usr/bin/env python
# coding: utf-8

#Note: all s0 and T here corresponds to st and t

from math import log, exp, erf, pi, sin
from price import optionPricingFormulas as opf

def call(s0, k, v, r, T, q = 0):#欧式看涨
    return opf.call(k/s0, v, r, T, q) * s0

def put(s0, k, v, r, T, q = 0):#欧式看跌
    return opf.put(k/s0, v, r, T, q) * s0

def bcall(s0, k, v, r, T, q = 0):#二值看涨
    return opf.bcall(k/s0, v, r, T, q)

def uoc0rb(s0, k, b, v, r, T, dt = 0, q = 0):
    return opf.uoc0rb(k/s0, b/s0, v, r, T, dt, q) * s0

def bui(s0, b, v, r, T, dt = 0, q = 0):
    return opf.bui(b/s0, v, r, T, dt, q)

def uoc(s0, k, b, rb, v, r, T, dt = 0, q = 0):
    #uoc是uoc0rb和bui的线性组合
    return uoc0rb(s0, k, b, v, r, T, dt, q) + rb*bui(s0, b, v, r, T, dt, q) #rb是绝对数

def dop0rb(s0, k, b, v, r, T, dt = 0, q = 0):
    return opf.dop0rb(k/s0, b/s0, v, r, T, dt, q) * s0

def F(s0, k, b, v, r, T, dt = 0, q = 0):
    return opf.F(k/s0, b/s0, v, r, T, dt, q)

def dop(s0, k, b, rb, v, r, T, dt = 0, q = 0):
    #dop是dop0rb和bdi的线性组合
    return dop0rb(s0, k, b, v, r, T, dt, q) + rb * F(s0, k, b, v, r, T, dt, q)

def dboc0rb(s0, k, b1, b2, v, r, T, dt = 0, q = 0):
    return opf.dboc0rb(k/s0, b1/s0, b2/s0, v, r, T, dt, q) * s0

def dbop0rb(s0, k, b1, b2, v, r, T, dt = 0, q = 0):
    return opf.dbop0rb(k/s0, b1/s0, b2/s0, v, r, T, dt, q) * s0

def dbudi(s0, k, b1, b2, v, r, T, dt = 0, q = 0):
    return opf.dbudi(k/s0, b1/s0, b2/s0, v, r, T, dt, q)

def dboc(s0, k, b1, b2, rb, v, r, T, dt = 0, q = 0):
    #dboc = dboc0rb + rb * dbudi
    return dboc0rb(s0, k, b1, b2, v, r, T, dt, q) + rb * dbudi(s0, k, b1, b2, v, r, T, dt, q)

def dbop(s0, k, b1, b2, rb, v, r, T, dt = 0, q = 0):
    #dbop = dbop0rb + rb * dbudi
    return dbop0rb(s0, k, b1, b2, v, r, T, dt, q) + rb * dbudi(s0, k, b1, b2, v, r, T, dt, q)


