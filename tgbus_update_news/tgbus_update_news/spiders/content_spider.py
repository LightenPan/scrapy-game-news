#!/usr/bin/env python
# encoding: utf-8

import scrapy
from tgbus_update_news.items import NewsContentItem
from hashlib import md5
import MySQLdb
import MySQLdb.cursors

import re

import logging
logger = logging.getLogger('tgbus_update_news')


class ContentSpider(scrapy.Spider):
	name = "tgbus_update_news"
	allowed_domains = ["tgbus.com"]
	start_urls = [
		'http://3ds.tgbus.com/news/',
		'http://nds.tgbus.com/news/',
		'http://psv.tgbus.com/news/',
		'http://psp.tgbus.com/news/',
		'http://wiiu.tgbus.com/news/',
		'http://ps4.tgbus.com/news/',
		'http://ps3.tgbus.com/news/',
		'http://xbox360.tgbus.com/news/',
		'http://xboxone.tgbus.com/news/',
	]

	def parse(self, response):
		#先获取最新的新闻列表
		alist = response.xpath('//div[contains(@class, "fl bc f14")]//a')
		linklist = []
		for sel in alist:
			link = ''.join(sel.xpath('@href').extract())
			if not re.match('.*Index.shtml.*', link):
				linklist.append(link)

		#获取内容
		for link in linklist:
			logger.info('get content from link: ' + link)
			yield scrapy.Request(link, callback=self.ContentParse, errback=self.errHandler)

	def ContentParse(self, response):
		item = NewsContentItem()
		item['link'] = response.url
		item['linkmd5id'] = md5(item['link']).hexdigest()

		title = response.xpath('//div[contains(@class, "content bdr")]/h1/text()').extract()
		item['title'] = ''.join(title).strip()

		#提取时间
		date = response.xpath('//li[contains(@class, "d")]/text()').extract()
		date = ''.join(date).strip()
		#去掉时间前面的汉字
		date = date.split('：')
		date = date[-1:]
		date = ''.join(date)
		#转化为时间戳
		import time
		item['date'] = time.mktime(time.strptime(date,"%Y/%m/%d %H:%M:%S"))
		# logger.info('date: ' + date)

		content = response.xpath('//div[contains(@class, "text")]/*').extract()
		item['content'] = ''.join(content)

		import time
		#timestamp是输入变量
		timestamp = item['date']
		show_datetime = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(timestamp))
		logger.info('finish get next content. link: %s, title: %s, date: %s, content_length: %u' % (item['link'], item['title'], show_datetime, len(item['content'])))
		return item

	def errHandler(self, failure):
		logger.error('errHandler: ' + str(failure))
