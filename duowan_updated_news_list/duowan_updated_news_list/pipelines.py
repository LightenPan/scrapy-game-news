# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors

import logging
logger = logging.getLogger('pipelines')


# 清空数据表
def _do_delete(self, conn, item, spider):
	sqlExecute = "delete from t_duowan_update_news_list"
	# logger.info("sqlExecute: " + sqlExecute)
	conn.execute(sqlExecute)



class MySQLPipeline(object):
	def __init__(self, dbpool):
		self.dbpool = dbpool

	@classmethod
	def from_settings(cls, settings):
		dbargs = dict(
			host=settings['MYSQL_HOST'],
			db=settings['MYSQL_DBNAME'],
			user=settings['MYSQL_USER'],
			passwd=settings['MYSQL_PASSWD'],
			charset='utf8',
			cursorclass=MySQLdb.cursors.DictCursor,
			use_unicode=True,
		)
		dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)

		#删除更新表的数据
		sqlExecute = "delete from t_duowan_update_news_list"
		# logger.info("sqlExecute: " + sqlExecute)
		dbpool.runQuery(sqlExecute)
		return cls(dbpool)

	# pipeline默认调用
	def process_item(self, item, spider):
		d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
		d.addErrback(self._handle_error, item, spider)
		d.addBoth(lambda _: item)
		return item

	# 将每行更新或写入数据库中
	def _do_upinsert(self, conn, item, spider):
		sqlExecute = """
				insert into t_duowan_update_news_list(link)
				values('%s')
			""" % (item['link'])
		# logger.info("sqlExecute: " + sqlExecute)
		conn.execute(sqlExecute)


	# 异常处理
	def _handle_error(self, failure, item, spider):
		logger.error(str(failure))
