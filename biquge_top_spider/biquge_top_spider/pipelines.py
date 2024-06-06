# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BiqugeTopSpiderPipeline:
    def process_item(self, item, spider):
        return item


class SQLitePipeline:

    def __init__(self):
        self.cursor = None
        self.connection = None

    def open_spider(self, spider):
        self.connection = sqlite3.connect('biquge.db')
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        sql = '''
        INSERT INTO biquge_list (each_code, each_type, each_href, each_title, each_author, each_update_time, page_info, now_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(sql, (
            item.get('each_code'),
            item.get('each_type'),
            item.get('each_href'),
            item.get('each_title'),
            item.get('each_author'),
            item.get('each_update_time'),
            item.get('page_info'),
            item.get('now_time')
        ))
        self.connection.commit()
        return item
