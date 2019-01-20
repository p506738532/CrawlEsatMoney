# -*- coding: utf-8 -*-
__author__ = 'Administrator'
'''
文件名：ParseOfflineHtml.py
作用：利用xpath工具解析Html文件，获取其中的单位净值和估计值。将获取到的值上传的Mysql数据库中。
'''
import pymysql
import time
from lxml import etree
from mySpider import Configure
from mySpider import GlobalVariant
#判断是否为数字
def IsNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
class ParseOfflineHtml():
    hour8Secs = 8 * 3600;#8小时是多少秒
    currentDate = time.strftime('%Y-%m-%d',time.gmtime(time.time()+hour8Secs) )#UTC+8时间
    currentTime = time.strftime('%H:%M:%S',time.gmtime(time.time()+hour8Secs) )
    fileName = GlobalVariant.m_htmlPath + "/fundguzhi.html"
    def __init__(self):
        #判断eastmoney数据库是否存在
        self.createDB()
        #创建数据表
        self.createAllTable()
        #插入数据
        self.InsertFundData(self.fileName)

    #创建全部数据表
    def createAllTable(self):
        #创建表
        self.createFundInfoTable()
        self.createExpectTable()
        self.createNAVTable()
    #判断数据库是否存在，存在不做任何操作，不存在则创建
    def createDB(self):
        #连接数据库
        db = pymysql.connect( Configure.mysqlHost, Configure.mysqlUser, Configure.mysqlPassword,
                              charset=Configure.mysqlCharset )
        #获取操作游针
        cursor = db.cursor()
        # 执行SQL语句
        cursor.execute("show databases")
        results = cursor.fetchall()
        dbExistBool = False
        for dbOne in results:
            dbName = "%2s" % dbOne#??%2s
            if dbName == Configure.mysqlDatabase:
                dbExistBool = True
        if  dbExistBool :
            pass
        else:
            #创建数据库
            creatDBSql = "create database `%s`" % (Configure.mysqlDatabase)
            print("creatDBSql",creatDBSql)
            cursor.execute( creatDBSql )
        db.commit()
        db.close()
    #判断allfundinfo数据表是否存在,返回True，存在；返回False，不存在
    def checkTableExists(self):
        #连接数据库
        db = pymysql.connect( Configure.mysqlHost, Configure.mysqlUser, Configure.mysqlPassword,
                             Configure.mysqlDatabase, charset=Configure.mysqlCharset )
        #获取操作游针
        cursor = db.cursor()
        # 执行SQL语句
        cursor.execute("SHOW TABLES like 'allfundinfo'")
        # 关闭数据库连接
        db.close()
        results = cursor.fetchall()
        if len(results) >0 :
            print("exists allfundinfo")
            return True
        else :
            print("not exists allfundinfo")
            return False

    #创建全部基金数据表
    def createFundInfoTable(self):
        #连接数据库
        db = pymysql.connect( Configure.mysqlHost, Configure.mysqlUser, Configure.mysqlPassword,
                             Configure.mysqlDatabase, charset=Configure.mysqlCharset )
        #获取操作游针
        cursor = db.cursor()
        creatSql = '''
    CREATE TABLE IF NOT EXISTS `allfundinfo` (
  `fundCode` varchar(10) DEFAULT NULL,
  `fundName` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`fundCode`)
) ENGINE=InnoDB DEFAULT CHARSET=gbk;
'''
        # 执行SQL语句
        cursor.execute(creatSql)
        # 提交到数据库执行
        db.commit()
        # 关闭数据库连接
        db.close()
    #创建历史净值数据表
    def createNAVTable(self):
        #连接数据库
        db = pymysql.connect( Configure.mysqlHost, Configure.mysqlUser, Configure.mysqlPassword,
                             Configure.mysqlDatabase, charset=Configure.mysqlCharset )
        #获取操作游针
        cursor = db.cursor()
        creatSql = '''
    CREATE TABLE IF NOT EXISTS `nav` (
  `fundCode` varchar(10) NOT NULL,
  `fundDate` date DEFAULT NULL,
  `netAssetValue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=gbk;
'''
        # 执行SQL语句
        cursor.execute(creatSql)
        # 提交到数据库执行
        db.commit()
        # 关闭数据库连接
        db.close()
    '''
    创建最新估值数据表
    表名：expectvalue
    '''
    def createExpectTable(sel):
        #连接数据库
        db = pymysql.connect( Configure.mysqlHost, Configure.mysqlUser, Configure.mysqlPassword,
                             Configure.mysqlDatabase, charset=Configure.mysqlCharset )
        #获取操作游针
        cursor = db.cursor()
        creatSql = '''
        CREATE TABLE IF NOT EXISTS `expectvalue` (
  `fundCode` varchar(10) NOT NULL,
  `scrawlDate` date DEFAULT NULL,
  `scrawlTime` time DEFAULT NULL,
  `expectUnitValue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=gbk;
'''
        # 执行SQL语句
        cursor.execute(creatSql)
        # 提交到数据库执行
        db.commit()
        # 关闭数据库连接
        db.close()
    #解析http://fund.eastmoney.com/fundguzhi.html基金估值页面，得到
    def InsertFundData(self,htmlFilePath):
        #连接数据库
        db = pymysql.connect( Configure.mysqlHost, Configure.mysqlUser, Configure.mysqlPassword,
                             Configure.mysqlDatabase, charset=Configure.mysqlCharset )
        #获取操作游针
        cursor = db.cursor()
        with open(htmlFilePath, "r", encoding='utf-8') as readFile:
            htmxText = readFile.read()
            page = etree.HTML(htmxText)
            #test
            # print(htmxText[:500])
            #获取 估算日期
            expectDateR = "//*[contains(text(),'估算数据')]"
            eDStr = page.xpath(expectDateR)[0].text
            #print("expect rule:",eDStr)
            eDate = eDStr[0:eDStr.find(" ")]
            #获取 净值日期
            netDateR = "//a[contains(text(),'单位净值')]/.."
            nDStr = page.xpath(netDateR)[0].text
            # print("nDStr",nDStr)
            #获取基金总数
            fCountR = "//a[contains(text(),'档案')]"
            fundCount = len( page.xpath(fCountR) )
            #print('fundCount',fundCount)
            #获取 基金代码
            fCodeR = "//a[contains(text(),'档案')]/../../td[3]"
            fCodeStrList = page.xpath(fCodeR)
            #获取 基金名称
            fNameR = "//a[contains(text(),'档案')]/../../td[4]/a[1]"
            fNameStrList = page.xpath(fNameR)
            #获取 估算数据
            eValueR = "//a[contains(text(),'档案')]/../../td[5]"
            eValueStrLst = page.xpath(eValueR)
            #获取 单位净值
            netValueR = "//a[contains(text(),'档案')]/../../td[10]"
            netValueStrList = page.xpath(netValueR)
            updateExpectTable = [] #估计值表格数据
            updateNavTable = [] #单位净值表格数据
            updateFundInfoTable = [] #基金编号表格
            insertExpectTable = [] #估计值表格数据
            insertNavTable = [] #单位净值表格数据
            fundInfoTable = [] #
            navExistCode = [] #今天nav表已有基金编码列表
            #根据基金编码和日期查找nav表已有的数据
            selectNAVStr = "select * from nav where fundDate = '%s'" % nDStr
            cursor.execute(selectNAVStr)
            results = cursor.fetchall()
            for rOneRow in results:
                navExistCode += [rOneRow[0]]
            allfundinfoExistCode = []
            #查找allfundinfo表已有的数据
            selectAllFunInfoStr = "select * from allfundinfo"
            cursor.execute(selectAllFunInfoStr)
            results = cursor.fetchall()
            for rOneRow in results:
                allfundinfoExistCode += [rOneRow[0]]
            #查找expectvalue表已有的数据
            expectValueExistCode = []
            selectExpectValueStr = "SELECT * FROM expectvalue WHERE scrawlDate = '%s' and scrawlTime = '%s'" \
                                   % (eDate,self.currentTime)
            #print("selectExpectValueStr+"+selectExpectValueStr)
            cursor.execute(selectExpectValueStr)
            results = cursor.fetchall()
            for rOneRow in results:
                expectValueExistCode += [rOneRow[0]]
            #根据主键查找估值表
            #根据主键查找净值表
            for index in range(fundCount):#fundCount
                #print("index",index)
                #基金代码
                fCodeStr = fCodeStrList[index].text
                fCodeStr = fCodeStr.replace(" ","").replace("\r","").replace("\n","")
                #print('fCodeStr：'+fCodeStr)
                #基金名称
                fNameStr = fNameStrList[index].text
                # print('fNameStr',fNameStr)
                #估算数据
                eValue = 0.0
                if IsNumber(eValueStrLst[index].text):
                    eValue = eValueStrLst[index].text
                # else:
                #     print(eValueStrLst[index].text)
                #print("eValueStr type",type(eValue) )
                eValue = eValue.replace(" ","").replace("\r","").replace("\n","")
                #print('eValueStr',eValue)
                #获取 单位净值
                netValueStr = 0.0
                if IsNumber(netValueStrList[index].text):
                    netValueStr = netValueStrList[index].text
                # else:
                #     print(netValueStrList[index].text)
                # print('netValueStr',netValueStr)
                netValueStr = netValueStr.replace(" ","").replace("\r","").replace("\n","")
                if expectValueExistCode.count(fCodeStr) > 0:
                    updateExpectTable +=[(fCodeStr,eDate,self.currentTime,eValue)]
                else:
                    insertExpectTable += [(fCodeStr,eDate,self.currentTime,eValue)]
                if navExistCode.count(fCodeStr) > 0:
                    updateNavTable+= [(fCodeStr,nDStr,netValueStr)]
                else:
                    insertNavTable += [(fCodeStr,nDStr,netValueStr)]
                if allfundinfoExistCode.count(fCodeStr) > 0:
                    updateFundInfoTable+=[(fCodeStr,fNameStr)]
                else:
                    fundInfoTable+=[(fCodeStr,fNameStr)]
            #批量插入期望值
            sql = "INSERT INTO expectvalue(fundCode,scrawlDate,scrawlTime,expectUnitValue)" \
                  " VALUES(%s,%s,%s,%s)"
            cursor.executemany(sql,insertExpectTable)
            #更新期望值数据xx
            #sql = "UPDATE expectvalue SET Address = 'Zhongshan 23', City = 'Nanjing' WHERE fundCode = 'Wilson'"
            #批量插入单位净值
            sql = "INSERT INTO nav(fundCode,fundDate,netAssetValue)" \
                  " VALUES(%s,%s,%s)"
            cursor.executemany(sql,insertNavTable)
            #插入基金信息表
            sqlSelect = "select * from allfundinfo"
            cursor.execute(sqlSelect)
            results = cursor.fetchall()
            if len(results) < 1:
                #插入基金信息
                sql = "INSERT INTO allfundinfo(fundCode,fundName)" \
                  " VALUES(%s,%s)"
                cursor.executemany(sql,fundInfoTable)

            # 提交到数据库执行
            db.commit()
            # 关闭数据库连接
            db.close()
        print('fundCount',fundCount)
    def parse(self,htmlFilePath):
        with open(htmlFilePath, "r", encoding='utf-8') as readFile:
            page = etree.HTML(readFile.read())
            #p class="row row1"/<div class="col-right">/label
            dateRule = "//div[contains(@class,'basic-new')]/div[contains(@class,'bs_jz')]" \
                        "/div[contains(@class,'col-right')]/p[contains(@class,'row row1')]" \
                        "/label"
            dateStr = page.xpath(dateRule)[1].text
            currentYear = time.strftime('%Y-',time.gmtime(time.time()) )
            dateValue = currentYear+dateStr[dateStr.rfind("（")+1:dateStr.find("）")]
            #<b class="red lar bold">
            valueRule= dateRule + "/b"
            exceptRule = "//span[@id='fund_gsz']"#从html中查找盘中估值
            netAssetStr = page.xpath(valueRule)[0].text
            netAssetValue = float( netAssetStr[0:netAssetStr.find("(")])
            exceptValue = float(page.xpath(exceptRule)[0].text) #估计净值
            print("date:",dateValue)
            print("netAssetValue:",netAssetValue)
            print("exceptValue:",exceptValue)
            self.uploadDataBase(dateValue,netAssetValue)
            self.uploadExpectValEue(exceptValue)
    def uploadDataBase(self,fundDate,netAssetValue):
        #连接数据库
        db = pymysql.connect( Configure.mysqlHost, Configure.mysqlUser, Configure.mysqlPassword,
                             Configure.mysqlDatabase, charset=Configure.mysqlCharset )
        #获取操作游针
        cursor = db.cursor()
        #构造查询sql语句
        selectStr = "select * from jjjz_110003 where FundDate = '%s'" % (fundDate)
        print("select sql:",selectStr)
        # 执行SQL语句
        cursor.execute(selectStr)
        results = cursor.fetchall()
        if len(results) == 0 :
            #查询不到该日信息，可以插入数据
            insertStr = "INSERT INTO jjjz_110003 (FundDate,netAssetValue) VALUES ('%s',%f)"\
                        % ( fundDate, netAssetValue )
            print(insertStr)
            cursor.execute(insertStr)
            # 提交到数据库执行
            db.commit()
        else :
            #查询到了结果，更新数据
            updateStr = "UPDATE jjjz_110003 SET netAssetValue = %f WHERE FundDate = '%s' "\
             %( netAssetValue,fundDate )
            print(updateStr)
            cursor.execute(updateStr)
            # 提交到数据库执行
            db.commit()
        # 关闭数据库连接
        db.close()
    #上传估计净值
    def uploadExpectValEue(self,expectValue):
        #连接数据库
        db = pymysql.connect(Configure.mysqlHost, Configure.mysqlUser, Configure.mysqlPassword,
                             Configure.mysqlDatabase, charset=Configure.mysqlCharset )
        #获取操作游针
        cursor = db.cursor()
        #构造查询sql语句
        selectStr = "select * from expectValue where fundID = '%s' AND scrawlDate = '%s' " \
                    " AND scrawlTime = '%s' " % ('jjjz_110003',self.currentDate,self.currentTime)
        print("select sql:",selectStr)
        # 执行SQL语句
        cursor.execute(selectStr)
        results = cursor.fetchall()
        if len(results) == 0 :
            #查询不到该日信息，可以插入数据
            insertStr = "INSERT INTO expectValue (fundID,scrawlDate,scrawlTime,expectUnitValue) " \
                        "VALUES ('%s','%s','%s',%f)"\
                        % ( 'jjjz_110003', self.currentDate,self.currentTime,expectValue )
            print(insertStr)
            cursor.execute(insertStr)
            # 提交到数据库执行
            db.commit()
        else :
            #查询到了结果，更新数据
            updateStr = "UPDATE expectValue SET expectUnitValue = %f WHERE fundID = '%s' AND scrawlDate = '%s' " \
                        " AND scrawlTime = '%s' "\
             %( expectValue,'jjjz_110003',self.currentDate,self.currentTime )
            print(updateStr)
            cursor.execute(updateStr)
            # 提交到数据库执行
            db.commit()
        # 关闭数据库连接
        db.close()
# parse = ParseOfflineHtml()