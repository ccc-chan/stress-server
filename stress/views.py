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
def test(request):
  query = json.loads(request.body)['query']
  idToFind = query['ID']
  today = query['timeShift']
  ratePoints = [None, 0.023, 0.0251, 0.0256, 0.0257, 0.0259, 0.0265, 0.0271, 0.028, 0.0288]
  heatMap.plotHeatMap(idToFind, today, ratePoints)
  print("Plotted")

@csrf_exempt
def createTime(request):
  hTime = ''
  sTime = ''
  if os.path.exists('E:/stress-server/price/historyData.xls'): 
    historyTime = time.localtime(os.stat("E:/stress-server/price/historyData.xls").st_mtime)
    hTime = time.strftime('%Y-%m-%d %H:%M:%S', historyTime)
  if os.path.exists('E:/stress-server/price/sigmaData.xls'): 
    sigmaTime = time.localtime(os.stat("E:/stress-server/price/sigmaData.xls").st_mtime)
    sTime = time.strftime('%Y-%m-%d %H:%M:%S', sigmaTime)
  return JsonResponse({'hTime': hTime, 'sTime': sTime})

@csrf_exempt
def uploadHistory(request):
  data = request.FILES.get('historyFile')
  file_full_path = 'E:/stress-server/price/historyData.xls'
  if os.path.exists(file_full_path): 
    os.remove(file_full_path)
  dest = open(file_full_path,'wb+')
  dest.write(data.read())
  dest.close()
  res = createTime(request)
  return res

@csrf_exempt
def uploadSigma(request):
  data = request.FILES.get('sigmaFiles')
  file_full_path = 'E:/stress-server/price/sigmaData.xls'
  if os.path.exists(file_full_path): 
    os.remove(file_full_path)
  dest = open(file_full_path,'wb+')
  dest.write(data.read())
  dest.close()
  res = createTime(request)
  return res

@csrf_exempt
def searchById(request):
  params = request.body
  print(params)
  query = json.loads(request.body)['query']
  idToFind = query['ID']
  today = query['timeShift']
  s0Shock = query['price_bump']
  sigmaShock = query['volatility_bump']
  om = float(query['OM'])
  tm = float(query['TM'])
  sm = float(query['SM'])
  nm = float(query['NM'])
  oy = float(query['OY'])
  sy = float(query['SY'])
  ty = float(query['TY'])
  fy = float(query['FY'])
  hy = float(query['HY'])
  ratePoints = [None, om, tm, sm, nm, oy, sy, ty, fy, hy]
  print(ratePoints)
  data = model.readData()
  data = others.setT(data,today)
  [id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, vegaExposure, vega_tmp, thetaExposure, theta_tmp] = model.getData(data, idToFind, ratePoints, s0Shock, sigmaShock)
  
  findResult = [id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, vegaExposure, vega_tmp, thetaExposure, theta_tmp]
  convertedData = others.convertDataSet(id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, vegaExposure, vega_tmp, thetaExposure, theta_tmp)
  heatMapData = model.getHeatMapData(data, "Price", True, idToFind, ratePoints)
  sumUpList = others.sumUpEachList(others.convertDataSet(id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, vegaExposure, vega_tmp, thetaExposure, theta_tmp))
  print(heatMapData)
  print(sumUpList)

  result = {'data':findResult, 'sum': sumUpList, 'heatMap:': heatMapData}
  return JsonResponse(json.dumps(result), safe=False)

@csrf_exempt
def searchByWind(request):
  params = request.body
  print(params)
  query = json.loads(request.body)['query']
  windIDToFind = query['contract_name']
  today = query['timeShift']
  s0Shock = query['price_bump']
  sigmaShock = query['volatility_bump']

  om = float(query['OM'])
  tm = float(query['TM'])
  sm = float(query['SM'])
  nm = float(query['NM'])
  oy = float(query['OY'])
  sy = float(query['SY'])
  ty = float(query['TY'])
  fy = float(query['FY'])
  hy = float(query['HY'])
  ratePoints = [None, om, tm, sm, nm, oy, sy, ty, fy, hy]
  data = model.readData()
  data = others.setT(data,today)
  [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, vegaExposureSet, vega_tmpSet, thetaExposureSet, theta_tmpSet] = model.getDataWithWindID(data, windIDToFind, ratePoints, s0Shock, sigmaShock)
  findResult = [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, vegaExposureSet, vega_tmpSet, thetaExposureSet, theta_tmpSet]
  sumUpList = others.sumUpEachList(others.convertDataSet(idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, vegaExposureSet, vega_tmpSet, thetaExposureSet, theta_tmpSet))
  heatMapData = model.getHeatMapData(data, "Price", False, windIDToFind, ratePoints)
  print("findResult", findResult)


  result = {'data':findResult, 'sum': sumUpList, 'heatMap:': heatMapData}
  return JsonResponse(json.dumps(result), safe=False)