# -*- coding: utf-8 -*-
import scrapy
#scrapy crawl easymoney
from  mySpider.items import EasyMoneyItem
from mySpider.ParseOfflineHtml import ParseOfflineHtml
from mySpider.FundTactics import FundTactics
class EasymoneySpider(scrapy.Spider):
    name = 'easymoney'
    allowed_domains = ['eastmoney.com']
    start_urls = ['http://fundf10.eastmoney.com/jjjz_110003.html']

    def parse(self, response):
        fileName = "jjjz_110003.html"
        with open(fileName, "w", encoding='utf-8') as f:
            f.write(response.text)
        parseHtml = ParseOfflineHtml()
        parseHtml.parse(fileName)
        tactics = FundTactics()
        tactics.RunTactics()
