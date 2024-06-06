# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BiqugeTopSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    each_code = scrapy.Field()
    each_type = scrapy.Field()
    each_href = scrapy.Field()
    each_title = scrapy.Field()
    each_author = scrapy.Field()
    each_update_time = scrapy.Field()
    page_info = scrapy.Field()
    now_time = scrapy.Field()
