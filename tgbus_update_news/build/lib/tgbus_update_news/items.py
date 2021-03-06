# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class NewsContentItem(scrapy.Item):
	linkmd5id = scrapy.Field()
	title = scrapy.Field()
	link = scrapy.Field()
	date = scrapy.Field()
	content = scrapy.Field()

class NewsListItem(scrapy.Item):
	link = scrapy.Field()
