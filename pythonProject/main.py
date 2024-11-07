from playwright.sync_api import sync_playwright
from lxml import html
import re
import time
import pandas as pd

def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto("https://www.amazon.com/stores/Gencywe/page/EDE4733A-A10B-4776-B972-6748AC653C62?ref_=ast_bln")
        page.wait_for_timeout(5000)
        page.keyboard.press("End")
        page.wait_for_timeout(2000)
        page.keyboard.press("Home")
        page.wait_for_timeout(2000)

        page.wait_for_load_state("networkidle", timeout=20000)
        page.wait_for_timeout(5000)

        html_contents = []  # List to accumulate HTML content

        for i in range(2, 6):  # Loop through the first 5 pages of the store
            page.locator(f"//div/nav/ul/li[{i}]/a").click()
            page.wait_for_timeout(5000)
            page.wait_for_load_state("networkidle", timeout=20000)

            html_content = page.inner_html("body")
            html_contents.append(html_content)  # Append the content to the list
            time.sleep(3)

        browser.close()
        return ''.join(html_contents)  # Join all HTML contents into a single string

def parse_store(html_contents):
    product_data = {
        "TITLE": [],
        "CODE": [],
        "PRICE": []
    }
    tree = html.fromstring(html_contents)
    titles = tree.xpath('//div/h2/a[contains(@class,"ProductShowcase__title")]/@title')
    code_urls = tree.xpath('//div/h2/a[contains(@class,"ProductShowcase__title")]/@href')

    product_codes = []
    for url in code_urls:
        match = re.search(r'/([^/?]+)\?', url)
        if match:
            product_codes.append(match.group(1))

    prices = []

    price_containers = tree.xpath('//div/span[contains(@class,"Price__price")][1]')

    for container in price_containers:
        currency = container.xpath('.//span[contains(@class,"Price__currency")]/text()')
        whole = container.xpath('.//span[contains(@class,"Price__whole")]/text()')
        decimal = container.xpath('.//span[contains(@class,"Price__decimalSeparator")]/text()')
        fractional = container.xpath('.//span[contains(@class,"Price__fractional")]/text()')

        if currency and whole and decimal and fractional:
            price = f"{currency[0]}{whole[0]}{decimal[0]}{fractional[0]}"
            prices.append(price)

    product_data["TITLE"] = titles
    product_data["CODE"] = product_codes
    product_data["PRICE"] = prices

    return product_data

def save_to_csv(filename="AZ_store_data.csv", data = None):
    if data is None:
        raise ValueError("Data must be specified")
    else:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)




if __name__ == "__main__":
    content = main()
    store_data=parse_store(content)
    save_to_csv(data=store_data)
