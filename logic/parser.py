import asyncio
import pandas as pd

import requests
from bs4 import BeautifulSoup
from database.models import async_session

import database.requests as rq
from database.models import async_main

async def parsing_data_with_city(city):
    city_name = await rq.getter_city_name(470068887)
    link = await rq.getter_url_from_city(city_name)

    pasta = requests.get(link).text

    soup = BeautifulSoup(pasta, 'lxml')
    containers = soup.find('div').text

    df = pd.read_html(link)
    print(df)




def filter_for_regions(hpref):
    return '/pogoda/ru-RU/region/'


def filter_for_sities(hpref):
    return '/pogoda/'


async def added_city_to_db(name, url, translit):
    await rq.setter_sity(name, url, translit)


async def add_moscow():
    await rq.setter_sity('Москва', 'https://yandex.ru/pogoda/moscow')


async def getter_weather(city: str) -> tuple:
    """
    Функция возвращает список с температурой и состоянием погоды, исходя из города
    :param city:
    :return:
    """
    city_eng = await rq.getter_city_eng(city)
    ulr = f"https://pogoda.mail.ru/prognoz/{city_eng}/extended/"
    try:
        r = requests.get(ulr)
    except UnboundLocalError:
        print(city, city_eng)
        exit()
    soup = BeautifulSoup(r.content, 'lxml')


    containers = soup.find_all('div', class_='p-flex__column p-flex__column_percent-16')
    temp = []
    state = []
    if containers:
        for i in range(0, 4):
            temp.append(containers[i].find('span', {"class": "text text_block text_bold_medium margin_bottom_10"}).text)
            state.append(containers[i].find('span', {"class": "text text_block text_light_normal text_fixed"}).text)
        return temp, state
    else:
        print(soup)


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
            translit = link.split("/")[2].split("?")[0]
            asyncio.run(added_city_to_db(name, url, translit))
        print(region, "added")

    asyncio.run(async_main())
    asyncio.run(add_moscow())


if __name__ == '__main__':
    pass
    # start_total_parsing()
    # get_weather("Новокузнецк")