from sqlalchemy import Column, Integer, String, Float, DateTime, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class HotelsTable(Base):
    '''
    Hotels table schema
    '''
    __tablename__ = 'hotels'

    name = Column(String, primary_key=True)
    city = Column(String)
    rating = Column(String)
    description = Column(String)
    reviews = Column(Integer)
    coordinates = Column(String)
    url = Column(String)
    dt_partition = Column(String, primary_key=True)


class WeatherTable(Base):
    '''
    Weather table schema
    '''
    __tablename__ = 'weather'

    city = Column(String, primary_key=True)
    weather = Column(String)
    temps = Column(Float)
    feels_like = Column(Float)
    sunrise = Column(DateTime)
    sunset = Column(DateTime)
    dt_text = Column(DateTime)
    daylight = Column(Time)
    dt_partition = Column(String, primary_key=True)
    
    
