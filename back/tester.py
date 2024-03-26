import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess

class HotelSpider(scrapy.Spider):
    name='hotelspider'

    def start_requests(self):
        urls = ['https://www.booking.com/hotel/fr/b-amp-b-porte-des-lilas.fr.html?aid=304142&label=gen173nr-1FCAMoTTjjAkgNWARoTYgBAZgBDbgBF8gBDNgBAegBAfgBAogCAagCA7gCk73nrgbAAgHSAiQxNzIyNTAzZC04OWRhLTQyZTUtYjg5My02NDhhZDIwNTJlYjTYAgXgAgE']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        name = response.css('h2.d2fee87262.pp-header__title::text').get()
        name = name.encode('utf-8').decode('unicode_escape')
        rating = response.css('p.review_score_value::text').get()
        description = response.css('a.big_review_score_detailed div.aaee4e7cd3::text').get()
        reviews = response.css('a.big_review_score_detailed div.abf093bdfe::text').get()
        coordinates = response.css('a#hotel_sidebar_static_map::attr(data-atlas-latlng)').get()


        yield {
            'name': name,
            'rating': rating,
            'description': description,
            'reviews': reviews,
            'coordinates': coordinates
        }

filename = 'output.json'

process = CrawlerProcess(settings={
    'USER_AGENT': 'Mozilla/5.0',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        filename: {"format": "json"},
    }
})

process.crawl(HotelSpider)
process.start()
