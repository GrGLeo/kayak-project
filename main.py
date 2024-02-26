import threading
from scraper import Crawler, HotelSpider
from caller import WeatherCall
from param import cities


def get_weather_data():
    weather = WeatherCall(cities)
    weather.to_s3()

def get_hotels_data():
    crawl = Crawler(HotelSpider, cities, 'bookings_hotels.json')

def get_all_data():
    thread1 = threading.Thread(target=get_weather_data)
    thread2 = threading.Thread(target=get_hotels_data)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


if __name__ == '__main__':
    get_all_data()
