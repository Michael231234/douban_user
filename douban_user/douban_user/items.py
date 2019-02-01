# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanUserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    group_id = scrapy.Field()
    user_id = scrapy.Field()
    location = scrapy.Field()
    join_time = scrapy.Field()
    movie_url = scrapy.Field()
    movie_genre = scrapy.Field()
    movie_rate = scrapy.Field()
    pass
