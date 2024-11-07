from fileinput import filename

from playwright.sync_api import sync_playwright
from lxml import html
import re
import time
import pandas as pd


def main():
    url = "https://www.amazon.co.uk/s?i=merchant-items&me=ASLG92IW3VWWP&page={}&qid=1728064975&refresh=1&ref=sr_pg_2"
    # main container
    product_data = {
        "TITLE": [],
        "CODE": [],
        "PRICE": []
    }
    # Initialize lists to store titles and product codes and prices
    all_titles = []
    all_product_codes = []
    all_prices=[]

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        main_page = browser.new_page()
        # main_page.set_viewport_size({"width": 1920, "height": 1080})
        main_page.goto(url.format(1))
        main_page.wait_for_timeout(5000)

        main_page.locator("//div/span[contains(@id,'glow-ingress-line2')]").click()
        main_page.wait_for_timeout(5000)
        main_page.locator("//div/div/input[@autocomplete='postal-code']").fill("SW1W 0NY")
        main_page.keyboard.press("Enter")
        main_page.wait_for_timeout(2000)
        main_page.keyboard.press("Enter")

        main_page.wait_for_timeout(5000)
        main_page.goto(url)
        main_page.wait_for_timeout(5000)
        main_page.locator("//div/span[@class='s-pagination-strip']").scroll_into_view_if_needed()
        last_page=main_page.locator("//div/span/span[contains(@class,'s-pagination-disabled')][2]").inner_text()
        print(last_page)

        for p in range(1, int(last_page)+1):
            main_page.goto(url.format(p))
            main_page.wait_for_timeout(5000)
            main_page.wait_for_selector("//div[contains(@class,'s-main-slot')]", timeout=40000)

            # Scroll down to load more products
            main_page.mouse.wheel(0, 1000)
            main_page.wait_for_timeout(3000)
            product_number = main_page.locator("//div/h2/a").count()

            for i in range(0,product_number):

                part_url=main_page.locator("//div/h2/a").nth(i).get_attribute("href")
                main_url=f"https://www.amazon.co.uk{part_url}"
                product_page=browser.new_page()
                product_page.goto(main_url)
                # product_page.wait_for_timeout(5000)
                # product_page.keyboard.press("End")
                # product_page.wait_for_timeout(2000)
                # product_page.keyboard.press("Home")
                # product_page.wait_for_timeout(2000)
                #product_page.mouse.wheel(0,200)
                product_page.wait_for_selector("//div/h1[@id='title']",timeout=60000)
                prices= product_page.locator("//div[contains(@class,'a-box')]/div/div/div/div/div[1]/span[contains(@class,'offer-price')]").text_content()
                all_prices.append(prices.strip())
                print(f"product {i} done")

                time.sleep(2)
                product_page.close()

            # Extract titles
            titles_spans = main_page.locator("//div/div[@data-cy='title-recipe']/h2/a/span").all_inner_texts()
            all_titles.extend(titles_spans)  # Append titles to the list

            # Find all the hrefs using the locator
            product_hrefs = main_page.locator("//div/div[@data-cy='title-recipe']/h2/a")

            # Loop through all hrefs and extract the product codes
            for i in range(product_hrefs.count()):
                href = product_hrefs.nth(i).get_attribute('href')
                if href:
                    # Regex pattern to extract the product code between "dp/" and "/ref"
                    pattern = r"dp\/(.*?)\/ref"
                    match = re.search(pattern, href)
                    if match:
                        all_product_codes.append(match.group(1))  # Append product codes to the list
            print(f"page {p} done")
        browser.close()
            # Output the consolidated lists
        product_data["TITLE"] = all_titles
        product_data["CODE"] = all_product_codes
        product_data["PRICE"] = all_prices


        return product_data
    # print(all_titles)
    # print(all_product_codes)
    # print(all_prices)
    # print(len(all_titles))
    # print(len(all_product_codes))
    # print(len(all_prices))

def save_to_csv(file_name="AZ_store_front_data.csv", data = None):
    if data is None:
        raise ValueError("Data must be specified")
    else:
        df = pd.DataFrame(data)
        df.to_csv(file_name, index=False)





if __name__ == "__main__":
   products=main()
   save_to_csv(data=products)
