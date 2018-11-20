# -*- coding: utf-8 -*-
__author__ = 'Administrator'
import pymysql
import time
from lxml import etree
from mySpider import Configure
class ParseOfflineHtml():
    hour8Secs = 8 * 3600;#8小时是多少秒
    currentDate = time.strftime('%Y-%m-%d',time.gmtime(time.time()+hour8Secs) )#UTC+8时间
    currentTime = time.strftime('%H:%M:%S',time.gmtime(time.time()+hour8Secs) )
    # print("currentDate",currentDate,"current time:",currentTime)
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
parse = ParseOfflineHtml()
parse.parse("jjjz_110003.html")