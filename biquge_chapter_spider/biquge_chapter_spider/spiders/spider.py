import scrapy
import re
import pika
import json
import time
import scrapy
from urllib import parse
import logging
import sqlite3
from biquge_chapter_spider.items import BiqugeChapterSpiderFictionItem, BiqugeChapterSpiderChapterItem


logger = logging.getLogger(__name__)


class SpiderSpider(scrapy.Spider):
    name = "spider"
    # allowed_domains = ["spider.com"]
    start_urls = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queue_name = None
        self.channel = None
        self.db_params = None
        self.conn = None
        self.cursor = None
        self.tcp_uuid = 0

    def establish_connection(self):
        try:
            connection_params = self.settings.get('RABBITMQ_PARAMS', None)
            self.queue_name = connection_params['queue']
            credentials = pika.PlainCredentials(
                connection_params['username'],
                connection_params['password']
            )
            connection_params_result = {
                'host': connection_params['host'],
                'port': connection_params['port'],
                'virtual_host': connection_params['virtual_host'],
                'credentials': credentials,
                'heartbeat': 3600,
                'connection_attempts': 5,
            }
            connection = pika.BlockingConnection(pika.ConnectionParameters(**connection_params_result))
            self.channel = connection.channel()
            self.channel.basic_qos(prefetch_count=1)
            self.tcp_uuid = int(self.tcp_uuid) + 1
        except Exception as e:
            print(f"连接MQ失败: {str(e)}")
            print("等待5秒后重试...")
            time.sleep(5)
            self.establish_connection()

    def connect_db(self):
        try:
            self.conn = sqlite3.connect("../db/biquge.db")
            self.cursor = self.conn.cursor()
        except Exception as e:
            print("Error connecting to DB: ", e)
            print("等待5秒后重试...")
            time.sleep(5)
            self.connect_db()

    def extract_last_number(self, text):
        # 使用正则表达式查找所有的数字
        numbers = re.findall(r'.*?/(\d+)/', text)
        # print(numbers)
        if numbers:
            # 返回最后一个数字
            return str(numbers[-1])
        else:
            return ""

    def start_requests(self):
        self.establish_connection()
        self.connect_db()
        while True:
            try:
                method, header, body = self.channel.basic_get(self.queue_name)
            except Exception as e:
                print("--- ---")
                print(e)
                print("--- establish_connection ---")
                self.establish_connection()
                time.sleep(1)
                continue
            if not method:
                continue
            delivery_tag = method.delivery_tag
            body = body.decode()
            body = parse.unquote(body)
            json_data = json.loads(body)
            print(body)
            url = json_data['url']
            if url is None or url == "":
                self.ack(delivery_tag)
                continue
            fiction_code = self.extract_last_number(url)
            # 检验数据库中是否有数据 有则跳过
            sql = "SELECT COUNT(id) AS count FROM fiction_list WHERE fiction_code = ?"
            try:
                self.cursor.execute(sql, (fiction_code,))
                result = self.cursor.fetchone()
                count = result[0]
                if count > 0:
                    print(f"SQL SELECT fiction_code: {fiction_code}, COUNT: {count}, ACK: {delivery_tag} 已跳过")
                    self.ack(delivery_tag)
                    continue
            except Exception as e:
                print(e)
                print(sql)
                print("--- reconnect_db ---")
                self.no_ack(delivery_tag)
                self.connect_db()
                time.sleep(1)
                continue
            print(f"准备请求: {url}, ACK: {delivery_tag}")
            yield self.callback(
                url=url,
                delivery_tag=delivery_tag,
                fiction_code=fiction_code,
            )

    def callback(self, url, delivery_tag, fiction_code):
        meta = {
            "url": url,
            "fiction_code": fiction_code,
            "delivery_tag": delivery_tag,
            "tcp_uuid": int(self.tcp_uuid),
        }
        print(url)
        return scrapy.Request(
            url=url,
            meta=meta,
            callback=self.parse_list,
        )

    def ack(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)
        print(f"提交ACK确认: {delivery_tag}")

    def no_ack(self, delivery_tag):
        self.channel.basic_reject(delivery_tag=delivery_tag, requeue=True)

    def parse_list(self, response):
        meta = response.meta

        # ==== 解析 小说基本信息 ====
        fiction_code = meta['fiction_code']
        fiction_name = response.xpath(".//div[@id='info']/h1/text()").extract_first()
        fiction_info = response.xpath(".//p[contains(text(), '更新时间：')]/text()").extract_first()
        fiction_introduce = response.xpath(".//div[@id='intro']/text()").extract()
        fiction_author = response.xpath(".//p[contains(text(), '作者：')]/a/text()").extract_first()

        #  > 都市小说 > 汴京小医娘
        fiction_type = response.xpath(".//div[@class='con_top']/text()").extract_first()
        fiction_type = re.sub(" ", "", str(fiction_type))
        fiction_type = re.sub(re.escape(fiction_name), "", str(fiction_type))
        fiction_type = re.sub(">", "", str(fiction_type))

        fiction_image_url = response.xpath(".//div[@id='fmimg']/img/@src").extract_first()
        fiction_count = response.xpath(".//p[contains(text(), '更新时间：')]/text()").extract_first()
        fiction_count = re.sub("更新时间：", "", str(fiction_count))

        item = BiqugeChapterSpiderFictionItem()
        item['fiction_code'] = str(fiction_code)
        item['fiction_name'] = str(fiction_name)
        item['fiction_info'] = str(fiction_info)
        item['fiction_introduce'] = str(fiction_introduce)
        item['fiction_author'] = str(fiction_author)
        item['fiction_type'] = str(fiction_type)
        item['fiction_image_url'] = str(fiction_image_url)
        item['fiction_count'] = str(fiction_count)
        print(f"获取{item['fiction_name']}信息")
        yield item

        # ==== 解析 小说章节 ====
        chapter_list = response.xpath(".//div[@id='list']/dl/dd/a")
        # 用来去重的 页面上有不少重复内容
        chapter_set = set()
        chapter_only_one_list = list()
        for each_chapter in chapter_list:
            # 40726662.html
            each_href = each_chapter.xpath("./@href").extract_first()
            # 40726662
            each_code = re.sub(".html", "", str(each_href))
            if each_code in chapter_set:
                continue
            else:
                chapter_set.add(each_code)
            each_name = each_chapter.xpath("./text()").extract_first()
            set_item = {
                "each_code": str(each_code),
                "each_name": str(each_name),
            }
            # print(f"set_item: {set_item}")
            chapter_only_one_list.append(set_item)

        # 去重后的
        for each_chapter in chapter_only_one_list:
            chapter_code = each_chapter.get('each_code')
            chapter_name = each_chapter.get('each_name')
            # 通过code进行排序
            chapter_order = int(chapter_code)

            item = BiqugeChapterSpiderChapterItem()
            item['fiction_code'] = str(fiction_code)
            item['chapter_code'] = str(chapter_code)
            item['chapter_name'] = str(chapter_name)
            item['chapter_order'] = int(chapter_order)
            # print(f"获取 {fiction_name} 章节信息: {chapter_name}")
            yield item

        # ack
        delivery_tag = meta['delivery_tag']
        tcp_uuid = meta['tcp_uuid']
        if int(tcp_uuid) == self.tcp_uuid:
            self.ack(delivery_tag)
        else:
            print(f"ACK 跳过: tcp_uuid: {tcp_uuid}, self.tcp_uuid: {self.tcp_uuid}, delivery_tag: {delivery_tag}")
