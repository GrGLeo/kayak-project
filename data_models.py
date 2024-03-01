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
    rating = Column(Float)
    description = Column(String)
    reviews = Column(Integer)
    url = Column(String)
    personnel = Column(Float) 
    equipments = Column(Float)
    property = Column(Float)
    comfort = Column(Float)
    value = Column(Float)
    location = Column(Float)
    wifi = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
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
    dt_text = Column(DateTime, primary_key=True)
    daylight = Column(Integer)
    dt_partition = Column(String, primary_key=True)
    
    
