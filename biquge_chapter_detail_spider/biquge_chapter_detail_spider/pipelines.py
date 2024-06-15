# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3


class SQLitePipeline:
    def __init__(self):
        self.cursor = None
        self.connection = None

    def open_spider(self, spider):
        # 连接到 SQLite 数据库
        self.connection = sqlite3.connect("../db/biquge.db")
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        # 关闭数据库连接
        self.connection.close()

    def process_item(self, item, spider):
        sql = """
        INSERT INTO
        chapter_detail_list(chapter_code, chapter_content)
        VALUES(?, ?)
        """
        # print(sql)
        self.cursor.execute(
            sql, (item['chapter_code'], item['chapter_content'])
        )
        self.connection.commit()
        return item
