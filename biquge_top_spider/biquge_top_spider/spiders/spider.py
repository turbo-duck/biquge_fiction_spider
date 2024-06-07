import scrapy
import re
import time
from biquge_top_spider.items import BiqugeTopSpiderItem


class SpiderSpider(scrapy.Spider):
    name = "spider"
    # allowed_domains = ["spider.com"]
    # start_urls = ["https://spider.com"]

    def start_requests(self):
        for page in range(1, 1392):
            url = f"https://www.xbiqugew.com/top/allvisit/{page}.html"
            print(f"url: {url}")
            yield scrapy.Request(
                url=url,
                callback=self.parse_list,
            )

    def extract_last_number(self, text):
        # 使用正则表达式查找所有的数字
        numbers = re.findall(r'.*?/(\d+)/', text)
        # print(numbers)
        if numbers:
            # 返回最后一个数字
            return str(numbers[-1])
        else:
            return ""

    def parse_list(self, response):
        data_list = response.xpath(".//div[@class='novelslistss']//li")
        page_info = response.xpath(".//em[@id='pagestats']/text()").extract_first()
        for each in data_list:
            each_type = each.xpath("./span[@class='s1']/text()").extract_first()
            each_href = each.xpath("./span[@class='s2']/a/@href").extract_first()
            each_title = each.xpath("./span[@class='s2']/a/text()").extract_first()
            each_author = each.xpath("./span[@class='s4']/text()").extract_first()
            each_update_time = each.xpath("./span[@class='s5']/text()").extract_first()
            each_code = self.extract_last_number(each_href)
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            item = BiqugeTopSpiderItem()
            item['each_code'] = str(each_code)
            item['each_type'] = str(each_type)
            item['each_href'] = str(each_href)
            item['each_title'] = str(each_title)
            item['each_author'] = str(each_author)
            item['each_update_time'] = str(each_update_time)
            item['page_info'] = str(page_info)
            item['now_time'] = str(now_time)
            print(f"each_code: {each_code}")
            yield item
