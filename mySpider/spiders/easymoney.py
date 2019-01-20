# -*- coding: utf-8 -*-
import scrapy
#scrapy crawl easymoney
from  mySpider.items import EasyMoneyItem
from mySpider.ParseOfflineHtml import ParseOfflineHtml
from mySpider.FundTactics import FundTactics
import os
from mySpider import GlobalVariant
class EasymoneySpider(scrapy.Spider):
    name = 'easymoney'
    allowed_domains = ['fund.eastmoney.com']
    start_urls = ['http://fund.eastmoney.com/fundguzhi.html']
    def __init__(self):
        #判断是否存在html文件夹，没有就创建
        self.m_htmlPath = GlobalVariant.m_htmlPath
        if os.path.isdir(self.m_htmlPath) == False :
            os.mkdir(self.m_htmlPath)
    def parse(self, response):
        fileName = self.m_htmlPath + "/fundguzhi.html"
        with open(fileName, "w", encoding='utf-8') as f:
            f.write(response.text)
        parseHtml = ParseOfflineHtml()
        # parseHtml.parse(fileName)
        # tactics = FundTactics()
        # tactics.RunTactics()
