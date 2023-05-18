import scrapy
from chocolatescraper.config import api_key
from chocolatescraper.itemsloaders import ChocolateProductLoader
from chocolatescraper.items import ChocolateProduct
from urllib.parse import urlencode

API_KEY = api_key
def get_proxy_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url



class ChocolateSpider(scrapy.Spider):
    name = "chocolatespider"

    def start_requests(self):
        start_url = "https://www.chocolate.co.uk/collections/all"
        yield scrapy.Request(url=get_proxy_url(start_url), callback=self.parse)

    def parse(self, response):
        products = response.css('product-item')
        
        for product in products:
            chocolate = ChocolateProductLoader(item=ChocolateProduct(), selector = product)
            chocolate.add_css('name','a.product-item-meta__title::text')
            chocolate.add_css ('price','span.price', re='<span class="price">\n              <span class="visually-hidden">Sale price</span>(.*)</span>')   
            chocolate.add_css('url', 'div.product-item-meta a::attr(href)')
            yield chocolate.load_item()
            
        next_page = response.css('[rel="next"] ::attr(href)').get()

        if next_page is not None:
            next_page_url = 'https://www.chocolate.co.uk' + next_page
            yield response.follow(next_page_url, callback=self.parse)
