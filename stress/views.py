from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import xlrd as xlrd
import os, time

from price import appModel as model
from price import others as others
from price import heatMap as heatMap
# Create your views here.

@csrf_exempt
def setTodayDate(request):
  todayDate = model.getTodayDate()
  return JsonResponse({'todayDate': todayDate})

@csrf_exempt
def createTime(request):
  hTime = ''
  historyPath = os.path.abspath(os.path.join(__file__, r"../../price/data.xls"))
  if os.path.exists(historyPath): 
    historyTime = time.localtime(os.stat(historyPath).st_mtime)
    hTime = time.strftime('%Y-%m-%d %H:%M:%S', historyTime)
  return JsonResponse({'hTime': hTime})

@csrf_exempt
def uploadHistory(request):
  data = request.FILES.get('historyFile')
  file_full_path = os.path.abspath(os.path.join(__file__, r"../../price/data.xls"))
  if os.path.exists(file_full_path): 
    os.remove(file_full_path)
  dest = open(file_full_path,'wb+')
  dest.write(data.read())
  dest.close()
  res = createTime(request)
  return res

# @csrf_exempt
# def uploadSigma(request):
#   data = request.FILES.get('sigmaFiles')
#   file_full_path = os.path.abspath(os.path.join(__file__, "../sigmaData.xls"))
#   if os.path.exists(file_full_path): 
#     os.remove(file_full_path)
#   dest = open(file_full_path,'wb+')
#   dest.write(data.read())
#   dest.close()
#   res = createTime(request)
#   return res

@csrf_exempt
def computation(request):
  #params = request.body
  #print(params)
  query = json.loads(request.body)['query']
  return iDSearch(query)

def iDSearch(query):
  #######
  print("Start", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
  
  inputSearch = query['ID']
  today = query['timeShift']
  s0Shock = query['price_bump']
  sigmaShock = query['volatility_bump']
  chartType = query['type']

  om = float(query['OM'])
  tm = float(query['TM'])
  sm = float(query['SM'])
  nm = float(query['NM'])
  oy = float(query['OY'])
  sy = float(query['SY'])
  ty = float(query['TY'])
  fy = float(query['FY'])
  ratePoints = [None, om, tm, sm, nm, oy, sy, ty, fy, None]
  data = model.readData()
  data = others.setT(data,today)
  #######
  print("Read Complete", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
  benchMark = model.getBenchMarkList(False, inputSearch, ratePoints)
  [idSetBM, price_tmpSetBM, deltaExposureSetBM, delta_tmpSetBM, gammaExposureSetBM, gamma_tmpSetBM, thetaExposureSetBM, theta_tmpSetBM, vegaExposureSetBM, vega_tmpSetBM, PVSetBM] = benchMark
  
  #######
  print("BenchMark Complete", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
  [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet] = model.getDataWithSearch(data, inputSearch, ratePoints, s0Shock, sigmaShock)

  #######
  print("getData Complete", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
  sumUpList = others.sumUpEachList(others.convertDataSet(idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet))
  [idSetSum, price_tmpSetSum, deltaExposureSetSum, delta_tmpSetSum, gammaExposureSetSum, gamma_tmpSetSum, thetaExposureSetSum, theta_tmpSetSum, vegaExposureSetSum, vega_tmpSetSum, PVSetSum] = sumUpList

  #######
  print("SumUp Complete", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

  ###Change the positions
  newBenchMark = [idSetBM, PVSetBM, deltaExposureSetBM, delta_tmpSetBM, gammaExposureSetBM, gamma_tmpSetBM, thetaExposureSetBM, theta_tmpSetBM, vegaExposureSetBM, vega_tmpSetBM, price_tmpSetBM]

  findResult = [idSet, PVSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, price_tmpSet]

  newSumUpList = [idSetSum, PVSetSum, deltaExposureSetSum, delta_tmpSetSum, gammaExposureSetSum, gamma_tmpSetSum, thetaExposureSetSum, theta_tmpSetSum, vegaExposureSetSum, vega_tmpSetSum, price_tmpSetSum]

  heatMapData = model.getHeatMapData(data, benchMark, chartType, inputSearch, ratePoints)
  ######
  print("Plot Complete", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
  
  #print("findResult", findResult)

  result = {'data':findResult, 'sum': newSumUpList, 'heatMap': heatMapData, 'benchMark': newBenchMark}
  return JsonResponse(json.dumps(result), safe=False)

