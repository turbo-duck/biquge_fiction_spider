# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3
from .items import BiqugeChapterSpiderFictionItem, BiqugeChapterSpiderChapterItem


class BiqugeChapterSpiderPipeline:
    def process_item(self, item, spider):
        return item


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
        adapter = ItemAdapter(item)
        if isinstance(item, BiqugeChapterSpiderFictionItem):
            self.process_fiction_item(adapter, spider)
        elif isinstance(item, BiqugeChapterSpiderChapterItem):
            self.process_chapter_item(adapter, spider)
        return item

    def process_fiction_item(self, adapter, spider):
        self.cursor.execute('''
            INSERT INTO
            fiction_list(
            fiction_code, fiction_name, fiction_info, 
            fiction_introduce, fiction_author, fiction_type, 
            fiction_image_url, fiction_count, 
            create_time, update_time) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (
            adapter.get('fiction_code'),
            adapter.get('fiction_name'),
            adapter.get('fiction_info'),
            adapter.get('fiction_introduce'),
            adapter.get('fiction_author'),
            adapter.get('fiction_type'),
            adapter.get('fiction_image_url'),
            adapter.get('fiction_count')
        ))
        self.connection.commit()
        print(f"数据库入库: fiction_list {adapter.get('fiction_name')}")
        return adapter

    def process_chapter_item(self, adapter, spider):
        self.cursor.execute('''
            INSERT INTO
            chapter_list(
            fiction_code, chapter_code, chapter_name, 
            chapter_order, create_time, update_time)
            VALUES(?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (
            adapter.get('fiction_code'),
            adapter.get('chapter_code'),
            adapter.get('chapter_name'),
            adapter.get('chapter_order')
        ))
        self.connection.commit()
        # print(f"数据库入库: chapter_list {adapter.get('chapter_name')}")
        return adapter
