import os
import requests
import json
import logging
from dotenv import load_dotenv
from big_data import AwsInstance
from param import cities

load_dotenv()


class WeatherCall:
    def __init__(self, cities):
        self.cities = cities
        self.apikey = os.getenv('APIKEY')
        self.aws = AwsInstance()
        self.weather = self.get_cities_weather()

    def _get_geo(self, city):
        url = 'https://nominatim.openstreetmap.org/search?'
        params = {
            'city': city,
            'format': 'json'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            content = response.json()
            lat,lon = content[0]['lat'], content[0]['lon']
            return (lat, lon)
        else:
            raise Exception

    def _get_weather(self, city, lat, lon):
        url = f'https://api.openweathermap.org/data/2.5/forecast?'
        params ={
            'lat':lat,
            'lon': lon,
            'appid': self.apikey,
            'units': 'metric'
        }

        response = requests.get(url, params=params)
        content = response.json()
        sunrise = content['city']['sunrise']
        sunset = content['city']['sunset']
        weather = []
        for i, id in enumerate(content['list']):
            if i%8 == 0:
                weather.append({
                    'city': city,
                    'weather': id['weather'][0]['main'],
                    'temps': id['main']['temp'],
                    'feels_like': id['main']['feels_like'],
                    'sunrise': sunrise,
                    'sunset': sunset,
                    'dt_text': id['dt_txt']
                })
        return weather

    def get_cities_weather(self):
        logging.info('Starting Weather API calls')
        geocode = geocode = {city: self._get_geo(city) for city in self.cities}
        weather = []
        for k,v in geocode.items():
            weather.extend(self._get_weather(k, v[0], v[1]))
        return weather

    def to_s3(self):
        file_path = 'weather.json'
        with open(file_path, "w") as json_file:
            json.dump(self.weather, json_file, indent=4)

        self.aws.push_to_s3('weather.json')
