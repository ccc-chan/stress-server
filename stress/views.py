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
  idToFind = query['ID']
  if others.isNormalID(idToFind):
    return idSearch(query)
  else:
    return windIDSearch(query)

def idSearch(query):
  idToFind = query['ID']
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
  #print(ratePoints)
  data = model.readData()
  data = others.setT(data,today)
  benchMark = model.getBenchMarkList(True, idToFind, ratePoints)
  [idBM, priceBM, deltaExposureBM, deltaBM, gammaExposureBM, gammaBM, thetaExposureBM, thetaBM, vegaExposureBM, vegaBM, PVBM] = benchMark
  
  [id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, thetaExposure, theta_tmp, vegaExposure, vega_tmp, PV_tmp] = model.getData(data, idToFind, ratePoints, s0Shock, sigmaShock)
  
  sumUpList = others.sumUpEachList(others.convertDataSet(id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, thetaExposure, theta_tmp, vegaExposure, vega_tmp, PV_tmp))
  [idSum, priceSum, deltaExposureSum, deltaSum, gammaExposureSum, gammaSum, thetaExposureSum, thetaSum, vegaExposureSum, vegaSum, PVSum] = sumUpList
  
  ###Change the positions of views only!
  newBenchMark = [idBM, PVBM, deltaExposureBM, deltaBM, gammaExposureBM, gammaBM, thetaExposureBM, thetaBM, vegaExposureBM, vegaBM, priceBM]

  findResult = [id_tmp, PV_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, thetaExposure, theta_tmp, vegaExposure, vega_tmp, price_tmp]
  
  newSumUpList = [idSum, PVSum, deltaExposureSum, deltaSum, gammaExposureSum, gammaSum, thetaExposureSum, thetaSum, vegaExposureSum, vegaSum, priceSum]

  heatMapData = model.getHeatMapData(data, benchMark, chartType, True, idToFind, ratePoints)
  
  #print(heatMapData)
  #print(sumUpList)
<<<<<<< HEAD
  print(benchMark)
  result = {'data':findResult, 'sum': sumUpList, 'heatMap': heatMapData, 'benchMark': benchMark}
=======

  result = {'data':findResult, 'sum': newSumUpList, 'heatMap': heatMapData, 'benchMark': newBenchMark}
>>>>>>> 6dcda37b7c33178d940d7a75486c7be4a6258f0d
  return JsonResponse(json.dumps(result), safe=False)


def windIDSearch(query):
  windIDToFind = query['ID']
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
  benchMark = model.getBenchMarkList(False, windIDToFind, ratePoints)
  [idSetBM, price_tmpSetBM, deltaExposureSetBM, delta_tmpSetBM, gammaExposureSetBM, gamma_tmpSetBM, thetaExposureSetBM, theta_tmpSetBM, vegaExposureSetBM, vega_tmpSetBM, PVSetBM] = benchMark
  
  [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet] = model.getDataWithWindID(data, windIDToFind, ratePoints, s0Shock, sigmaShock)

  sumUpList = others.sumUpEachList(others.convertDataSet(idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet))
  [idSetSum, price_tmpSetSum, deltaExposureSetSum, delta_tmpSetSum, gammaExposureSetSum, gamma_tmpSetSum, thetaExposureSetSum, theta_tmpSetSum, vegaExposureSetSum, vega_tmpSetSum, PVSetSum] = sumUpList

  ###Change the positions
  newBenchMark = [idSetBM, PVSetBM, deltaExposureSetBM, delta_tmpSetBM, gammaExposureSetBM, gamma_tmpSetBM, thetaExposureSetBM, theta_tmpSetBM, vegaExposureSetBM, vega_tmpSetBM, price_tmpSetBM]

  findResult = [idSet, PVSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, price_tmpSet]

  newSumUpList = [idSetSum, PVSetSum, deltaExposureSetSum, delta_tmpSetSum, gammaExposureSetSum, gamma_tmpSetSum, thetaExposureSetSum, theta_tmpSetSum, vegaExposureSetSum, vega_tmpSetSum, price_tmpSetSum]

  heatMapData = model.getHeatMapData(data, benchMark, chartType, False, windIDToFind, ratePoints)
  
  #print("findResult", findResult)

  result = {'data':findResult, 'sum': newSumUpList, 'heatMap': heatMapData, 'benchMark': newBenchMark}
  return JsonResponse(json.dumps(result), safe=False)



# @csrf_exempt
# def selectChart(request): 
#   params = request.body
#   print(params)
#   query = json.loads(request.body)['query']
#   windIDToFind = query['contract_name']
#   today = query['timeShift']
#   chartType = query['type']

#   om = float(query['OM'])
#   tm = float(query['TM'])
#   sm = float(query['SM'])
#   nm = float(query['NM'])
#   oy = float(query['OY'])
#   sy = float(query['SY'])
#   ty = float(query['TY'])
#   fy = float(query['FY'])
#   hy = float(query['HY'])
#   ratePoints = [None, om, tm, sm, nm, oy, sy, ty, fy, hy]
#   data = model.readData()
#   data = others.setT(data,today)
#   heatMapData = model.getHeatMapData(data, chartType, False, windIDToFind, ratePoints)
#   # result = {'heatMap:': heatMapData}
#   return JsonResponse(json.dumps(heatMapData), safe=False)

