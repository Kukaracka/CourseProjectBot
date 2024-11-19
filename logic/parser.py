import asyncio

import requests
from bs4 import BeautifulSoup
import sqlite3 as sl

import database.requests as rq
from database.models import async_main

def filter_for_regions(hpref):
    return '/pogoda/ru-RU/region/'

def filter_for_sities(hpref):
    return '/pogoda/'

async def to_db(name, url):
    await rq.setter_sity(name, url)

async def add_moscow():
    await rq.setter_sity('Москва', 'https://yandex.ru/pogoda/moscow')


def start_total_parsing():
    link_for_regions_find = "https://yandex.ru/pogoda/ru-RU/region/russia"
    list_for_regions = []

    resource_regions = requests.get(link_for_regions_find).text
    soup_for_regions = BeautifulSoup(resource_regions, 'lxml')

    blocks_of_regions = (soup_for_regions.find('section', {'class': 'AppRegion_region__Oymus'}).
                         find('ul').find_all('a', hpref=filter_for_regions))

    for sity in blocks_of_regions:
        link = sity['href']
        list_for_regions.append(link)

    for region in list_for_regions:
        link_for_cities_find = 'https://yandex.ru' + region
        resource_cities = requests.get(link_for_cities_find).text
        soup_for_cities = BeautifulSoup(resource_cities, 'lxml')
        blocks_for_cities = (soup_for_cities.find('section', {'class': 'AppRegion_region__Oymus'}).
                             find('ul')).find_all('a', hpref=filter_for_sities)
        for sity in blocks_for_cities:
            name = sity.text
            link = sity['href']
            url = "https://yandex.ru" + link
            asyncio.run(async_main())
            asyncio.run(to_db(name, url))

    asyncio.run(async_main())
    asyncio.run(add_moscow())


if __name__ == '__main__':
    start_total_parsing()