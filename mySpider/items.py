# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MyspiderItem(scrapy.Item):
    name = scrapy.Field()
    level = scrapy.Field()
    info = scrapy.Field()

class ItcastItem(scrapy.Item):
    name = scrapy.Field()
    level = scrapy.Field()
    info = scrapy.Field()
    title = scrapy.Field()

class EasyMoneyItem(scrapy.Item):
    name = scrapy.Field()
    detailLink = scrapy.Field()
    positionInfo = scrapy.Field()
    peopleNumber = scrapy.Field()
    workLocation = scrapy.Field()
    publishTime = scrapy.Field()