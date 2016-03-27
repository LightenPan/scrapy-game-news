#!/usr/bin/env python
# encoding: utf-8

import scrapy
from scrapy.http import Request
from duowan_updated_news_list.items import NewsListItem
from hashlib import md5

import re

import logging
logger = logging.getLogger('duowan_updated_news_list')

class NewsListSpider(scrapy.Spider):
	name = "duowan_updated_news_list"
	allowed_domains = ["tv.duowan.com"]
	start_urls = [
		"http://tv.duowan.com/news/list/index.html",
	]
	list_url_prex = 'http://tv.duowan.com/news/list/'
	readed_pages = 0


	def parse(self, response):
		# 获取列表
		item = NewsListItem()
		for sel in response.xpath('//div[contains(@class, "news-filter-cont u-clearfix")]/ul/li'):
			title = sel.xpath('a[2]/@title').extract()
			link = sel.xpath('a[2]/@href').extract()

			title = ''.join(title)
			link = ''.join(link)


			matchObj = re.match('.*com.*', link)
			if not matchObj:
				link = 'http://tv.duowan.com' + link

			item['link'] = link
			logger.info('link: ' + link)
			yield item

		if self.readed_pages < 1:
			# 翻页
			page_title = sel.xpath('//div[contains(@id, "pageNum")]/span[last()]/a/text()').extract()
			page_title = ''.join(page_title)
			if u'下一页' == page_title:
				nextlink = sel.xpath('//div[contains(@id, "pageNum")]/span[last()]/a/@href').extract()
				nextlink = self.list_url_prex + ''.join(nextlink)
				logger.info("log next link: " + nextlink)
				yield Request(nextlink, callback=self.parse, errback=self.errHandler)
			self.readed_pages = self.readed_pages + 1
		else:
			#拉取列表结束，通知拉取内容任务开始
			#利用scrapyd服务进行调度
			#shell命令为: curl http://localhost:6800/schedule.json -d project=duowan_updated_news_content -d spider=duowan_updated_news_content
			logger.info('schedule duowan_updated_news_content')
			import urllib
			import urllib2
			req = urllib2.Request("http://localhost:6800/schedule.json",
					urllib.urlencode({"project":"duowan_updated_news_content","spider":"duowan_updated_news_content"}))
			resp = urllib2.urlopen(req)
			logger.info('schedule finish. resp: ' + resp.read())


	def errHandler(self, failure):
		logger.error('errHandler: ' + str(failure))
