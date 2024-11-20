import requests
import bs4 as bs
import asyncio
import database.requests as rq
from database.models import async_main
import asyncio

async def get_weather(city):
    city_eng = await rq.getter_city_eng(city)
    ulr = f"https://pogoda.mail.ru/prognoz/{city_eng}/extended/"

    r = requests.get(ulr)
    soup = bs.BeautifulSoup(r.content, 'lxml')

    containers = soup.find_all('div', class_='p-flex__column p-flex__column_percent-16')
    temp = []
    state = []
    for i in range(0, 4):
        temp.append(containers[i].find('span', {"class": "text text_block text_bold_medium margin_bottom_10"}).text)
        state.append(containers[i].find('span', {"class": "text text_block text_light_normal text_fixed"}).text)
    print(temp, state)
    return temp, state



if __name__ == '__main__':
    asyncio.run(async_main())
    asyncio.run(get_weather("Москва"))

