import tkinter as tk
from tkinter import TOP, W, X, LEFT, YES, BOTH
import os
from price import appModel as model
from price import others as others

from price import heatMap as heatMap

#import matplotlib.pyplot as plt
#from pyecharts import Bar

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets(self.master)

    def create_widgets(self, master):
        ########
        
        buttonFrame = tk.Frame(master)
        self.idButton = tk.Button(buttonFrame, width = 10)
        self.idButton["text"] = "Search By ID"
        self.idButton["command"] = self.computation
        self.idButton.pack(side="left", expand = "yes")
        
        """
        self.windIDButton = tk.Button(buttonFrame, width = 10)
        self.windIDButton["text"] = "Search By Wind ID"
        self.windIDButton["command"] = self.windIDSearch
        self.windIDButton.pack(side="right", expand = "yes")
        """
        
        self.plotButton = tk.Button(buttonFrame, width = 10)
        self.plotButton["text"] = "Plot"
        self.plotButton["command"] = self.plot
        self.plotButton.pack(side="right", expand = "yes")
        
        buttonFrame.pack(side = "top", expand = "yes")
        
        ######
        fm1 = tk.Frame(master)
        self.timeLabel = tk.Label(fm1, text='Today:')
        self.timeLabel.pack(side = "left", anchor="w", fill="x", expand="yes")
        
        self.time = tk.StringVar()
        self.time.set('2019-07-08')
        self.tInputBox = tk.Entry(fm1, textvariable = self.time)
        self.tInputBox.pack(side = "right", anchor="w", fill="x", expand="yes")
        
        fm1.pack(expand = "yes")
        
        ######
        fm11 = tk.Frame(master)
        self.s0Label = tk.Label(fm11, text='Spot Bump:')
        self.s0Label.pack(side = "left", anchor="w", fill="x", expand="yes")
        
        self.s0 = tk.StringVar()
        self.s0.set('1.0')
        self.s0InputBox = tk.Entry(fm11, textvariable = self.s0)
        self.s0InputBox.pack(side = "right", anchor="w", fill="x", expand="yes")
        
        fm11.pack(expand = "yes")
        
        ######
        fm111 = tk.Frame(master)
        self.sigmaLabel = tk.Label(fm111, text='Volatility Bump:')
        self.sigmaLabel.pack(side = "left", anchor="w", fill="x", expand="yes")
        
        self.sigma = tk.StringVar()
        self.sigma.set('1.0')
        self.sigmaInputBox = tk.Entry(fm111, textvariable = self.sigma)
        self.sigmaInputBox.pack(side = "right", anchor="w", fill="x", expand="yes")
        
        fm111.pack(expand = "yes")
        
        ######
        fm2 = tk.Frame(master)
        self.idLabel = tk.Label(fm2, text='ID:')
        self.idLabel.pack(side = "left", anchor="w", fill="x", expand="yes")
       
        self.idString = tk.StringVar()
        self.idString.set('19461157')
        self.idInputBox = tk.Entry(fm2, textvariable = self.idString)
        self.idInputBox.pack(side = "right", anchor="w", fill="x", expand="yes")
        
        fm2.pack(expand = "yes")
        #######
        """
        windIDFrame = tk.Frame(master)
        self.windIDLabel = tk.Label(windIDFrame, text='Wind ID:')
        self.windIDLabel.pack(side = "left", anchor="w", fill="x", expand="yes")
       
        self.windIDString = tk.StringVar()
        self.windIDString.set('000016.SH')
        self.windIDInputBox = tk.Entry(windIDFrame, textvariable = self.windIDString)
        self.windIDInputBox.pack(side = "right", anchor="w", fill="x", expand="yes")
        
        windIDFrame.pack(expand = "yes")
        """
        #######

        fm3 = tk.Frame(master)
        self.label1 = tk.Label(fm3, text='Price:')
        self.label1.pack(side = "left", anchor="w", fill="x", expand="yes")
       
        self.priceString = tk.StringVar()
        self.priceString.set("0.0")
        self.priceLabel = tk.Entry(fm3, text = self.priceString)
        self.priceLabel.pack(side = "right", anchor="w", fill="x", expand="yes")
        
        fm3.pack(expand = "yes")
        ########
        
        fm4 = tk.Frame(master)
        self.label2 = tk.Label(fm4, text='Delta:')
        self.label2.pack(side = "left", anchor="w", fill="x", expand="yes")
       
        self.deltaString = tk.StringVar()
        self.deltaString.set("0.0")
        self.deltaLabel = tk.Entry(fm4, text = self.deltaString)
        self.deltaLabel.pack(side = "right", anchor="w", fill="x", expand="yes")
        
        fm4.pack(expand = "yes")
        ########
        
        fm5 = tk.Frame(master)
        self.label3 = tk.Label(fm5, text='Gamma:')
        self.label3.pack(side = "left", anchor="w", fill="x", expand="yes")
       
        self.gammaString = tk.StringVar()
        self.gammaString.set("0.0")
        self.gammaLabel = tk.Entry(fm5, text = self.gammaString)
        self.gammaLabel.pack(side = "right", anchor="w", fill="x", expand="yes")
        
        fm5.pack(expand = "yes")
        ########
        
        fm6 = tk.Frame(master)
        self.label4 = tk.Label(fm6, text='Vega:')
        self.label4.pack(side = "left", anchor="w", fill="x", expand="yes")
       
        self.vegaString = tk.StringVar()
        self.vegaString.set("0.0")
        self.vegaLabel = tk.Entry(fm6, text = self.vegaString)
        self.vegaLabel.pack(side = "right", anchor="w", fill="x", expand="yes")
        
        fm6.pack(expand = "yes")
        ########
        
        fm7 = tk.Frame(master)
        self.label5 = tk.Label(fm7, text='Theta:')
        self.label5.pack(side = "left", anchor="w", fill="x", expand="yes")
       
        self.thetaString = tk.StringVar()
        self.thetaString.set("0.0")
        self.thetaLabel = tk.Entry(fm7, text = self.thetaString)
        self.thetaLabel.pack(side = "right", anchor="w", fill="x", expand="yes")
        
        fm7.pack(expand = "yes")
        
        
        #######
        
        self.quit = tk.Button(self, width = 10, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side = "bottom")
        
    def computation(self):
        if others.isNormalID(self.idString.get()):
            self.idSearch()
        else:
            self.windIDSearch()

    
    def idSearch(self):
        #pathString = os.path.abspath("UITest.py")[:-9] + "data.xls"
        idToFind = self.idString.get()
        today = self.time.get()
        s0Shock = self.s0.get()
        sigmaShock = self.sigma.get()
        #[idSet, price_tmpSet, delta_tmpSet, gamma_tmpSet, vega_tmpSet, theta_tmpSet] = model.getData(idToFind, today, s0Shock, sigmaShock)
        #self.priceString.set(price_tmpSet[0])
        #self.deltaString.set(delta_tmpSet[0])
        #self.gammaString.set(gamma_tmpSet[0])
        #self.vegaString.set(vega_tmpSet[0])
        #self.thetaString.set(theta_tmpSet[0])
        ratePoints = [None, 0.0229471, 0.0250464, 0.0254817, 0.0255681, 0.0258563, 0.0263679, 0.0270334, 0.0279025, None]
        """
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
        """
        data = model.readData()
        data = others.setT(data,today) # data is T-sensitive
        [id_tmp, price_tmp, deltaExposure, delta_tmp, gammaExposure, gamma_tmp, thetaExposure, theta_tmp, vegaExposure, vega_tmp, PV_tmp] = model.getData(data, idToFind, ratePoints, s0Shock, sigmaShock)
        #heatMapData = model.getHeatMapData(data, "Price", True, idToFind, ratePoints)
        #print(heatMapData[0])
        print(price_tmp[0], deltaExposure[0], delta_tmp[0], gammaExposure[0], gamma_tmp[0], thetaExposure[0], theta_tmp[0], vegaExposure[0], vega_tmp[0], PV_tmp[0])
        
    def windIDSearch(self):
        windIDToFind = self.idString.get()  #########
        today = self.time.get()
        s0Shock = self.s0.get()
        sigmaShock = self.sigma.get()
        ratePoints = [None, 0.0229471, 0.0250464, 0.0254817, 0.0255681, 0.0258563, 0.0263679, 0.0270334, 0.0279025, None]
        data = model.readData()
        data = others.setT(data,today) # data is T-sensitive
        [idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet] = model.getDataWithWindID(data, windIDToFind, ratePoints, s0Shock, sigmaShock)
        sumUpList = others.sumUpEachList(others.convertDataSet(idSet, price_tmpSet, deltaExposureSet, delta_tmpSet, gammaExposureSet, gamma_tmpSet, thetaExposureSet, theta_tmpSet, vegaExposureSet, vega_tmpSet, PVSet))
        print(sumUpList)

        #heatMapData = model.getHeatMapData(data, "Price", False, windIDToFind, ratePoints)
        #print(heatMapData[0])
        
        
    def plot(self):
        idToFind = self.idString.get()
        today = self.time.get()
        ratePoints = [None, 0.0229471, 0.0250464, 0.0254817, 0.0255681, 0.0258563, 0.0263679, 0.0270334, 0.0279025, None]
        heatMap.plotHeatMap(idToFind, today, ratePoints)
        print("Plotted")

 
    
root = tk.Tk()
root.geometry("300x500")
app = Application(master=root)
app.mainloop()


