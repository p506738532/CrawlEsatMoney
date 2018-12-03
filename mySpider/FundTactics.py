# -*- coding: utf-8 -*-
__author__ = 'Administrator'
'''
文件名：FundTactics.py
作用：分析基金数据，绘制折线图。
'''
import pymysql
import os
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import matplotlib

from datetime import datetime
from datetime import date
from datetime import timedelta
import csv
import smtplib
from email.utils import formataddr
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

from mySpider import Configure
matplotlib.style.use('ggplot')
#用来分析基金净值的变化
class FundTactics():
    #卖出手续费率有4个档，持有天数[0,7)，1.50%，[7,365)0.5%,[365,730)0.25%,[730,无穷)0%
    sellRateList = [0.985,0.995,0.9975,1.0]
    dateCountList =[] #[日期,对应当日份额]列表
    #图片保存路径
    imagePath = "./figure"
    expectValueStr = ''#估计值概况
    foundInfo = ''#基金持有情况详情
    def __init__(self):
        #新建存储图片的路径
        if os.path.isdir(self.imagePath) == False :
            os.mkdir(self.imagePath)
    #求卖出时的卖出费率；date:卖出日期
    def sellRate(self,date):
        keepTime = (date - self.dateCountList[0][0])/timedelta(days=1) #持有时间
        if  keepTime >= 730 :
            return self.sellRateList[3]
        elif keepTime >= 365 :
            return self.sellRateList[2]
        elif keepTime >= 7:
            return self.sellRateList[1]
        else:
            print("警告：费率太高！")
            return self.sellRateList[0];
    #持有时长大于7天的份数
    def keepTimeLonger7(self,currentDate):
        countTotal = 0;#持有时长大于7天的份数
        for dateCount in self.dateCountList:
            if (currentDate - dateCount[0])/timedelta(days=1) >= 7:
                countTotal += dateCount[1]
        print("持有时长大于7天份额：",countTotal)
        return countTotal
    #从数据库中获取数据
    def plotData(self):
        #下载数据
        dicDateValue = self.downloadData()
        #根据时间选择数据,最近30天数据
        dayDelta = -1 * 7#len(dicDateValue["fundValue"])
        # currentDate = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        # (datetime.now() - timeDelta).strftime('%Y-%m-%d')

        averageValue = np.mean(dicDateValue["fundValue"][dayDelta:])
        df = pd.DataFrame({"fundValue":dicDateValue["fundValue"][dayDelta:],
                           "averageValue":averageValue },
                          dicDateValue["fundDate"][dayDelta:]
                          )
        df.plot()
        plt.legend(loc='best')
        tradeDateValue = self.tradeDateValue()
        # print(tradeDateValue)
        #"red"表示买入，"green"表示卖出
        colors = []
        for i in range(len(tradeDateValue["fundDate"])):
            if float(tradeDateValue["tradeValue"][i]) > 0 :
                colors += ["red"]
            else:
                colors += ["green"]
        plt.scatter(x=tradeDateValue["fundDate"],y=tradeDateValue["fundValue"],s=30,c=colors, alpha=0.5)
        plt.title('"red"-buy "green"-sell')
        plt.show()

    #下载净值数据，按日期升序排列
    def downloadData(self):
        #连接数据库
        db = pymysql.connect(Configure.mysqlHost, Configure.mysqlUser, Configure.mysqlPassword,
                             Configure.mysqlDatabase, charset=Configure.mysqlCharset)
        #获取操作游针
        cursor = db.cursor()
        #构造查询sql语句
        selectStr = "SELECT * FROM jjjz_110003 ORDER BY FundDate"
        print("select sql:",selectStr)
        # 执行SQL语句
        cursor.execute(selectStr)
        results = cursor.fetchall()
        fundDate = []
        fundValue = []
        for row in results:
            fundDate +=[row[0]]
            fundValue += [row[1]]
            # print( "date:%s,value:%f" % (fundDate,fundValue) )
        return {"fundDate":fundDate,"fundValue":fundValue}
        db.close()
    def computeIncome(self):
        #全局变量清零
        self.dateCountList.clear()
        #下载净值信息
        dicDateValue = self.downloadData()
        #读取交易记录
        tradeRecord = self.readTradeRecord();
        '''
        定投收益分析，买入手续费0.15%，卖出手续费0.5%,三天单位收益分别为15,5,10，前两天定投100元，第三天卖出，求收益率。
        买入份额=100*0.9985/15+100*0.9985/5
        卖出的钱=买入份额*0.995*10=205.36
        收益率=5.36/200=2.68%
        '''
        buyRate = 0.9985
        fundCount = 0.0#持有份数
        sellMoney = 0.0#卖出基金得到的钱
        buyMoney = 0.0#买基金花的钱

        #遍历交易记录
        for index in range(len(tradeRecord["fundDate"] ) ):
            tradeDate = tradeRecord["fundDate"][index]#交易日期
            date = datetime.strptime(tradeDate,'%Y-%m-%d').date()
            tradeRate = float(tradeRecord["fundValue"][index])#交易钱数
            indexOfList = 0
            #从净值列表中查找净值
            while date <= dicDateValue["fundDate"][-1] :
                if dicDateValue["fundDate"].count(date) == 1 :
                    indexOfList = dicDateValue["fundDate"].index(date)
                    break
                else:
                    date += timedelta(days=1)
            #找到了净值
            fundValue = dicDateValue["fundValue"][indexOfList]
            if tradeRate <0 :#卖出
                tradeRate *= -1
                fundLeftValue = tradeRate#交易的钱数
                while fundLeftValue > 0 :
                    #交易的费率
                    sellRate = self.sellRate(date)
                    #交易的份额
                    sellCount = 0
                    if fundLeftValue > float(self.dateCountList[0][1]*fundValue*sellRate) :
                        fundLeftValue -= float(self.dateCountList[0][1]*fundValue*sellRate)
                        fundCount -= self.dateCountList[0][1]#卖出的份数
                        sellCount += self.dateCountList[0][1]
                        #print("卖出日期：",self.dateCountList[0][0],"卖出份额：",self.dateCountList[0][1])
                        del self.dateCountList[0]
                    else :
                        #计算卖出的份数
                        fundCount -= fundLeftValue/sellRate/fundValue
                        self.dateCountList[0][1] -= fundLeftValue/sellRate/fundValue
                        sellCount+=fundLeftValue/sellRate/fundValue
                        #print("卖出日期：",self.dateCountList[0][0],"剩余份额：",self.dateCountList[0][1])
                        fundLeftValue = 0
                sellMoney += tradeRate
                # print("卖出的钱",tradeRate,"卖出份",sellCount,"单位净值",fundValue,"成交日期",date)
            else:#买入
                fundCount += tradeRate*buyRate/fundValue#买入的份数
                buyMoney += tradeRate
                self.dateCountList.append([date,tradeRate*buyRate/fundValue])
                # print("买入的钱",tradeRate,"买入份",tradeRate*buyRate/fundValue,"单位净值",fundValue,"成交日期",date)
        # 持仓成本=投入的钱数/持有份额，与支付宝计算有偏差，不知道它怎么算的
        latestValue = dicDateValue["fundValue"][-1]
        print("持有份额:",fundCount,"持有市值:",latestValue * fundCount,"持仓成本:",
              (buyMoney - sellMoney)/fundCount)
        #持有时长大于7天的份额
        countLonger7 = self.keepTimeLonger7(date.today())
        print("现金投入：",buyMoney - sellMoney )
        self.foundInfo = """持有时长大于7天的份额%.2f
        持有总份额:%d , 持有市值:%.2f ,持仓成本:%.2f，现金投入：%.2f , 累计收益：%.2f
        """ % (countLonger7,fundCount,latestValue * fundCount,(buyMoney - sellMoney)/fundCount,buyMoney - sellMoney ,
        latestValue * fundCount + sellMoney - buyMoney )

        return latestValue * fundCount + sellMoney - buyMoney

    #从csv文件中读取交易记录，日期升序排列
    def readTradeRecord(self):
        filename = 'tradeRecord.csv'
        fundDate =[]
        fundValue = []
        with open(filename) as f:
            reader = csv.reader(f)
            for row in reader:
                fundDate+=[row[0]]
                fundValue+=[row[1]]
                #print(row[0],row[1])
        return {"fundDate":fundDate,"fundValue":fundValue}
    #获得交易时的日期及价格
    def tradeDateValue(self):
        #下载净值信息
        dicDateValue = self.downloadData()
        #读取交易记录
        tradeRecord = self.readTradeRecord();
        tradeDateList = []#交易日期列表
        tradeUnitValueList = []#交易单位净值列表
        #遍历交易记录
        for index in range(len(tradeRecord["fundDate"] ) ):
            tradeDate = tradeRecord["fundDate"][index]#交易日期
            date = datetime.strptime(tradeDate,'%Y-%m-%d').date()
            tradeRate = float(tradeRecord["fundValue"][index])#交易钱数
            indexOfList = 0
            #从净值列表中查找净值
            while date <= dicDateValue["fundDate"][-1] :
                if dicDateValue["fundDate"].count(date) == 1 :
                    indexOfList = dicDateValue["fundDate"].index(date)
                    break
                else:
                    date += timedelta(days=1)
            #找到了净值
            tradeUnitValueList += [dicDateValue["fundValue"][indexOfList]]
            tradeDateList += [date]
        return {"fundDate":tradeDateList,"fundValue":tradeUnitValueList,"tradeValue":tradeRecord["fundValue"]}
    #股市下午3点停盘，获取估计值
    def downloadExpectValue(self):
        #连接数据库
        db = pymysql.connect(Configure.mysqlHost, Configure.mysqlUser, Configure.mysqlPassword,
                             Configure.mysqlDatabase, charset=Configure.mysqlCharset)
        #获取操作游针
        cursor = db.cursor()
        #构造查询sql语句，获取最新的估计值
        selectStr = "SELECT * FROM expectValue WHERE fundID = 'jjjz_110003' ORDER BY scrawlDate DESC ,scrawlTime DESC "
        print("select sql:",selectStr)
        # 执行SQL语句
        cursor.execute(selectStr)
        results = cursor.fetchall()
        fundDate =results[0][1]
        fundValue = results[0][3]
        print( "expect date:%s,value:%f" % (fundDate,fundValue) )
        return {"fundDate":fundDate,"fundValue":fundValue}
        db.close()
    #分析估计值是近几天的最高，近几天的最低
    def parseExpectValue(self):
        #获取全部单位净值，日期升序
        dicDateValue = self.downloadData()
        #获取估计值
        expectDateValue = self.downloadExpectValue()
        #计算估计值是近几天的最低值
        index = -1
        changedDayly = 1.0 #较前一天变化
        changedbool = False #变化量计算标志位，False：还没计算，True：已经计算
        minDays = 0 #最小估值天数
        while expectDateValue["fundDate"] <= dicDateValue["fundDate"][index] :
            index -=1
        while expectDateValue["fundDate"] > dicDateValue["fundDate"][index] :
            if changedbool == False :
                changedbool = True
                changedDayly = (expectDateValue["fundValue"] - dicDateValue["fundValue"][index]) / dicDateValue["fundValue"][index] * 100
            if expectDateValue["fundValue"] <=  dicDateValue["fundValue"][index]:
                minDays +=1
            else:
                break;
            index -=1
        #计算估计值是近几天的最高值
        maxDays = 0 #最大估值天数
        index = -1
        while expectDateValue["fundDate"] <= dicDateValue["fundDate"][index] :
            index -=1
        while expectDateValue["fundDate"] > dicDateValue["fundDate"][index] :
            if expectDateValue["fundValue"] >=  dicDateValue["fundValue"][index]:
                maxDays +=1
            else:
                break;
            index -=1
        self.expectValueStr = "当前估计值：%.2f ,日变化幅度：%.2f %%，最小值天数：%d ,最大值天数：%d" \
                              % (expectDateValue["fundValue"],changedDayly,minDays,maxDays)
        print("最小值天数：",minDays,"最大值天数：",maxDays)
    #用估计值绘图，参照plotData
    #days绘制近days天的点
    def plotExpectValue(self,days = 6):
        netDateValue = self.downloadData()
        #根据时间选择数据,最近30天数据
        dayDelta = -1 * days#len(dicDateValue["fundValue"])
        #获取估计值
        expectDateValue = self.downloadExpectValue()
        # 移除日期大于等于估计值的数据
        print( type(netDateValue["fundDate"]),len( netDateValue["fundDate"] ) )
        while 1 <= len( netDateValue["fundDate"]  ):
            if netDateValue["fundDate"][-1] >= expectDateValue["fundDate"] :
                netDateValue["fundValue"].pop()
                netDateValue["fundDate"].pop()
                print( "len:",len( netDateValue["fundDate"]  ) )
            else:
                break;
        #加入估计值
        netDateValue["fundDate"].append(expectDateValue["fundDate"])
        netDateValue["fundValue"].append(expectDateValue["fundValue"])
        averageValue = np.mean(netDateValue["fundValue"][dayDelta:])
        df = pd.DataFrame({"fundValue:%.3f"%expectDateValue["fundValue"]:netDateValue["fundValue"][dayDelta:],
                           "averageValue:%.3f"%averageValue:averageValue },
                          netDateValue["fundDate"][dayDelta:]
                          )
        df.plot()
        plt.legend(loc='best')
        #plt.show()
        plt.savefig( self.imagePath + "/plot%ddays.png"%(days) )
    def sendEmail(self):
        #邮件发送配置
        my_sender=Configure.emailSender    # 发件人邮箱账号
        my_pass = Configure.emailPassword              # 发件人邮箱密码
        my_user=Configure.emailReceiver      # 收件人邮箱账号
        #设置邮件表头
        msgRoot = MIMEMultipart('related')
        msgRoot['From'] = formataddr(["基金分析小组",my_sender])
        msgRoot['To'] =  formataddr(["chenxi.pang",my_user])
        subject = '易方达上证50基金分析'
        msgRoot['Subject'] = Header(subject, 'utf-8')

        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        #构造html
        mail_msg = """
        <p>%s</p>
        <p>%s</p>
        <p>%s</p>
        <p>最近一周走势：</p>
        <p><img src="cid:image1"></p>
        <p>最近一月走势：</p>
        <p><img src="cid:image2"></p>
        """% (subject,self.expectValueStr,self.foundInfo)
        print(mail_msg)
        msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))
        # 指定图片为当前目录
        fp = open('./figure/plot7days.png', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        # 定义图片 ID，在 HTML 文本中引用
        msgImage.add_header('Content-ID', '<image1>')
        msgRoot.attach(msgImage)
        # 指定图片为当前目录
        fp = open('./figure/plot30days.png', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        # 定义图片 ID，在 HTML 文本中引用
        msgImage.add_header('Content-ID', '<image2>')
        msgRoot.attach(msgImage)
        server=smtplib.SMTP_SSL(Configure.emailSmtp, Configure.emailPort)  # 发件人邮箱中的SMTP服务器，端口是25
        # server=smtplib.SMTP("smtp.sina.com", 25)
        server.login(my_sender,my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender,[my_user,],msgRoot.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    def RunTactics(self):
        self.computeIncome()
        self.plotExpectValue(7)
        self.plotExpectValue(30)
        self.parseExpectValue()
        # self.sendEmail()
# ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))
# ts = ts.cumsum()
# plt.plot(ts)
# plt.show()
# tactics = FundTactics()
# tactics.RunTactics()
