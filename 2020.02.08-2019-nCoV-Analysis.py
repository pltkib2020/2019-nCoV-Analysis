#####################################################################################
##   发布时间：   2020年2月8日     V1.0
##   本文件名:   2019-nCoV疫情分析测试(2020.02.08).py
##   程序运行必须的文件及相应目录结构
##     .\graph  保存生成的相关图像
##     .\data   保存相关下载数据(JSON字串格式)
##     .\res    程序需要使用的地图数据与字体（simsun.ttf），中国各城市人口-2019.csv
##   测试环境： win10 + Python3.7.6
##   IDE：    Pycharm Professional 2019.3
##   MAIL:   pltkib.stone@gmail.com
##   欢迎任何形式的修改，利用及完善，任何BUG请邮件联系作者
##   PS： 生成的图像保存在.\graph 目录之下，格式为PNG格式， Sankey图保存为HTML格式支持交互操作
##
##   ***************** 愿疫情得控，山河无恙，春回大地，人间吉祥！ **********************
##   链接：https://pan.baidu.com/s/1ISYeiAkZ7kJTe1-qESFmqA  提取码：tmee
####################################################################################

# -*- coding: utf-8 -*-
__author__  = 'Bright Stone'
__version__ = '1.1'

import requests, os, sys, bs4, re, time, plotly, json
import numpy as np
import matplotlib
import matplotlib.figure
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Polygon
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image
from datetime import datetime

#plotly.offline.init_notebook_mode(connected=True)
### 湖北......西藏省份共有34个，因为Python的区间都是左闭右开的所以定义了35个
iTotalProvinceNumber = 35

plt.rcParams['font.sans-serif'] = ['FangSong']  # 设置默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时'-'显示为方块的问题

##############################################################################################
##               功能： 得到当前的日期字符串
##               调用参数: 无
##               返回值: 字符串，格式为：  yyyy年mm月dd日_HH时MM分SS秒
##############################################################################################
def getCurrentDateAndTime():

    dayOfWeek = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    localStruct = time.localtime()
    year = int(localStruct.tm_year)
    month = int(localStruct.tm_mon)
    day = int(localStruct.tm_mday)
    hour = int(localStruct.tm_hour)
    minute = int(localStruct.tm_min)
    second = int(localStruct.tm_sec)

    #tm_year=2020, tm_mon=2, tm_mday=7, tm_hour=22, tm_min=30, tm_sec=14,
    #tm_wday=4, tm_yday=38, tm_isdst=0, -1不是夏令时，0不知道是否是夏令时， 1是夏令时
    strTimeString = "%d年%02d月%02d日-%02d时%02d分%02d秒"%(year,month,day,hour,minute,second)
    currentDateANDTime = strTimeString
    return currentDateANDTime
##############################################################################################


##############################################################################################
##  函数名称：  DailyDataStatistics
##  输入参数：  none
##  返回参数：  date_list, confirm_list, suspect_list, dead_list, heal_list
##  函数功能：  从网上下载全国的按日期统计的确诊，疑似，治愈，死亡数据整理成相应LIST
##############################################################################################
def DailyDataStatistics():
    ###抓取有历史记录以来的全国统计数据，并且按照时间从过去到现在进行排序
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name' \
          '=wuwei_ww_cn_day_counts&callback=&_=%d' \
          % int(time.time() * 1000)
    data = json.loads(requests.get(url=url).json()['data'])
    data.sort(key=lambda x: x['date'])

    date_list = list()  # 日期
    confirm_list = list()  # 确诊
    suspect_list = list()  # 疑似
    dead_list = list()  # 死亡
    heal_list = list()  # 治愈

    ####将此刻取得的网络数据保存到数据文件以便日后研究
    strJson = json.dumps(data, ensure_ascii=False)
    dataFileName = '.\\data\\2019-nCoV疫情-全国时间推移统计数据(' + getCurrentDateAndTime() + ').txt'
    dateFileHandle = open(dataFileName, 'w+', encoding='utf-8')
    dateFileHandle.write(strJson)
    dateFileHandle.close()

    for item in data:
        month, day = item['date'].split('/')
        date_list.append(datetime.strptime('2020-%s-%s' % (month, day), '%Y-%m-%d'))
        confirm_list.append(int(item['confirm']))
        suspect_list.append(int(item['suspect']))
        dead_list.append(int(item['dead']))
        heal_list.append(int(item['heal']))

    return date_list, confirm_list, suspect_list, dead_list, heal_list
##############################################################################################


##############################################################################################
##  函数名称：  WuHanFeiYanStatisticsGraph
##  输入参数：  none
##  返回参数：  none
##  函数功能：  用matplotlib绘制全国的疫情数据统计图并保存为文件以便后续研究
##############################################################################################
def WuHanFeiYanStatisticsGraph():

    #### 从腾讯网获取历史统计数据
    date_list, confirm_list, suspect_list, dead_list, heal_list = DailyDataStatistics()

    ####设定图标标题
    strTitleName = '2019-nCoV疫情统计('+ getCurrentDateAndTime() + ')'

    plt.figure(strTitleName, facecolor='#f4f4f4', figsize=(10, 8))
    plt.title(strTitleName, fontsize=20)

    plt.plot(date_list, confirm_list, label='确诊', color='red', linestyle='-')
    plt.plot(date_list, suspect_list, label='疑似', color='magenta', linestyle='-.')
    plt.plot(date_list, heal_list, label='治愈', color='green', linestyle='--')
    plt.plot(date_list, dead_list, label='死亡', color='darkgray', linestyle=':')

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))  # 格式化时间轴标注
    plt.gcf().autofmt_xdate()  # 优化标注（自动倾斜）
    plt.grid(linestyle=':')  # 显示网格
    plt.legend(loc='best')  # 显示图例
    fileName = '.\\graph\\' + strTitleName + '.png'
    plt.savefig(fileName)  # 保存为文件
    plt.show()
##############################################################################################


##############################################################################################
##  函数名称：  WuHanFeiYanMapGraph
##  输入参数：  none
##  返回参数：  none
##  函数功能：  利用Basemap描绘疫情全国形势图，显示地图并且保存地图以便日后研究
##############################################################################################
def WuHanFeiYanMapGraph():

    ###绘制行政区域确诊分布数据"""
    data = getDetailedInformaiton()

    font = FontProperties(fname='res/simsun.ttf', size=14)
    lat_min = 0; lat_max = 60; lon_min = 70; lon_max = 140

    handles = [
        matplotlib.patches.Patch(color='#ffaa85', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#ff7b69', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#bf2121', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#ff1818', alpha=1, linewidth=0),
    ]

    labels = ['1-99人', '100-999人', '1000-3000人', '>3000人']

    fig = matplotlib.figure.Figure()
    fig.set_size_inches(10, 8)  # 设置绘图板尺寸
    axes = fig.add_axes((0.1, 0.12, 0.8, 0.8))  # rect = l,b,w,h
    m = Basemap(llcrnrlon=lon_min, urcrnrlon=lon_max, llcrnrlat=lat_min,
                urcrnrlat=lat_max, resolution='l', ax=axes)
    m.readshapefile('res/china-shapefiles-master/china', 'province', drawbounds=True)
    m.readshapefile('res/china-shapefiles-master/china_nine_dotted_line',
                    'section', drawbounds=True)
    m.drawcoastlines(color='black')  # 洲际线
    m.drawcountries(color='black')  # 国界线
    m.drawparallels(np.arange(lat_min, lat_max, 10), labels=[1, 0, 0, 0])  # 画经度线
    m.drawmeridians(np.arange(lon_min, lon_max, 10), labels=[0, 0, 0, 1])  # 画纬度线

    for info, shape in zip(m.province_info, m.province):
        pname = info['OWNER'].strip('\x00')
        fcname = info['FCNAME'].strip('\x00')
        #不绘制海岛
        if pname != fcname:
            continue
        for key in data.keys():
            if key in pname:
                if data[key] == 0:
                    color = '#f0f0f0'
                elif data[key] < 100:
                    color = '#ffaa85'
                elif data[key] < 1000:
                    color = '#ff7b69'
                elif data[key] < 3000:
                    color = '#bf2121'
                else:
                    color = '#ff1818'
                break

        poly = Polygon(shape, facecolor=color, edgecolor=color)
        axes.add_patch(poly)

    #### 完成图形绘制
    axes.legend(handles, labels, bbox_to_anchor=(0.5, -0.11), loc='lower center', ncol=4, prop=font)
    strCurrentDateTime = getCurrentDateAndTime()
    strTitleName = '2019-nCoV疫情地图(' + strCurrentDateTime +')'
    axes.set_title(strTitleName, fontproperties=font)
    FigureCanvasAgg(fig)

    ### 保存图像到当前目录的 .\graph\子目录，这个需要用户自己设定好
    fileName = '.\\graph\\' + strTitleName + '.png'
    fig.savefig(fileName)

    ###必要时可以打开绘制的地图进行查看，如果启动Timer定时抓取数据，可以注释掉
    im = Image.open(fileName)
    im.show()
##############################################################################################



##############################################################################################
##  函数名称：  getDataListFromOfficialWeb
##  输入参数：  none
##  返回参数：  none
##  函数功能：  从官方网站得到疫情相关数据， 利用正则表达式检索与JSON解析得到相关数据
##############################################################################################
def getDataListFromOfficialWeb():

    dataAnalyzedList = []

    url = "https://ncov.dxy.cn/ncovh5/view/pneumonia"
    response = requests.get(url, timeout = 10)
    response.encoding = response.apparent_encoding
    strReturnText = response.text

    strSearchPattern = 'try.*?{.*?window.getAreaStat.*?=(.*?)\}catch\(e\)'
    strResultList = re.findall(strSearchPattern, strReturnText, re.M | re.S )

    ###如果统计数字不正确，或者官方改变了发布网站
    if len(strResultList) <  1 :
        print("官方发布网站下载数据有错，请手动检查官方网站：", url)
        return dataAnalyzedList

    ### 进行字符串的JSON分解，得到一个LIST，其中每一个元素为一个DICT #######################
    strNeedToAnalyze = str(strResultList[0])
    dataAnalyzedList = json.loads(strNeedToAnalyze)

    ####将此刻取得的网络数据保存到数据文件以便日后研究
    dataFileName = '.\\data\\2019-nCoV疫情-省份统计数据(' + getCurrentDateAndTime() + ').txt'
    dateFileHandle = open(dataFileName, 'w+', encoding='utf-8')
    dateFileHandle.write(strNeedToAnalyze)
    dateFileHandle.close()

    ###################### 返回的LIST的格式如下，非常方便使用###########################
    #[ ############数据LIST开始，每一个LIST元素都是一个字典 格式如下 #####################
    #{
    #        "provinceName": "湖北省",
    #        "provinceShortName": "湖北",
    #       "confirmedCount": 22112,
    #        "suspectedCount": 0,
    #        "curedCount": 828,
    #        "deadCount": 618,
    #        "comment": "",
    #        "locationId": 420000,
    #        "cities":
    #           [
    #               {"cityName": "武汉", "confirmedCount": 11618, "suspectedCount": 0,
    #               "curedCount": 535,  "deadCount": 478, "locationId": 420100},
    #               {"cityName": "孝感", "confirmedCount": 2141, "suspectedCount": 0,
    #               "curedCount": 25, "deadCount": 25,   "locationId": 420900},
    #               {"cityName": "神农架林区", "confirmedCount": 10, "suspectedCount": 0,
    #               "curedCount": 2, "deadCount": 0,    "locationId": 429021}
    #           ]
    #    },
    #    {
    #        "provinceName": "广东省",
    #        "provinceShortName": "广东",
    #        ..................
    #        "cities":
    #           [
    #                {"cityName": "深圳", "confirmedCount": 334, "suspectedCount": 0, "curedCount": 22,
    #                "deadCount": 0,     "locationId": 440300},
    #            ]
    #    }
    #   ]   ############数据LIST结束，每一个LIST元素都是一个字典

    return dataAnalyzedList
##############################################################################################


##############################################################################################
##  函数名称：  getDetailedInformaiton
##  输入参数：  none
##  返回参数：  none
##  函数功能：  将从网站下载的数据进行整理分类
##############################################################################################
def getDetailedInformaiton():

    #### 返回参数的初始化
    plotMapDistributionData = dict()

    ### 进行字符串的JSON分解，得到一个LIST，其中每一个元素为一个DICT
    dataAnalyzed = getDataListFromOfficialWeb()

    ##########全国的数字统计#############################
    iWholeCountryConfirm = 0
    iWholeCountrySuspect = 0
    iWholeCountryCured   = 0
    iWholeCountrydead    = 0

    ### 每个省份的数据处理 BEGIN
    for i in range(len(dataAnalyzed)):

        oneProData = dataAnalyzed[i]

        #### 用于绘制地图的每个省的确诊的数据
        strShortProName = str(oneProData["provinceName"])
        plotMapDistributionData[strShortProName] = int(oneProData["confirmedCount"])

        iWholeCountryConfirm += int(oneProData["confirmedCount"])
        iWholeCountrySuspect += int(oneProData["suspectedCount"])
        iWholeCountryCured += int(oneProData["curedCount"])
        iWholeCountrydead += int(oneProData["deadCount"])

        #print("No.[%d] 省份=[%s] 确诊=[%d]人 疑似=[%d]人 治愈=[%d]人 死亡=[%d]人"
        #      %(i+1, oneProData["provinceShortName"], oneProData["confirmedCount"],
        #        oneProData["suspectedCount"],oneProData["curedCount"],
        #        oneProData["deadCount"]))
        ##### 处理一个省份中的城市数据 BEGIN
        citiesList = oneProData["cities"]
        iCityNum = len(citiesList)
        if iCityNum > 1 :
            for index in range(iCityNum) :
                cityData = citiesList[index]
                #print("\tNo.[%d-%d] 省份=[%s] 确诊=[%d]人 疑似=[%d]人 治愈=[%d]人 死亡=[%d]人"
                #      % (i + 1, index+1, cityData["cityName"], cityData["confirmedCount"],
                #         cityData["suspectedCount"], cityData["curedCount"],
                #         cityData["deadCount"]))
        ##### 处理一个省份中的城市数据 END
    ### 每个省份的数据处理 END

    #print("全国统计数字：  确诊[ %d ]人   疑似[ %d ]人   治愈[ %d ]人   死亡[ %d ]人"
    #      %(iWholeCountryConfirm,iWholeCountrySuspect,iWholeCountryCured,iWholeCountrydead ))

    return plotMapDistributionData
##############################################################################################



##############################################################################################
##  函数名称：  WuhanFeiyanSankey
##  输入参数：  none
##  返回参数：  none
##  函数功能：  绘制疫情传播桑基图
##############################################################################################
def WuhanFeiyanSankey():

    global iTotalProvinceNumber

    labelNameList = ['中国总人口', '湖北', '广东', '浙江', '河南', '湖南', '江西', '安徽',
                 '重庆', '江苏', '山东', '四川', '北京', '上海', '黑龙江', '福建', '陕西',
                 '广西', '河北', '云南', '海南', '山西', '辽宁', '天津', '贵州', '甘肃',
                 '吉林', '内蒙古', '宁夏', '新疆','香港','青海','台湾','澳门','西藏',
                 '确诊总人数', '治愈总人数', '死亡总人数']

    ### Population of each province data, delete #.... comment lines
    dataFileName = ".\\res\\中国各城市人口-2019.csv"
    fileReadHandle = open(dataFileName, 'r', encoding='utf-8')
    readBuffer = fileReadHandle.read()
    listRead =  readBuffer.strip().split('\n')
    realContentList=[]
    for i in range(len(listRead)):
        strTemp = str(listRead[i])
        strTemp = strTemp.strip()
        if len(strTemp)>0 and strTemp.find("#") == -1 :
            realContentList.append(strTemp)

    ### 初始化数据结果字典 ###########################################################################
    #### data= {'北京': {'population': 19612368, 'confirm': 168, 'cured': 1, 'died': 9
    #                   'confirm-ratio'：0.001，  'cured-ratio'：0.001， 'died-ratio'：0.001 },
    #           '天津': {'population': 19612368, 'confirm': 168, 'cured': 1, 'died': 9
    #                   'confirm-ratio'：0.001，  'cured-ratio'：0.001， 'died-ratio'：0.001 },
    ###############################################################################################
    #print('realContentList=',realContentList)
    ##### 共有34个省市自治区需要纳入统计，如果不正确则不进行Sankey图的绘制处理
    if len(realContentList) != iTotalProvinceNumber-1 :
        print("请检查文件[%s]中的行数是否为34，格式是否正确！"%(dataFileName))
        return -1

    #### 将34个省市自治区的数据字典进行初始化处理
    data = dict()
    for i in range(len(realContentList)) :
        lineList = str(realContentList[i]).split(',')
        strProShortName = str(lineList[0])
        iProvincePopulation = int(lineList[1])
        eachProvinceDict = dict()
        eachProvinceDict['population'] = iProvincePopulation
        eachProvinceDict['confirm'] = 0
        eachProvinceDict['cured'] = 0
        eachProvinceDict['died'] = 0
        eachProvinceDict['confirm-ratio'] = 0.0
        eachProvinceDict['cured-ratio'] = 0.0
        eachProvinceDict['died-ratio'] = 0.0
        data[strProShortName] = eachProvinceDict
    ########### 查询官方网站将必要的数据分解并填写到准备好的data数据字典当中去

    ################ 用从官方网站得到一个数据LIST，填充需要绘制桑基图的数据字典########################
    iTotalPopulation = 0
    iTotalConfirm = 0
    iTotalcured = 0
    iTotalDied  = 0
    webDataList = getDataListFromOfficialWeb()
    for i in range(len(webDataList)) :
        webDict = webDataList[i]
        strShortProName = str(webDict['provinceShortName'])
        useDict = data[strShortProName]
        useDict['confirm'] = int(webDict['confirmedCount'])
        useDict['cured'] = int(webDict['curedCount'])
        useDict['died'] = int(webDict['deadCount'])
        useDict['confirm-ratio'] = float(useDict['confirm']) / float(useDict['population'])
        useDict['cured-ratio'] = float(useDict['cured']) / float(useDict['population'])
        useDict['died-ratio'] = float(useDict['died']) / float(useDict['population'])
        iTotalPopulation += useDict['population']
        iTotalConfirm    += useDict['confirm']
        iTotalcured      += useDict['cured']
        iTotalDied       += useDict['died']


    ### 检查一下看看准备好了的桑基图的数据是否正确
    ### print("data=", data)

    ########将统计人口数字加入到标签之中
    stTemp = "中国总人口\(" + str(iTotalPopulation) + " 人)"
    labelNameList[0] = stTemp

    stTemp = "确诊总人数(" + str(iTotalConfirm) + " 人)"
    labelNameList[35] = stTemp

    stTemp = "治愈总人数(" + str(iTotalcured) + " 人)"
    labelNameList[36] = stTemp

    stTemp = "死亡总人数(" + str(iTotalDied) + " 人)"
    labelNameList[37] = stTemp


    ########### Sankey Diagram 需要的三个数据LIST的数据准备 #######################
    sourceList = []
    targetList = []
    ValueList  = []

    ### Deal withe populaiton of each province
    totalPopulaitonIndex = 0
    for i in range(1,iTotalProvinceNumber) :
        sourceList.append(totalPopulaitonIndex)
        targetList.append(i)
        strProviceName = str(labelNameList[i])
        iValue = data[strProviceName]['population']
        ValueList.append(iValue)

    ### Deal withe confirm data of each province
    indexConfirmLabel = 35
    for i in range(1,iTotalProvinceNumber) :
        sourceList.append(i)
        targetList.append(indexConfirmLabel)
        strProviceName = str(labelNameList[i])
        iValue = data[strProviceName]['confirm']
        ValueList.append(iValue)

    ### Deal withe cured data of each province
    indexCuredLabel = 36
    for i in range(1,iTotalProvinceNumber) :
        sourceList.append(i)
        targetList.append(indexCuredLabel)
        strProviceName = str(labelNameList[i])
        iValue = data[strProviceName]['cured']
        ValueList.append(iValue)

    ### Deal withe died data of each province
    indexDiedLabel = 37
    for i in range(1,iTotalProvinceNumber) :
        sourceList.append(i)
        targetList.append(indexDiedLabel)
        strProviceName = str(labelNameList[i])
        iValue = data[strProviceName]['died']
        ValueList.append(iValue)

    xList=[]
    yList=[]

    xList.append(0.1)
    yList.append(0.1)

    for i in range(1,iTotalProvinceNumber) :
        xList.append(0.3)
        yCoord = 1.0 / iTotalProvinceNumber * i
        yList.append(yCoord)

    ####################确诊总人数标签位置
    xList.append(0.5)
    yList.append(0.2)
    ####################治愈总人数标签位置
    xList.append(0.7)
    yList.append(0.5)
    ####################死亡总人数标签位置
    xList.append(0.9)
    yList.append(0.8)


    data_trace = dict(

        type='sankey',


        node=dict(pad=20,
                  thickness=50,
                  line=dict(color="black", width=0.5),
                  label=labelNameList,
                  x=xList,
                  y=yList),

        link=dict(source=sourceList,
                  target=targetList,
                  value=ValueList )

    )

    titleName = '2019-nCoV疫情桑基图(' + getCurrentDateAndTime() + ')'
    myfilename  = '.\\graph\\' + titleName + '.html'

    layout = dict(
                    title=titleName ,
                    font=dict(size=15, color='black'),
                )

    fig = dict(data=[data_trace], layout=layout)
    plotly.offline.plot(fig, validate=False, filename = myfilename)
##########################################################################################


##############################################################################################
##  函数名称：  main
##  输入参数：  none
##  返回参数：  none
##  函数功能：  三种统计图模块调用与绘制
##############################################################################################
if __name__ == '__main__':
    print(getCurrentDateAndTime(), "开始处理全国统计数据......")
    WuHanFeiYanStatisticsGraph()

    print(getCurrentDateAndTime(), "开始处理疫情地图数据......")
    WuHanFeiYanMapGraph()

    print(getCurrentDateAndTime(), "开始绘制疫情数据桑基图......")
    WuhanFeiyanSankey()
##########################################################################################


