import scrapy


class AmazonFrontSpider(scrapy.Spider):
    name = "amazon_front"
    allowed_domains = ["amazon.com"]
    start_urls = ["https://amazon.com"]

    def parse(self, response):
        pass
