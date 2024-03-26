import os
import sys
import datetime
import pandas as pd
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError
from data_models import Base


class Kayak:
    def __init__(self, tables: dict):
        self.tables = tables
        self.engine = self._postgres_connection()
        self._create_table()
        self.weather_df = self.transfrom_weather()
        self.hotels_df = self.transform_hotels()

    def _create_table(self):
        inspector = inspect(self.engine)
        Base.metadata.bind = self.engine
        created_tables = inspector.get_table_names()
        for table in self.tables:
            if table not in created_tables:
                Base.metadata.create_all(self.engine)
                print(f"Create table {table}")

    def _postgres_connection(self):
        connection_str = os.getenv("POSTGRES")
        engine = create_engine(connection_str)
        try:
            with engine.connect() as connection_str:
                print("Successfully connected to the PostgreSQL database")
                return engine
        except OperationalError as ex:
            print(f"Sorry failed to connect: {ex}")
            sys.exit()

    def transfrom_weather(self):
        weather = pd.read_json("weather.json")
        weather["daylight"] = (weather["sunset"] - weather["sunrise"]) // 3600
        weather["sunrise"] = pd.to_datetime(weather["sunrise"], unit="s")
        weather["sunset"] = pd.to_datetime(weather["sunset"], unit="s")
        weather["dt_partition"] = datetime.date.today().strftime("%Y-%m-%d")
        weather.to_sql("weather", con=self.engine,
                       if_exists="append", index=False)
        print(f"Inserted {weather.shape[0]} in Weather table")
        return weather

    def transform_hotels(self):
        def get_float(x):
            try:
                return float(x.replace(",", "."))
            except AttributeError:
                return x
            except ValueError:
                return x

        hotels = pd.read_json("bookings_hotels.json")
        mapper = {
            "Personnel": "personnel",
            "Équipements": "equipments",
            "Propreté": "property",
            "Confort": "comfort",
            "Rapport qualité/prix": "value",
            "Situation géographique": "location",
            "Connexion Wi-Fi gratuite": "wifi",
        }
        hotels.rename(mapper, axis=1, inplace=True)
        hotels["reviews"] = hotels["reviews"].apply(
            lambda x: int("".join(x.split(" ")[:-2]))
        )
        hotels["lat"] = (
            hotels["coordinates"].apply(
                lambda x: x.split(",")[0]).astype(float)
        )
        hotels["lon"] = (
            hotels["coordinates"].apply(
                lambda x: x.split(",")[1]).astype(float)
        )
        hotels.drop("coordinates", axis=1, inplace=True)
        for col in mapper.values():
            hotels[col] = hotels[col].apply(get_float)
        hotels["rating"] = hotels["rating"].str.replace(",", ".").astype(float)
        hotels["dt_partition"] = datetime.date.today().strftime("%Y-%m-%d")
        hotels.to_sql("hotels", con=self.engine,
                      if_exists="append", index=False)
        print(f"Inserted {hotels.shape[0]} in Hotels table")
        os.remove("bookings_hotels.json")
        return hotels
