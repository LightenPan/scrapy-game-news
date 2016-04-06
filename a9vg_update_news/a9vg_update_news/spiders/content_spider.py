#!/usr/bin/env python
# encoding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import scrapy
from a9vg_update_news.items import ContentItem

import logging
logger = logging.getLogger('a9vg_update_news')

import re
import time
import urlparse

def extract_date(date):
    #一次处理找出日期、时间、事情三样信息
    pattern = re.compile("(?P<date>\d{4}/\d{1,2}/\d{1,2})\s+(?P<time>\d{1,2}:\d{1,2})")
    # pattern = re.compile("(?P<date>\d{4}/\d{1,2}/\d{1,2})\s+(?P<time>\d{1,2}:\d{1,2}:\d{1,2})")
    m = pattern.search(date)
    if m:
        return m.group('date') + " " + m.group('time')
    else:
        return ''


class ContentSpider(scrapy.Spider):
	name = "a9vg_update_news"
	allowed_domains = ["a9vg.com"]
	start_urls = [
		'http://www.a9vg.com/news/',
		'http://www.a9vg.com/news/index_2.html',
	]

	def parse(self, response):

		#先获取最新的新闻列表
		alist = response.xpath("//div[@class='list']/dl")
		linklist = []
		for item in alist:
			#链接
			link = item.xpath("dd/h4/a/@href").extract()
			link = ''.join(link)

			#标题
			title = item.xpath("dd/h4/a/text()").extract()
			title = ''.join(title)

			#缩略图
			thumbnail = item.xpath("dt/div/a/img/@src").extract()
			thumbnail = ''.join(thumbnail)

			item = {}
			item['link'] = link
			item['title'] = title
			item['thumbnail'] = thumbnail
			linklist.append(item)

		#获取内容
		for item in linklist:
			yield scrapy.Request(item['link'], meta={'item': item}, callback=self.ContentParse, errback=self.errHandler)

	def ContentParse(self, response):
		meta = response.meta['item']

		#获取标题
		title = response.xpath("//h1[@class='news-title']/text()").extract()
		title = ''.join(title)

		#获取内容
		content = response.xpath("//div[@class='article-body']").extract()
		meta['content'] = ''.join(content)

		#获取日期
		date = response.xpath("//span[@class='pos-time']/text()").extract()
		date = ''.join(date)
		# date = extract_date(date)

		item = ContentItem()
		item['link'] = meta['link']
		item['title'] = meta['title']
		item['date'] = time.mktime(time.strptime(date, "%Y-%m-%d %H:%M"))
		# item['thumbnail'] = meta['thumbnail']
		item['content'] = meta['content']

		logger.info('finish get content. link: %s, title: %s, date: %s, content_length: %u' % (item['link'], item['title'], date, len(item['content'])))
		return item

	def errHandler(self, failure):
		logger.error('errHandler: ' + str(failure))
