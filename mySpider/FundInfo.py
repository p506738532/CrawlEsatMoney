__author__ = 'Administrator'
'''
文件名：FundInfo.py
作用：基金数据类，包括每天的单位净值，交易记录
'''
import pymysql

from datetime import datetime
from datetime import date
from datetime import timedelta
import csv
from mySpider import Configure
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
#基金一天的数据，包括单位净值，预计值，交易净值等
class FundOneDay():
    m_date = datetime.strptime('1992-6-8','%Y-%m-%d').date()#日期，
    m_expectValue = -1.00   #估值，
    m_netValue = -1.00      #单位净值，
    m_tradeValue = 0.00       #交易金额，买入为+，卖出为-
    m_tradeCount = 0.00       #交易份数，买入为+，卖出为-
    m_keepCount = 0.00      #持有份额
#基金历史数据类，读取基金的交易日单位净值，一个基民的交易记录
class FundInfo():
    m_fundDays = [  ]#每天的基金点FundOneDay列表，日期升序
    dateCountList =[] #[日期,对应当日份额]列表
    def __init__(self):
        print("FundInfo() __init__")
        #从数据库获取单位净值
        self.downloadData()
        #从数据库获取估计净值
        self.downloadExpectValue()
        #获取交易记录
        self.readTradeRecord()
        #计算持有份额
        self.computeKeepCount()
        #再次读取交易记录
        self.tradeDateValue()
    #设置估计值
    def setExpectValue(self,date,value):
        for index in range( len( self.m_fundDays ) ):
            fundOneDay = self.m_fundDays[index]
            if self.m_fundDays[index].m_date == date:
                fundOneDay.m_expectValue = value
                self.m_fundDays[index] = fundOneDay
                break;
            if fundOneDay.m_date > date:
                expectFundOneDay = FundOneDay()
                expectFundOneDay.m_date = date
                expectFundOneDay.m_expectValue = value
                self.m_fundDays.insert(index,expectFundOneDay)
                break;
    #设置交易金额
    def setTradeValue(self,date,value):
        for index in range( len(self.m_fundDays) ):
            fundOneDay = self.m_fundDays[index]
            if self.m_fundDays[index].m_date == date:
                fundOneDay.m_tradeValue = value
                self.m_fundDays[index] = fundOneDay
                break;
            if fundOneDay.m_date > date:
                newFundOneDay = FundOneDay()
                newFundOneDay.m_date = date
                newFundOneDay.m_tradeValue = value
                self.m_fundDays.insert(index,newFundOneDay)
                break;
    #返回全部基金日期列表
    def fundDayList(self):
        dateList = []
        for fundOneDay in self.m_fundDays:
            if fundOneDay.m_netValue > 0 :
                dateList += [fundOneDay.m_date]
        return dateList
    #返回全部基金单位净值列表
    def fundValueList(self):
        unitNetList = []
        for fundOneDay in self.m_fundDays:
            if fundOneDay.m_netValue > 0 :
                unitNetList += [fundOneDay.m_netValue]
        return unitNetList
    #返回date这天的单位净值,如果这天是休息日，则向后查找工作日
    def fundUnitValue(self,date):
        indexOfList = -1
        #从净值列表中查找净值
        while date <= self.m_fundDays[-1].m_date :
            if self.fundDayList().count(date) == 1 :
                indexOfList = self.fundDayList().index(date)
                break
            else:
                date += timedelta(days=1)
        #找到了净值
        return self.fundValueList()[indexOfList]
    #下载净值数据，按日期升序排列
    def downloadData(self):
        self.m_fundDays.clear()
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
        for row in results:
            fundOneDay = FundOneDay()
            fundOneDay.m_date = row[0]
            fundOneDay.m_netValue = row[1]
            self.m_fundDays += [fundOneDay]
            # print( "date:%s,value:%f" % (fundDate,fundValue) )
        db.close()
    #下载估计净值
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
        db.close()
        self.setExpectValue(fundDate,fundValue)
        self.m_expectDateValue = {"fundDate":fundDate,"fundValue":fundValue}#最新估计日期
        return {"fundDate":fundDate,"fundValue":fundValue}

    #从csv文件中读取交易记录，日期升序排列
    def readTradeRecord(self):
        filename = 'tradeRecord.csv'
        with open(filename) as f:
            reader = csv.reader(f)
            fundDateList = []
            fundValueList = []
            for row in reader:
                fundDate=datetime.strptime(row[0],'%Y-%m-%d').date()
                fundValue=float(row[1])
                fundDateList += [fundDate]
                fundValueList += [fundValue]
                self.setTradeValue(fundDate,fundValue)
            self.m_tradeRecord = {"fundDate":fundDateList,"fundValue":fundValueList}
    #近days天(从1开始），净买入的钱数
    def BuyCountRecentDays(self,days):
        buyCount = 0.0 #购买金额初始化
        if days == 0 :
            return buyCount

        for fundOneDay in self.m_fundDays[days*-1:]:
            buyCount += fundOneDay.m_tradeValue
        return buyCount
    #计算持有份额
    '''
    定投收益分析，买入手续费0.15%，卖出手续费0.5%,三天单位收益分别为15,5,10，前两天定投100元，第三天卖出，求收益率。
    买入份额=100*0.9985/15+100*0.9985/5
    卖出的钱=买入份额*0.995*10=205.36
    收益率=5.36/200=2.68%
    '''
    def computeKeepCount(self):
        buyRate = 1.0  #0.9985
        fundCount = 0.0  #持有份数
        sellMoney = 0.0#卖出基金得到的钱
        buyMoney = 0.0#买基金花的钱
        #全局变量清零
        self.dateCountList.clear()
        #遍历交易记录
        for index in range(len(self.m_fundDays ) ):
            tradeDate = self.m_fundDays[index].m_date#交易日期
            tradeRate = float(self.m_fundDays[index].m_tradeValue)#交易钱数
            if tradeRate == 0 :
                continue
            #找到了净值
            fundValue = self.fundUnitValue(tradeDate)
            #交易的份额
            sellCount = 0
            if tradeRate <0 :#卖出
                tradeRate *= -1
                fundLeftValue = tradeRate#交易的钱数
                while fundLeftValue > 0 :
                    #交易的费率
                    sellRate = self.sellRate(tradeDate)
                    #判断是否卖光了这一天的份额
                    if fundLeftValue > float(self.dateCountList[0][1]*fundValue*sellRate) :
                        fundLeftValue -= float(self.dateCountList[0][1]*fundValue*sellRate)
                        fundCount -= self.dateCountList[0][1]#卖出的份数
                        sellCount += self.dateCountList[0][1]
                        # print("交易日期",tradeDate,"卖出日期：",self.dateCountList[0][0],"卖出份额：",self.dateCountList[0][1])
                        del self.dateCountList[0]
                    #卖光了接着卖下一天的份额
                    else :
                        #计算卖出的份数
                        fundCount -= fundLeftValue/sellRate/fundValue
                        self.dateCountList[0][1] -= fundLeftValue/sellRate/fundValue
                        sellCount+=fundLeftValue/sellRate/fundValue
                        # print("卖出日期：",self.dateCountList[0][0],"剩余份额：",self.dateCountList[0][1])
                        fundLeftValue = 0
                sellMoney += tradeRate
                self.m_fundDays[index].m_tradeCount = sellCount * -1 #这天卖出的份额
                # print("卖出的钱",tradeRate,"卖出份",sellCount,"单位净值",fundValue,"成交日期",tradeDate)
            else:#买入
                fundCount += tradeRate*buyRate/fundValue#买入的份数
                buyMoney += tradeRate
                self.dateCountList.append([tradeDate,tradeRate*buyRate/fundValue])
                self.m_fundDays[index].m_tradeCount = tradeRate*buyRate/fundValue #保存这天买入的份数
                #  sellCount = -1 * tradeRate*buyRate/fundValue#买入的份数test
            self.m_fundDays[index].m_keepCount = fundCount #保存这天的持有份额
        # 持仓成本=投入的钱数/持有份额，与支付宝计算有偏差，不知道它怎么算的
        self.latestValue = self.fundValueList()[-1]
        print("持有份额:",fundCount,"持有市值:",self.latestValue * fundCount,"持仓成本:",
              (buyMoney - sellMoney)/fundCount)
        #持有时长大于7天的份额
        self.countLonger7 = self.keepTimeLonger7(date.today())
        print("现金投入：",buyMoney - sellMoney )
        self.m_foundInfo = """持有时长大于7天的份额%.2f
        持有总份额:%d , 最新净值：%.4f(%s),持有市值:%.2f ,持仓成本:%.2f，现金投入：%.2f ,近30天现金投入：%.2f， 累计收益：%.2f
        """ % (self.countLonger7,fundCount,self.latestValue,self.fundDayList()[-1],self.latestValue * fundCount,
               (buyMoney - sellMoney)/fundCount,buyMoney - sellMoney ,
        self.BuyCountRecentDays(30),self.latestValue * fundCount + sellMoney - buyMoney )

    #测试数据读取是否正确
    def printData(self,sellCount):
        self.logFile = open("test.log", "w")
        # for fundOneDay in self.m_fundDays:
        #     file.write(
        #         "%s,date:%s,expectValue:%.2f ,netValue:%f,tradeValue:%.2f,tradeCount:%.2f,keeyCount:%.2f \n " %
        #         (type(fundOneDay.m_date),fundOneDay.m_date,fundOneDay.m_expectValue,fundOneDay.m_netValue,
        #          fundOneDay.m_tradeValue,fundOneDay.m_tradeCount,fundOneDay.m_keepCount)
        #     )
        for oDateCount in self.dateCountList:
            self.logFile.write( "sellCount:%.2f,date:%s,count:%.2f\r\n" % (sellCount,oDateCount[0],oDateCount[1]) )
    #求卖出时的卖出费率；date:卖出日期
    def sellRate(self,date):
        #卖出手续费率有4个档，持有天数[0,7)，1.50%，[7,365)0.0%,[365,730)0.0%,[730,无穷)0%
        sellRateList = [0.985, 1.0, 1.0, 1.0]
        if len(self.dateCountList) == 0:
            print("error: sell error.len(self.dateCountList) = %f " % len(self.dateCountList) )
        keepTime = (date - self.dateCountList[0][0])/timedelta(days=1) #持有时间
        if  keepTime >= 730 :
            return sellRateList[3]
        elif keepTime >= 365 :
            return sellRateList[2]
        elif keepTime >= 7:
            return sellRateList[1]
        else:
            # print("警告：费率太高！")
            return sellRateList[0]
    #持有时长大于7天的份数
    def keepTimeLonger7(self,currentDate):
        countTotal = 0;#持有时长大于7天的份数
        for dateCount in self.dateCountList:
            if (currentDate - dateCount[0])/timedelta(days=1) >= 7:
                countTotal += dateCount[1]
        print("持有时长大于7天份额：",countTotal)
        self.m_longer7Str = "持有时长大于7天份额：%.2f"%(countTotal)
        return countTotal
    def tradeDateValue(self):
        #读取交易记录
        tradeRecord = self.m_tradeRecord
        tradeDateList = []#交易日期列表
        tradeUnitValueList = []#交易单位净值列表
        #遍历交易记录
        for index in range(len(tradeRecord["fundDate"] ) ):
            tradeDate = tradeRecord["fundDate"][index]#交易日期
            date = tradeDate
            tradeRate = float(tradeRecord["fundValue"][index])#交易钱数
            indexOfList = 0
            #从净值列表中查找净值
            while date <= self.fundDayList()[-1] :
                if self.fundDayList().count(date) == 1 :
                    indexOfList = self.fundDayList().index(date)
                    break
                else:
                    date += timedelta(days=1)
            #找到了净值
            tradeUnitValueList += [self.fundValueList()[indexOfList]]
            tradeDateList += [date]
        self.m_tradeDateValue = {"fundDate":tradeDateList,"fundValue":tradeUnitValueList,
                                 "tradeValue":tradeRecord["fundValue"]}
        # return {"fundDate":tradeDateList,"fundValue":tradeUnitValueList,"tradeValue":tradeRecord["fundValue"]}
    #最近days天的交易记录
    def recentTradeRecord(self,days):
        fundDate = []
        tradeValue = []
        colors = []
        fundValue = []
        changeRate = []
        for index in range( 1,len(self.m_fundDays) ):
            index *= -1
            fundOneDay = self.m_fundDays[index]
            #卖出
            if fundOneDay.m_tradeCount < 0 :
                fundDate += [fundOneDay.m_date]
                tradeValue+=[fundOneDay.m_tradeCount*-1]
                colors += ["green"]
                fundValue += [fundOneDay.m_netValue]
                changeRate +=["%.2f%%" % ( (self.m_expectDateValue["fundValue"]- fundOneDay.m_netValue)
                                         /fundOneDay.m_netValue*100)]
                #print(fundOneDay.m_tradeCount)
            #买入
            elif fundOneDay.m_tradeCount > 0 :
                fundDate += [fundOneDay.m_date]
                tradeValue+=[fundOneDay.m_tradeCount]
                colors += ["red"]
                fundValue += [fundOneDay.m_netValue]
                changeRate +=["%.2f%%" % ( (self.m_expectDateValue["fundValue"]- fundOneDay.m_netValue)
                                         /fundOneDay.m_netValue*100) ]
                #print(fundOneDay.m_tradeCount)
            days -= 1
            if days == 0:
                break;
        #列表元素反向
        fundDate.reverse()
        tradeValue.reverse()
        colors.reverse()
        fundValue.reverse()
        changeRate.reverse()
        return {"fundDate":fundDate,"tradeValue":tradeValue,
                "colors":colors,"fundValue":fundValue,
                "changeRate":changeRate}
# fundInfo.printData()