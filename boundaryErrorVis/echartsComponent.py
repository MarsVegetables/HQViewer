'''
Date: 2021-09-09 00:19:37
LastEditors: Lei Si
LastEditTime: 2021-09-19 19:22:49
'''
from pyecharts.charts import Bar, Line
from pyecharts import options as opts
from jinja2 import Environment, FileSystemLoader
import os

# main chart generation functions are located in BndErrorVisUtility.py

class chartBase:
    def __init__(self, _htmlName, _title, _data) -> None:
        self.fileName = _htmlName
        self.fullPath = self.getHtmlPath(self.fileName)
        self.relative_path = self.get_relative_path(self.fileName)
        self.title = _title
        self.data = _data
        self.chart = Bar()
    
    def getHtmlPath(self, _htmlName):
        hpath = os.path.join(
                        os.path.abspath(os.path.dirname(__file__)), "echartsOutput", _htmlName
                    )
        return hpath

    def get_relative_path(self, _htmlName):
        hpath = os.path.join(
            "boundaryErrorVis/echartsOutput", _htmlName
        )
        return hpath

    def setChartSize(self):
        self.chart.width = "98vw"
        self.chart.height = "98vh"

    def addXaxis(self, _xlabel):
        # self.bar.add_xaxis(["衬衫", "毛衣", "领带", "裤子", "风衣", "高跟鞋", "袜子"])
        self.chart.add_xaxis(_xlabel)
    
    def addYaxis(self, _name, _data):
        # self.bar.add_yaxis("商家A", [114, 55, 27, 101, 125, 27, 105])
        self.chart.add_yaxis(_name, _data, label_opts=opts.LabelOpts(is_show=False))
        self.chart.set_series_opts(
                markline_opts=opts.MarkLineOpts(
                    data=[
                            opts.MarkLineItem(type_="min", name="Min"),
                            opts.MarkLineItem(type_="max", name="Max"),
                        ]
                    ),
            )

    def addMouseClickJSFuncs(self):
        charVar = "chart_" + self.chart.chart_id
        # js_f = charVar + ".on('click', function(params){alert(params.seriesName + params.name + params.value); window.pyQtOpt.printRef(params.value);})"
        js_f = charVar + ".on('click', function(params){window.pyQtOpt.printRef(params.name);})"
        self.chart.add_js_funcs(js_f)

    def addDataToBar(self):
        d = self.data
        name = d[0]
        xlabel = d[1]
        ydata = d[2]
        self.addXaxis(xlabel)
        for i, n in enumerate(name):
            self.addYaxis(n, ydata[i])

    def render(self):
        self.chart.render(self.fullPath, \
            template_name= "bndErrorTpl.html", \
            env = Environment(
                keep_trailing_newline=True,
                trim_blocks=True,
                lstrip_blocks=True,
                loader=FileSystemLoader( # set path to load templates
                    os.path.join(
                        os.path.abspath(os.path.dirname(__file__)), "render", "templates"
                    )
                )
            )
        )

class echartsBar(chartBase):
    def __init__(self, _htmlName, _title, _data, funcIndex = 0) -> None:
        super().__init__(_htmlName, _title, _data)
        if funcIndex == 0:
            self.createBar()
        if funcIndex == 1:
            self.createBar_localQuality()
        if funcIndex == 2:
            self.createBar_allQuality()
        
    def createBar(self):
        self.chart = (
            Bar()
            .set_global_opts(title_opts=opts.TitleOpts(title=self.title),
                datazoom_opts=[opts.DataZoomOpts(range_start = 0, range_end = 100), 
                opts.DataZoomOpts(orient="vertical", range_start = 0, range_end = 100),
                opts.DataZoomOpts(type_="inside")],
                yaxis_opts=opts.AxisOpts(name="percentage"),
                xaxis_opts=opts.AxisOpts(name="vertex"),
            )  
        )
        self.setChartSize()
        self.addDataToBar()
        self.addMouseClickJSFuncs()
            
    def createBar_localQuality(self):
        self.chart = (
            Bar()
            .set_global_opts(title_opts=opts.TitleOpts(title=self.title),
                datazoom_opts=[opts.DataZoomOpts(range_start = 0, range_end = 100), 
                opts.DataZoomOpts(orient="vertical", range_start = 0, range_end = 100),
                opts.DataZoomOpts(type_="inside")],
                yaxis_opts=opts.AxisOpts(name="Value"),
                xaxis_opts=opts.AxisOpts(name="Corner"),
            )  
        )
        self.setChartSize()
        self.addDataToBar()
        self.addMouseClickJSFuncs()
    
    def createBar_allQuality(self):
        self.chart = (
            Bar()
            .set_global_opts(title_opts=opts.TitleOpts(title=self.title),
                datazoom_opts=[opts.DataZoomOpts(range_start = 0, range_end = 100), 
                opts.DataZoomOpts(orient="vertical", range_start = 0, range_end = 100),
                opts.DataZoomOpts(type_="inside")],
                yaxis_opts=opts.AxisOpts(name="Value"),
                xaxis_opts=opts.AxisOpts(name="Vertex"),
            )  
        )
        self.setChartSize()
        self.addDataToBar()
        self.addMouseClickJSFuncs()
        
class echartsLine(chartBase):
    def __init__(self, _htmlName, _title, _data) -> None:
        super().__init__(_htmlName, _title, _data)
        self.createLine()
    
    def createLine(self):
        self.chart = (
            Line()
            .set_global_opts(title_opts=opts.TitleOpts(title=self.title))
        )
        self.setChartSize()
        self.addDataToBar()
        self.addMouseClickJSFuncs()
