from database import requests as rq
from logic.parser import getter_weather
import asyncio

if __name__ == '__main__':
    print(asyncio.run(rq.getter_actual_weather_from_db("Красноярск")))