#非向量化的期权定价函数，单次运行比向量化的函数效率更高，用于结构求解

from math import log, exp, erf, pi, sin

def NCD(x):#标准正太累积分布函数
    return 0.5 + erf(0.7071067811865476*x)/2.0

def adjustedBarrier(b, v, dt):#当观察频率为离散时，对障碍价格进行调整
    if b > 1:
        return b*exp(0.5826*v*dt**0.5)
    elif b < 1:
        return b*exp(-0.5826*v*dt**0.5)
    else:
        return b

def call(k, v, r, T, q = 0):#欧式看涨
    vSqrtT = v*T**0.5
    d1 = ((r - q + 0.5*v*v)*T - log(k))/vSqrtT
    return  exp(-q*T)*NCD(d1) - k*exp(-r*T)*NCD(d1 - vSqrtT)

def put(k, v, r, T, q = 0):#欧式看跌
    return call(k, v, r, T, q) + k*exp(-r*T) - exp(-q*T)

def bcall(k, v, r, T, q = 0):#二值看涨
    return exp(-r*T)*NCD(((r - q - 0.5*v*v)*T - log(k))/v/T**0.5)

def bput(k, v, r, T, q = 0):#二值看跌
    return exp(-r*T)*NCD(-((r - q - 0.5*v*v)*T - log(k))/v/T**0.5)

def bulls(k1, k2, v, r, T, q = 0):#牛市价差
    return call(k1, v, r, T, q) - call(k2, v, r, T, q)

def bears(k1, k2, v, r, T, q):#熊市价差
    return put(k2, v, r, T, q) - put(k1, v, r, T, q)

def buo(b, v, r, T, dt = 0, q = 0):
    '''
    Binary up-and-out-cash-at-expiry
    '''
    b = adjustedBarrier(b, v, dt)
    b = log(b)/v
    c = (r - q)/v - 0.5*v
    return exp(-r*T)*(NCD((b - c*T)/T**0.5) - exp(2*c*b)*NCD((- b - c*T)/T**0.5))

def bui(b, v, r, T, dt = 0, q = 0):
    '''
    Binary-up-and-in-cash-at-expiry
    '''
    return exp(-r*T) - buo(b, v, r, T, dt, q)

"""
def bdo(b, v, r, T, dt = 0, q = 0): ###It has error inside!
    '''
    Binary down-and-out-cash-at-expiry
    '''
    b = adjustedBarrier(b, v, dt)
    b = -log(b)/v
    c = (q - r)/v + 0.5*v
    return exp(-r*T)*(NCD((b - c*T)/T**0.5) - exp(2*c*b)*NCD((- b - c*T)/T**0.5))

def bdi(b, v, r, T, dt = 0, q = 0):
    '''
    Binary down-and-in-cash-at-expiry
    '''
    return exp(-r*T) - bdo(b, v, r, T, dt, q)
"""

def uoc0rb(k, b, v, r, T, dt = 0, q = 0):
    '''
    Standard up-and-out-call with no rebate.
    '''
    b = adjustedBarrier(b, v, dt)
    vSqrtT = v*T**0.5
    def dp(y):
        return (log(y) + (r - q + 0.5*v*v)*T)/vSqrtT
    def dm(y):
        return (log(y) + (r - q - 0.5*v*v)*T)/vSqrtT
    return exp(-q*T)*(NCD(dp(1/k)) - NCD(dp(1/b)) - \
           exp(-(r - q)*T)*k*(NCD(dm(1/k)) - NCD(dm(1/b))) - \
           b**(1 + 2*(r - q)/v/v)*(NCD(dp(b*b/k)) - NCD(dp(b))) + \
           exp(-(r - q)*T)*k*b**(2*(r - q)/v/v - 1)*(NCD(dm(b*b/k)) - NCD(dm(b))))

def uoc(k, b, rb, v, r, T, dt = 0, q = 0):
    #uoc是uoc0rb和bui的线性组合
    return uoc0rb(k, b, v, r, T, dt, q) + rb*bui(b, v, r, T, dt, q) #rb是绝对数但s0为1

def dop0rb(k, b, v, r, T, dt = 0, q = 0):
    '''
    Standard down-and-out-put with no rebate.
    '''
    b = adjustedBarrier(b, v, dt)
    vSqrtT = v*T**0.5
    mu = (r - q)/v/v - 0.5
    x1 = (1 + mu)*vSqrtT - log(k)/vSqrtT
    x2 = (1 + mu)*vSqrtT - log(b)/vSqrtT
    y1 = (1 + mu)*vSqrtT + log(b*b/k)/vSqrtT
    y2 = (1 + mu)*vSqrtT + log(b)/vSqrtT
    return exp(-q*T)*(NCD(x1) - NCD(x2) + b**(2*mu + 2)*(NCD(y2) - NCD(y1))) + \
           k*exp(-r*T)*(NCD(x2 - vSqrtT) - NCD(x1 - vSqrtT) + b**(2*mu)*(NCD(y1 - vSqrtT) - NCD(y2 - vSqrtT)))

#K, H, S, mu, lamb, eta, z, sigma, T
def F(k, b, v, r, T, dt = 0, q = 0):
    b = adjustedBarrier(b, v, dt)
    mu = (r-v**2/2)/v**2
    lamb = (mu**2+2*r/v**2)**0.5
    z = log(b)/(v*T**0.5)+lamb*v*T**0.5
    partA = ((b)**(mu+lamb)*NCD(z) + (b)**(mu-lamb)*NCD(z-2*lamb*v*(T)**0.5))
    return partA

def dop(k, b, rb, v, r, T, dt = 0, q = 0):
    #dop是dop0rb和bdi的线性组合
    #dop = dop0rb + F
    return dop0rb(k, b, v, r, T, dt, q) + rb * F(k, b, rb, v, r, T, dt, q)

"""
def dboc0rb(k, b1, b2, v, r, T, dt = 0, q = 0):
    '''
    Standard double-barrier-out-call with no rebate
    '''
    b1 = adjustedBarrier(b1, v, dt) #Lower
    b2 = adjustedBarrier(b2, v, dt) #Upper
    vSqrtT = v*T**0.5
    rqv = (r - q)/vSqrtT + 0.5*vSqrtT #Miss (r-q)*T?
    sum1 = sum2 = 0
    mu = 2*(r - q)/v/v + 1
    for n in range(-5, 6):
        d1 = (2*n*log(b2/b1) - log(k))/vSqrtT + rqv
        d2 = (2*n*log(b2/b1) - log(b2))/vSqrtT + rqv
        d3 = (2*log(b1) + 2*n*log(b1/b2) - log(k))/vSqrtT + rqv
        d4 = (log(b1) + (2*n + 1)*log(b1/b2))/vSqrtT + rqv
        sum1 += (b2/b1)**(n*mu)*(NCD(d1) - NCD(d2)) - b1**mu*(b1/b2)**(n*mu)*(NCD(d3) - NCD(d4))
        mu -= 2
        sum2 += (b2/b1)**(n*mu)*(NCD(d1 - vSqrtT) - NCD(d2 - vSqrtT)) - \
                 b1**mu*(b1/b2)**(n*mu)*(NCD(d3 - vSqrtT) - NCD(d4 - vSqrtT))
        mu += 2
    return exp(-q*T)*sum1 - k*exp(-r*T)*sum2
"""

def dboc0rb(k, b1, b2, v, r, T, dt = 0, q = 0):
    '''
    Standard double-barrier-out-call with no rebate
    '''
    b1 = adjustedBarrier(b1, v, dt) #Lower
    b2 = adjustedBarrier(b2, v, dt) #Upper
    vSqrtT = v*T**0.5
    rqv = (r - q)*T/vSqrtT + 0.5*vSqrtT #Miss (r-q)*T?
    sum1 = sum2 = 0
    mu1 = 2*(r - q)/v/v + 1
    mu2 = 0
    mu3 = mu1
    for n in range(-5, 6):
        d1 = (2*n*log(b2/b1) - log(k))/vSqrtT + rqv
        d2 = (2*n*log(b2/b1) - log(b2))/vSqrtT + rqv
        d3 = (2*log(b1) + 2*n*log(b1/b2) - log(k))/vSqrtT + rqv
        d4 = (2*log(b1) + 2*n*log(b1/b2) - log(b2))/vSqrtT + rqv
        sum1 = sum1 + (b2/b1)**(n*mu1)*(NCD(d1) - NCD(d2)) - b1**mu3*(b1/b2)**(n*mu3)*(NCD(d3) - NCD(d4))
        #mu -= 2
        sum2 = sum2 + (b2/b1)**(n*(mu1-2))*(NCD(d1 - vSqrtT) - NCD(d2 - vSqrtT)) - \
                 b1**(mu3-2)*(b1/b2)**(n*(mu3-2))*(NCD(d3 - vSqrtT) - NCD(d4 - vSqrtT))
        #mu += 2
    return exp(-q*T)*sum1 - k*exp(-r*T)*sum2

"""
def dbop0rb(k, b1, b2, v, r, T, dt = 0, q = 0):
    '''
    Standard double-barrier-out-put with no rebate
    bi >= 0, denotes the absolute difference between the strike and the barrier
    '''
    b1 = adjustedBarrier(b1, v, dt)
    b2 = adjustedBarrier(b2, v, dt)
    vSqrtT = v*T**0.5
    rqv = (r - q)/vSqrtT + 0.5*vSqrtT
    sum1 = sum2 = 0
    mu = 2*(r - q)/v/v + 1
    for n in range(-5, 6):
        d1 = (2*n*log(b2/b1) - log(b1))/vSqrtT + rqv
        d2 = (2*n*log(b2/b1) - log(k))/vSqrtT + rqv
        d3 = (log(b1) + 2*n*log(b1/b2))/vSqrtT + rqv
        d4 = (2*log(b1) + 2*n*log(b1/b2) - log(k))/vSqrtT + rqv
        sum1 += (b2/b1)**(n*mu)*(NCD(d1) - NCD(d2)) - b1**mu*(b1/b2)**(n*mu)*(NCD(d3) - NCD(d4))
        mu -= 2
        sum2 += (b2/b1)**(n*mu)*(NCD(d1 - vSqrtT) - NCD(d2 - vSqrtT)) - \
                 b1**mu*(b1/b2)**(n*mu)*(NCD(d3 - vSqrtT) - NCD(d4 - vSqrtT))
        mu += 2
    return k*exp(-r*T)*sum2 - exp(-q*T)*sum1
"""

def dbop0rb(k, b1, b2, v, r, T, dt = 0, q = 0):
    '''
    Standard double-barrier-out-put with no rebate
    bi >= 0, denotes the absolute difference between the strike and the barrier
    '''
    b1 = adjustedBarrier(b1, v, dt)
    b2 = adjustedBarrier(b2, v, dt)
    vSqrtT = v*T**0.5
    rqv = (r - q)*T/vSqrtT + 0.5*vSqrtT
    sum1 = sum2 = 0
    mu = 2*(r - q)/v/v + 1
    for n in range(-5, 6):
        d1 = (2*n*log(b2/b1) - log(b1))/vSqrtT + rqv
        d2 = (2*n*log(b2/b1) - log(k))/vSqrtT + rqv
        d3 = (log(b1) + 2*n*log(b1/b2))/vSqrtT + rqv
        d4 = (2*log(b1) + 2*n*log(b1/b2) - log(k))/vSqrtT + rqv
        sum1 += (b2/b1)**(n*mu)*(NCD(d1) - NCD(d2)) - b1**mu*(b1/b2)**(n*mu)*(NCD(d3) - NCD(d4))
        mu -= 2
        sum2 += (b2/b1)**(n*mu)*(NCD(d1 - vSqrtT) - NCD(d2 - vSqrtT)) - \
                 b1**mu*(b1/b2)**(n*mu)*(NCD(d3 - vSqrtT) - NCD(d4 - vSqrtT))
        mu += 2
    return k*exp(-r*T)*sum2 - exp(-q*T)*sum1

"""
#Check:
def bdbo(b1, b2, v, r, T, dt = 0, q = 0):
    '''
    Binary-double-barrier-out-cash-at-expiry
    '''
    b1 = adjustedBarrier(b1, v, dt)
    b2 = adjustedBarrier(b2, v, dt)
    z = log(b2/b1)
    alpha = 0.5 - (r - q)/v/v
    beta = -alpha*alpha - 2*r/v/v
    sign = 1
    sum1 = 0
    for i in range(1, 6):
        sum1 += 2*pi*i/z/z*(b1**(-alpha) + sign*b2**(-alpha))/(alpha*alpha + (i*pi/z)**2)* \
           sin(-i*pi*log(b1)/z)*exp(-0.5*((i*pi/z)**2 - beta)*v*v*T)
        sign *= -1
    return sum1

#Check:
def bdbi(b1, b2, v, r, T, dt = 0, q = 0):
    '''
    Binary-double-barrier-in-cash-at-expiry
    '''
    return exp(-r*T) - bdbo(b1, b2, v, r, T, dt, q)
"""

def dbudi(k, b1, b2, v, r, T, dt = 0, q = 0):
    b1 = adjustedBarrier(b1, v, dt)
    b2 = adjustedBarrier(b2, v, dt)
    alpha = -0.5*(2*(r-q)/v**2-1)
    beta = -0.25*(2*(r-q)/v**2-1)**2 - 2*r/v**2
    sum1 = 0.0
    sum2 = 0.0
    nRepeat = 1000
    z = log(b2/b1)
    for i in range(1, nRepeat+1):
        sum2 = sum1
        sum1 = sum1 + 2*pi*i* 1/z**2 * ((1/b1)**alpha - (-1)**i*(1/b2)**alpha) / (alpha**2 + (i*pi/z)**2) * sin(i*pi/z*log(1/b1)) * exp(-0.5*((i*pi/z)**2 - beta) * v**2 * T)
        if abs(sum1 - sum2) <= 0.000000000001:
            break
    return 1 * exp(-r*T) - sum1   

def dboc(k, b1, b2, rb, v, r, T, dt = 0, q = 0):
    #dboc = dboc0rb + rb * bdbi
    #dboc = dboc0rb + rb * dbudi
    return dboc0rb(k, b1, b2, v, r, T, dt, q) + rb * dbudi(k, b1, b2, v, r, T, dt, q)

def dbop(k, b1, b2, rb, v, r, T, dt = 0, q = 0):
    #dbop = dbop0rb + rb * bdbi
    #dbop = dbop0rb + rb * dbudi
    return dbop0rb(k, b1, b2, v, r, T, dt, q) + rb * dbudi(k, b1, b2, v, r, T, dt, q)

def dko(k1, k2, b1, b2, rb, v, r, T, dt = 0, q = 0):
    #dko是dboc0rb，dbop0rb和bdbi的线性组合
    return dboc0rb(k2, b1, b2, v, r, T, dt, q) + dbop0rb(k1, b1, b2, v, r, T, dt, q) + \
           rb*bdbi(b1, b2, v, r, T, dt, q)