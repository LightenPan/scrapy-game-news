#!/usr/bin/env python
# encoding: utf-8

import scrapy
from mduowan_update_news.items import ContentItem

import logging
logger = logging.getLogger('mduowan_update_news')

import time
import urlparse

class ContentSpider(scrapy.Spider):
	name = "mduowan_update_news"
	allowed_domains = ["duowan.com", "duowan.cn"]
	start_urls = [
		'http://ps4.duowan.cn/',
		'http://psv.duowan.cn/',
		'http://3ds.duowan.cn/',
		'http://tv.duowan.cn/',
		'http://x1.duowan.com/',
	]

	netloc_map = {
			'ps4.duowan.com' : 'ps4.duowan.cn',
			'psv.duowan.com' : 'psv.duowan.cn',
			'3ds.duowan.com' : '3ds.duowan.cn',
			'tv.duowan.com' : 'tv.duowan.cn',
			'x1.duowan.com' : 'x1.duowan.cn',
			'wiiu.duowan.com' : 'wiiu.duowan.cn',
			'ps4.duowan.cn' : 'ps4.duowan.cn',
			'psv.duowan.cn' : 'psv.duowan.cn',
			'3ds.duowan.cn' : '3ds.duowan.cn',
			'tv.duowan.cn' : 'tv.duowan.cn',
			'x1.duowan.cn' : 'x1.duowan.cn',
			'wiiu.duowan.cn' : 'wiiu.duowan.cn',
			}

	def parse(self, response):

		#先获取最新的新闻列表
		alist = response.xpath("//div[@class='channel-list clearfix']/ul/li")
		linklist = []
		for item in alist:
			#链接
			link = item.xpath("div/a/@href").extract()
			link = ''.join(link)
			res = urlparse.urlparse(link)
			if res.netloc:
				link = 'http://' + self.netloc_map[res.netloc] + res.path
			else:
				link = response.url + res.path

			#标题
			title = item.xpath("p/a/text()").extract()
			title = ''.join(title)

			#日期
			date = item.xpath("span/text()").extract()
			date = ''.join(date)
			date = date[1:-1]

			#缩略图
			thumbnail = item.xpath("div/a/img/@src").extract()
			thumbnail = ''.join(thumbnail)

			item = {}
			item['link'] = link
			item['title'] = title
			item['date'] = date
			item['thumbnail'] = thumbnail
			linklist.append(item)
			# logger.info('item: ' + str(item))

		#获取内容
		# user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
		# headers = { 'User-Agent' : user_agent }
		for item in linklist:
			# logger.info('get content from link: ' + item['link'])
			yield scrapy.Request(item['link'], meta={'item': item}, callback=self.ContentParse, errback=self.errHandler)
			# yield scrapy.Request(item['link'], meta={'item': item}, headers=headers, callback=self.ContentParse, errback=self.errHandler)

	def ContentParse(self, response):
		meta = response.meta['item']

		content = response.xpath('//article').extract()
		meta['content'] = ''.join(content)

		item = ContentItem()
		item['link'] = meta['link']
		item['title'] = meta['title']
		item['date'] = time.mktime(time.strptime(meta['date'], "%Y/%m/%d %H:%M:%S"))
		# item['thumbnail'] = meta['thumbnail']
		item['content'] = meta['content']

		logger.info('finish get content. link: %s, title: %s, date: %s, content_length: %u' % (item['link'], item['title'], meta['date'], len(item['content'])))
		return item

	def errHandler(self, failure):
		logger.error('errHandler: ' + str(failure))
