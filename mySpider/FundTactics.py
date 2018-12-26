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
import platform
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
from mySpider.FundInfo import FundInfo

matplotlib.style.use('ggplot')
def isRightIndexOfList(list,index) :
    if len(list) == 0 :
        return False
    if index <0 :
        if len(list) >= index * -1 :
            return True
        else:
            return False
    else :
        if len(list) > index:
            return True
        else:
            return False
#用来分析基金净值的变化卖出份数
class FundTactics():
    #卖出手续费率有4个档，持有天数[0,7)，1.50%，[7,365)0.5%,[365,730)0.25%,[730,无穷)0%
    sellRateList = [0.985,0.995,0.9975,1.0]
    #图片保存路径
    imagePath = "./figure"

    def __init__(self):
        #输出构造信息
        print("FundTactics __init__()")
        #新建存储图片的路径
        if os.path.isdir(self.imagePath) == False :
            os.mkdir(self.imagePath)
        #存储全部日期的基金数据
        self.m_fundInfo = FundInfo()
    #从数据库中获取数据
    def plotData(self):
        #根据时间选择数据,最近30天数据
        days =  7
        dayDelta = -1 * days#len(dicDateValue["fundValue"])
        # currentDate = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        # (datetime.now() - timeDelta).strftime('%Y-%m-%d')
        averageValue = np.mean(self.m_fundInfo.fundValueList()[dayDelta:])
        df = pd.DataFrame({"fundValue":self.m_fundInfo.fundValueList()[dayDelta:],
                           "averageValue":averageValue },
                          self.m_fundInfo.fundDayList()[dayDelta:]
                          )
        df.plot()
        plt.legend(loc='best')
        tradeDateValue = self.m_fundInfo.m_tradeDateValue
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
        plt.savefig( self.imagePath + "/trade%ddays.png"%(days) )

    #分析估计值是近几天的最高，近几天的最低
    def parseExpectValue(self):
        #计算估计值是近几天的最低值
        index = -1
        changedDayly = 1.0 #较前一天变化
        changedbool = False #变化量计算标志位，False：还没计算，True：已经计算
        minDays = 0 #最小估值天数
        while isRightIndexOfList(self.m_fundInfo.fundDayList(),index) \
                and self.m_fundInfo.m_expectDateValue["fundDate"] <= self.m_fundInfo.fundDayList()[index] :
            index -=1
        while isRightIndexOfList(self.m_fundInfo.fundDayList(),index) \
                and self.m_fundInfo.m_expectDateValue["fundDate"] > self.m_fundInfo.fundDayList()[index] :
            if changedbool == False :
                changedbool = True
                changedDayly = (self.m_fundInfo.m_expectDateValue["fundValue"] - self.m_fundInfo.fundValueList()[index]) / \
                               self.m_fundInfo.fundValueList()[index] * 100
            if self.m_fundInfo.m_expectDateValue["fundValue"] <=  self.m_fundInfo.fundValueList()[index]:
                minDays +=1
            else:
                break;
            index -=1
        #计算估计值是近几天的最高值
        maxDays = 0 #最大估值天数
        index = -1
        while isRightIndexOfList(self.m_fundInfo.fundDayList(),index) \
                and self.m_fundInfo.m_expectDateValue["fundDate"] <= self.m_fundInfo.fundDayList()[index] :
            index -=1
        while isRightIndexOfList(self.m_fundInfo.fundDayList(),index) \
                and self.m_fundInfo.m_expectDateValue["fundDate"] > self.m_fundInfo.fundDayList()[index] :
            if self.m_fundInfo.m_expectDateValue["fundValue"] >=  self.m_fundInfo.fundValueList()[index]:
                maxDays +=1
            else:
                break;
            index -=1
        self.expectValueStr = "当前日期：%s,当前估计值：%.4f ,日变化幅度：%.2f %%，最小值天数：%d ,最大值天数：%d" \
                              % (self.m_fundInfo.m_expectDateValue["fundDate"],
                                 self.m_fundInfo.m_expectDateValue["fundValue"],changedDayly,minDays,maxDays)
        print("最小值天数：",minDays,"最大值天数：",maxDays)
    #用估计值绘图，参照plotData
    #days绘制近days天的点
    def plotExpectValue(self,days = 6):
        netDateValue = {"fundDate":self.m_fundInfo.fundDayList(),"fundValue":self.m_fundInfo.fundValueList()}
        #根据时间选择数据,最近30天数据
        dayDelta = -1 * days#len(dicDateValue["fundValue"])
        #获取估计值
        expectDateValue = self.m_fundInfo.m_expectDateValue
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
        print("expect date:",expectDateValue["fundDate"],"value:",expectDateValue["fundValue"])
        averageValue = np.mean(netDateValue["fundValue"][dayDelta:])
        fig = plt.figure()
        df = pd.DataFrame({"fundValue:%.3f"%expectDateValue["fundValue"]:netDateValue["fundValue"][dayDelta:],
                           "averageValue:%.3f"%averageValue:averageValue },
                          netDateValue["fundDate"][dayDelta:]
                          )
        df.plot()
        plt.legend(bbox_to_anchor=(0.5, -0.25),loc='lower center')
        # tradeDateValue = self.m_fundInfo.m_tradeDateValue
        tradeDateValue = self.m_fundInfo.recentTradeRecord(days)
        # print(tradeDateValue)
        #"red"表示买入，"green"表示卖出
        if len(tradeDateValue["fundValue"]) > 0 :
            plt.scatter(x=tradeDateValue["fundDate"],y=tradeDateValue["fundValue"],
                        s=30,c=tradeDateValue["colors"], alpha=0.5)
        plt.title('"red"-buy "green"-sell')
        if len(tradeDateValue["fundValue"]) > 0 :
            plt.table(cellText=[tradeDateValue["changeRate"]],
                          rowLabels=['changeRate(%)'],
                          colLabels=tradeDateValue["fundDate"],
                          loc='best')
        plt.subplots_adjust(left=0.2, bottom=0.2)
        # ax = plt.gca()
        # ax.spines['bottom'].set_color('none')
        # ax.spines['bottom'].set_position(('axes', 0.05))

        #fig.autofmt_xdate() # 自动旋转xlabel
        plt.savefig( self.imagePath + "/plot%ddays.png"%(days) )
        # plt.show()
    def sendEmail(self):
        sysstr = platform.system()
        if(sysstr =="Windows"):
            print ("Call Windows tasks")
            self.sendEmailWithSina()
        elif(sysstr == "Linux"):
            print ("Call Linux tasks")
            self.sendEmailWithPostfix()
        else :
            print("system error!")
    def sendEmailWithPostfix(self):
        #邮件发送配置
        my_sender="ccbang@2.ccbangpersonal.xyz"    # 发件人邮箱账号
        my_pass = "dig1221"              # 发件人邮箱密码
        my_user= Configure.emailReceiver      # 收件人邮箱账号
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
        """% (subject,self.expectValueStr,self.m_fundInfo.m_foundInfo)
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
        server = smtplib.SMTP("localhost")
        server.sendmail(my_sender,[my_user,],msgRoot.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    def sendEmailWithSina(self):
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
        """% (subject,self.expectValueStr,self.m_fundInfo.m_foundInfo)
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
        self.plotExpectValue(7)
        self.plotExpectValue(30)
        self.parseExpectValue()
        self.sendEmail()
# ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))
# ts = ts.cumsum()
# plt.plot(ts)
# plt.show()
# tactics = FundTactics()
# tactics.RunTactics()
