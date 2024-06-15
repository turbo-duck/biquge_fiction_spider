# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BiqugeChapterDetailSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    chapter_code = scrapy.Field()
    chapter_content = scrapy.Field()
