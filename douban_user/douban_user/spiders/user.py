# -*- coding: utf-8 -*-
import scrapy
from ..items import DoubanUserItem
import re
import time
from scrapy.http import Request
# import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_movies():
    urls = []
    for i in range(10):
        if i % 2 == 0:
            time.sleep(5)
        url = 'https://www.douban.com/group/all?start=%d' % (i*15)
        urls.append(url)

    return urls


class DoubanSpider(scrapy.Spider):
    name = 'user'
    allowed_domains = ['douban.com']

    # def start_requests(self):
    #     return [Request('https://www.douban.com/login', callback=self.parse, meta={'cookiejar': 1})]

    # def post_login(self, response):
    #     #     capt = response.xpath('//div/img[@id="captcha_image"]/@src').extract()  # 获取验证码地址
    #     #     print(capt)
    #     #     if len(capt) > 0:  # 判断是否有验证
    #     #         print('有验证码')
    #     #         local_path = '/Users/konglingtong/PycharmProjects/spider_douban/douban_user/douban_user/spiders/capt.jpeg'
    #     #         urllib.request.urlretrieve(capt[0], filename=local_path)  # 保存验证码到本地
    #     #         print('查看本地验证码图片并输入')
    #     #         capt_id = response.xpath('//div/input[@name="captcha-id"]/@value').extract_first()
    #     #         captcha_value = input()  # 验证码
    #     #         data = {
    #     #             'ck': 'RZly',
    #     #             'source': None,
    #     #             'redir': 'https://www.douban.com',
    #     #             'form_email': '15147260861@163.com',  # 邮箱账号
    #     #             'form_password': '960128akML',  # 密码
    #     #             'remember': 'on',
    #     #             'login': '登陆',
    #     #             'captcha-solution': captcha_value,
    #     #             'captcha-id': capt_id,
    #     #             }
    #     #     else:
    #     #         print('没有验证码')
    #     #         data = {
    #     #             'ck': 'RZly',
    #     #             'source': None,
    #     #             'redir': 'https://www.douban.com',
    #     #             'form_email': '15147260861@163.com',  # 邮箱账号
    #     #             'form_password': '960128akML',  # 密码
    #     #             'remember': 'on',
    #     #             'login': '登陆',
    #     #         }
    #     #         print('login...')
    #     #     return [  # 使用Scrapy抓取网页时，如果想要预填充或重写像用户名、用户密码这些表单字段， 可以使用 FormRequest.from_response() 方法实现
    #     #         scrapy.FormRequest.from_response(response,
    #     #                                          meta={'cookiejar': response.meta['cookiejar']},
    #     #                                          dont_filter=False,
    #     #                                          formdata=data, callback=self.parse)
    #     #         ]

    def parse(self, response):
        urls = get_movies()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.first_parse)

    def first_parse(self, response):
        group_urls = response.css('.clist2 span.pl2 a::attr(href)').extract()
        for group_url in group_urls:
            url = group_url + 'members'
            yield scrapy.Request(url=url, callback=self.second_parse)

    def second_parse(self, response):
        numbers = response.xpath('//*[@id="content"]/div/div[1]/div[3]/div[2]/a[10]/text()').extract_first()
        for i in range(int(numbers)):
            if i % 2 == 0:
                time.sleep(5)
            url = response.url + '?start=%d' % (i*35)
            yield scrapy.Request(url=url, callback=self.third_parse)

    def third_parse(self, response):
        urls = response.css('.pic a::attr(href)').extract()
        i = 0
        for url in urls:
            i = i+1
            if i % 10 == 0:
                time.sleep(5)
            yield scrapy.Request(url=url, callback=self.item_parse)

    def item_parse(self, response):
        items = []
        item = DoubanUserItem()
        item['location'] = response.css('.user-info a::text').extract()
        item['user_id'] = response.css('.user-info .pl::text').extract()[0].replace(' ', '')
        pattern = re.compile(r'\d+-\d+-\d+')
        join_time = response.css('.user-info .pl::text').extract()[1]
        item['join_time'] = pattern.findall(join_time)
        urls = response.css('#movie span.pl a::attr(href)').extract()
        items.append(item)
        i = 0
        yield item
        for url in urls:
            i = i+1
            if i % 10 == 0:
                time.sleep(5)
            yield scrapy.Request(url=url, callback=self.seconditem_parse)

    def seconditem_parse(self, response):
        items = []
        item = DoubanUserItem()
        page = response.css('span.next a::attr(href)').extract_first()
        item['movie_url'] = response.css('.info li.title a::attr(href)').extract()
        rates = response.css('.info li:nth-child(3) span:nth-child(1)::attr(class)').extract()
        results = []
        for rate in rates:
            pattern = re.compile(r'\d')
            result = pattern.findall(rate)
            results.append(result)
        item['movie_rate'] = results
        items.append(item)
        i = 0
        yield item
        if page:
            i = i+1
            if i % 10 == 0:
                time.sleep(5)
            yield scrapy.Request(url=page, callback=self.seconditem_parse)
