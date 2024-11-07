import scrapy
from scrapy_playwright.page import PageCoroutine

class AmazonSpider(scrapy.Spider):
    name = "amazon_spider"
    start_urls = [
        "https://www.amazon.co.uk/s?i=merchant-items&me=ASLG92IW3VWWP&page=1&qid=1728064975&refresh=1&ref=sr_pg_2"
    ]

    async def parse(self, response):
        # Fill in the postal code
        yield PageCoroutine("click", "//div/span[contains(@id,'glow-ingress-line2')]")
        yield PageCoroutine("fill", "//div/div/input[@autocomplete='postal-code']", "SW1W 0NY")
        yield PageCoroutine("press", "//div/div/input[@autocomplete='postal-code']", "Enter")

        # Wait for the main slot to load
        yield PageCoroutine("wait_for_selector", "//div[contains(@class,'s-main-slot')]", timeout=30000)

        # Extract product links
        product_links = response.xpath("//div/h2/a/@href").getall()
        for link in product_links:
            if link:
                main_url = f"https://www.amazon.co.uk{link}"
                yield response.follow(main_url, self.parse_product)

    async def parse_product(self, response):
        # Extract product price
        price = response.xpath("//div[contains(@class,'a-box')]/div/div/div/div/div[1]/span[contains(@class,'offer-price')]/text()").get()
        if price:
            self.log(f"Product Price: {price.strip()}")
        else:
            self.log("Price not found.")

# To run the spider, use the command: scrapy crawl amazon_spider
