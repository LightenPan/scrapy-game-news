#!/usr/bin/env python
# encoding: utf-8

import scrapy
from duowan_updated_news_content.items import DuoWanItem
from hashlib import md5
import MySQLdb
import MySQLdb.cursors

import re

import logging
logger = logging.getLogger('duowan_updated_news_content')


class NewsContentSpider(scrapy.Spider):
	name = "duowan_updated_news_content"
	allowed_domains = ["tv.duowan.com"]
	start_urls = []

	conn= MySQLdb.connect(
		host='localhost',
		port = 3306,
		user='GameHeadLine',
		passwd='111111',
		db ='GameHeadLine',
		charset='utf8',
		)
	cur = conn.cursor()

	sqlExecute = "select link from t_duowan_update_news_list"
	logger.info("sqlExecute: " + sqlExecute)
	recordset = cur.execute(sqlExecute)
	rows = cur.fetchmany(recordset)
	for row in rows:
		link = row[0]
		if re.match(r'.*bbs.*', link):
			logger.info('no need process bbs link. link: ' + link)
			print 'no need process bbs link. link: ' + link
		else:
			start_urls.append(link)

	def parse(self, response):
		item = DuoWanItem()
		item['link'] = response.url
		item['linkmd5id'] = md5(response.url).hexdigest()
		title = response.xpath('//div[@class="mod-crumb-bd"]|//div[@class="tvPage__main"]/h1|//div[@class="article"]/h1[1]')[0].xpath('//h1/text()').pop().extract()
		item['title'] = ''.join(title).strip()

		#日期
		publicTime = response.xpath('//address/span[1]/text()').extract()
		publicTime = ''.join(publicTime).strip()
		publicTime = publicTime[len(publicTime)-19::]
		#转化为时间戳
		import time
		item['date'] = time.mktime(time.strptime(publicTime,"%Y-%m-%d %H:%M:%S"))

		#内容
		content = ''
		datas = response.xpath('//div[contains(@class, "text")]/*|//div[contains(@class, "article")]/*')
		for sel in datas:
			isShare = sel.extract().startswith('<div class="bdsharebuttonbox')
			if not isShare:
				content = content + sel.extract()
		item['content'] = ''.join(content)
		# logger.info(item['content'])

		page_title = response.xpath('//div[contains(@id, "pageNum")]/span[last()]/a/text()').extract()
		page_title = ''.join(page_title)
		if u'下一页' == page_title:
			meta = {
				"title": item['title'],
				"link": item['link'],
				"date": item['date'],
				"content": content,
			}
			nextlink = response.xpath('//div[contains(@id, "pageNum")]/span[last()]/a/@href').extract()
			nextlink = ''.join(nextlink)

			urllist = response.url.split('/')
			urllist.pop()
			nexturl = '/'.join(urllist) + '/' + nextlink

			timestamp = item['date']
			show_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
			logger.info('need get next content. cur_link: %s, next_link: %s, title: %s, date: %s, content_length: %u' % (response.url, nexturl, item['title'], show_datetime, len(item['content'])))
			yield scrapy.Request(nexturl, meta=meta, callback=self.NextContentParse, errback=self.errHandler)
		else:
			#timestamp是输入变量
			timestamp = item['date']
			show_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
			logger.info('fininsh get content. link: %s, title: %s, date: %s, content_length: %u' % (item['link'], item['title'], show_datetime, len(item['content'])))
			yield item

	def NextContentParse(self, response):
		item = DuoWanItem()
		item['link'] = response.meta['link']
		item['linkmd5id'] = md5(item['link']).hexdigest()
		item['title'] = response.meta['title']
		item['date'] = response.meta['date']
		content = response.xpath('//div[contains(@class, "text")]').extract()
		item['content'] = response.meta['content'] + ''.join(content)
		import time
		#timestamp是输入变量
		timestamp = item['date']
		show_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
		logger.info('finish get next content. link: %s, title: %s, date: %s, content_length: %u' % (item['link'], item['title'], show_datetime, len(item['content'])))
		return item

	def errHandler(self, failure):
		logger.error('errHandler: ' + str(failure))
