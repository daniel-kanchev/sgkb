import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from sgkb.items import Article


class SgkbSpider(scrapy.Spider):
    name = 'sgkb'
    start_urls = ['https://sgkb.de/news/']

    def parse(self, response):
        yield response.follow(response.url, self.parse_articles, dont_filter=True)
        next_page = response.xpath('//div[@class="nav-previous"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_articles(self, response):
        articles = response.xpath('//div[@id="main"]//div[@class="wrapper"]/div[@class="inside"]/div[@id]')
        for article in articles:
            item = ItemLoader(Article())
            item.default_output_processor = TakeFirst()

            title = article.xpath('.//h3//text()').get() or article.xpath('.//h1//text()').get()
            if not title:
                return

            date = article.xpath('.//h2//text()').get()

            content = article.xpath('.//div[contains(@class, "article")]/p[2]//text()').getall() or \
                      article.xpath('.//div[contains(@class, "article")]/text()').getall()
            if not content:
                return

            content = [text for text in content if text.strip()]
            content = "\n".join(content).strip()

            item.add_value('title', title)
            item.add_value('date', date)
            item.add_value('link', response.url)
            item.add_value('content', content)

            yield item.load_item()



