
import logging
import scrapy
from typing import Type
from scrapy.crawler import CrawlerProcess
from big_data import AwsInstance


class HotelSpider(scrapy.Spider):
    '''
    A spider for scraping hotel information from booking.com.\n
    Attributes:
        name (str): The name of the spider.
    '''
    name='hotelspider'

    def __init__(self, cities):
        '''
        Initializes the HotelSpider class.\n
        Args:
            cities (list): A list of cities to scrape hotel information for.
        '''
        super().__init__()
        self.cities = cities

    def start_requests(self):
        '''
        Generates initial requests for each city.\n
        Yields:
            scrapy.Request: The request to scrape hotel data.
        '''
        for city in self.cities:
            city = city.replace(' ','-')
            url = f'https://www.booking.com/city/fr/{city}.fr.html'
            yield scrapy.Request(url=url, callback=self.parse, meta={'city':city})

    def parse(self, response):
        '''
        Parses the response and extracts hotel links.\n
        Args:
            response (scrapy.http.Response): The response from the initial request.\n
        Yields:
            scrapy.Request: The request to scrape hotel details.
        '''
        hrefs = response.xpath('//div[@class="c6666c448e"]/a/@href').getall()
        city = response.meta.get('city')
        for href in hrefs:
            yield response.follow(href, callback=self.parse_hotel_details, meta={'url': href, 'city':city})


    def parse_hotel_details(self, response):
        '''
        Parses the hotel details page and extracts relevant information.\n
        Args:
            response (scrapy.http.Response): The response from the hotel details page.\n
        Yields:
            dict: A dictionary containing hotel information.
        '''
        name = response.css('h2.d2fee87262.pp-header__title::text').get()
        rating = response.css('p.review_score_value::text').get()
        description = response.xpath('/html/body/div[3]/div/div[5]/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[1]/div[1]/div[2]/div/p/text()').get()
        
        reviews = response.css('a.big_review_score_detailed div.abf093bdfe::text').get()
        coordinates = response.css('a#hotel_sidebar_static_map::attr(data-atlas-latlng)').get()
        url = response.meta.get('url')
        city = response.meta.get('city')
    
        
        review_elements = response.css('div[data-testid="review-subscore"]')

        special_rate = {review.css('span.be887614c2::text').get(): review.css('div.ccb65902b2.efcd70b4c4::text').get() for review in review_elements}
        yield {
            'name': name,
            'city': city,
            'rating': rating,
            'description': description,
            'reviews': reviews,
            'coordinates': coordinates,
            'url': url,
            **special_rate
        }


class Crawler():
    '''
    A class for initiating a crawling process to scrape hotel information and save it to AWS S3.\n
    Attributes:
        spider: An instance of the spider used for crawling.
        aws (AwsInstance): An instance of the AwsInstance class.
    '''

    def __init__(self, Spider: Type[scrapy.Spider], cities: list, filename: str):
        self.spider = Spider
        self.cities = cities
        self.filename = filename
        self.aws = AwsInstance()
        self._crawl_booking(filename)

    def _crawl_booking(self, filename: str):
        '''
        Initiates a crawling process to scrape hotel information and save it to a file.\n
        Args:
            filename (str): The name of the file to save the scraped data.\n
        Returns:
            None
        '''
        process = CrawlerProcess(settings={
            'USER_AGENT': 'Mozilla/5.0',
            'LOG_LEVEL': logging.INFO,
            "FEEDS": {
                filename: {"format": "json"},
            }
        })

        process.crawl(self.spider, cities=self.cities)
        process.start()

    def load_cloud_files(self, mode: str='latest') -> None:
        '''
        Downloads files from an Amazon S3 bucket to a local directory.\n
        Args:
            mode (str, optional): The mode of downloading. Defaults to 'latest'.\n
                - 'latest': Downloads only the latest uploaded file.
                - 'all': Downloads all files uploaded to the bucket.
        '''
        dir_ = 'hotels'
        if mode == 'latest':
            with open('s3_files.log', 'r', encoding='UTF-8') as file:
                for s3_upload in file:
                    last_uploaded = s3_upload.strip()
            self.aws.load_from_s3(last_uploaded, dir_)

        if mode == 'all':
            with open('s3_files.log', 'r', encoding='UTF-8') as file:
                uploaded_files = [line.strip() for line in file]
            for upload in uploaded_files:
                self.aws.load_from_s3(upload, dir_)
