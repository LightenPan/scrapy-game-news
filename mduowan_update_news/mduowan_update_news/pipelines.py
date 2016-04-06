# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
from datetime import datetime
from hashlib import md5
import MySQLdb
import MySQLdb.cursors

import logging
logger = logging.getLogger('pipelines')


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
        return cls(dbpool)

    # pipeline默认调用
    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return item

    # 将每行更新或写入数据库中
    def _do_upinsert(self, conn, item, spider):
        linkmd5id = self._get_linkmd5id(item)
        # print linkmd5id
        sqlSelect = """
                select 1 from t_duowan_news where linkmd5id = '%s'
        """ % (linkmd5id,)
        # logger.info("sel_sql: " + sqlSelect)
        conn.execute(sqlSelect)
        ret = conn.fetchone()

        import base64
        content = base64.b64encode(str(item['content']))
        if ret:
            sqlExecute = """
                update t_duowan_news set title = '%s', date = %u, link = '%s', content = '%s', updated = now() where linkmd5id = '%s'
            """ % (item['title'], item['date'], item['link'], content, linkmd5id)
        else:
            sqlExecute = """
                insert into t_duowan_news(linkmd5id, title, date, link, content, updated)
                values('%s', '%s', %u, '%s', '%s', now())
            """ % (linkmd5id, item['title'], item['date'], item['link'], content)
        # logger.info("sqlExecute: " + sqlExecute)
        conn.execute(sqlExecute)

    # 获取url的md5编码
    def _get_linkmd5id(self, item):
        # url进行md5处理，为避免重复采集设计
        return md5(item['link']).hexdigest()

    # 异常处理
    def _handle_error(self, failure, item, spider):
        logger.error(str(failure))
