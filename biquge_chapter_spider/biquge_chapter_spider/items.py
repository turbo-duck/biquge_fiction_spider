# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BiqugeChapterSpiderFictionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    fiction_code = scrapy.Field()
    fiction_name = scrapy.Field()
    fiction_info = scrapy.Field()
    fiction_introduce = scrapy.Field()
    fiction_author = scrapy.Field()
    fiction_type = scrapy.Field()
    fiction_image_url = scrapy.Field()
    fiction_count = scrapy.Field()


class BiqugeChapterSpiderChapterItem(scrapy.Item):
    fiction_code = scrapy.Field()
    chapter_code = scrapy.Field()
    chapter_name = scrapy.Field()
    chapter_order = scrapy.Field()

