import json
import time
import requests
from bs4 import BeautifulSoup
import datetime
import csv
import asyncio
import aiohttp
import os

start_time = time.time()  # Время перед полетом
news_data = {}

async def get_page_data(session, index):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0"
    }
    url = f'https://kotaku.com/culture/news?startIndex={index}'

    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')
        articles = soup.find_all('article', class_="sc-cw4lnv-0 ksZQxB js_post_item")
        for article in articles:
            a = article.find("div", class_='sc-cw4lnv-5 dYIPCV').find('h2', class_='sc-759qgu-0 kygHWE sc-cw4lnv-6 kTWlYS').get_text()
            href = article.find('div', class_='sc-cw4lnv-5 dYIPCV').find('a', class_="sc-1out364-0 dPMosf js_link").get('href')
            author = article.find('div', class_='sc-1mep9y1-0 sc-1ixdk2y-0 iVflSZ voDAY').find('a',
                                                                            class_="sc-1out364-0 dPMosf js_link").get_text()
            description = article.find('div', class_="sc-b8i51y-0 eoCFdA sc-cw4lnv-7 jqJvlz").find('p',
                                                                                             class_="sc-77igqf-0 fnnahv").get_text()
            date = article.find("time", class_="sc-uhd9ir-0 ckDoGx").get_text()

            article_id = href.split('-')[-1]

            news_data[article_id] = {
                'title': a,
                'href': href,
                'author': author,
                'description': description,
                'date': date}

        print(f"[INFO] обработал новости по индексам {index}")


async def gather_data():
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0"
    }
    url = 'https://kotaku.com/culture/news?'

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), "lxml")
        tasks = []
        for page in range(0, 60, 20):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def check_news_update():
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0"
    }
    url = f'https://kotaku.com/culture/news'

    with open('kotaku_news_async.json', encoding='UTF-8') as file:
        news_data = json.load(file)

    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    articles = soup.find_all('article', class_="sc-cw4lnv-0 ksZQxB js_post_item")

    fresh_news = {}

    for article in articles:
        href = article.find('div', class_='sc-cw4lnv-5 dYIPCV').find('a', class_="sc-1out364-0 dPMosf js_link").get('href')
        article_id = href.split('-')[-1]
        if article_id in news_data:
            continue
        else:
            a = article.find("div", class_='sc-cw4lnv-5 dYIPCV').find('h2',
                                                                  class_='sc-759qgu-0 kygHWE sc-cw4lnv-6 kTWlYS').get_text()
            href = article.find('div', class_='sc-cw4lnv-5 dYIPCV').find('a', class_="sc-1out364-0 dPMosf js_link").get(
                'href')
            author = article.find('div', class_='sc-1mep9y1-0 sc-1ixdk2y-0 iVflSZ voDAY').find('a',
                                                                            class_="sc-1out364-0 dPMosf js_link").get_text()
            description = article.find('div', class_="sc-b8i51y-0 eoCFdA sc-cw4lnv-7 jqJvlz").find('p',
                                                                                             class_="sc-77igqf-0 fnnahv").get_text()
            date = article.find("time", class_="sc-uhd9ir-0 ckDoGx").get_text()

            article_id = href.split('-')[-1]

            news_data[article_id] = {
                'title': a,
                'href': href,
                'author': author,
                'description': description,
                'date': date}

            fresh_news[article_id] = {
                'title': a,
                'href': href,
                'author': author,
                'description': description,
                'date': date}

    with open(f'kotaku_news_async.json',"w", encoding="utf-8")as file:
        json.dump(news_data,file,indent=4, ensure_ascii=False)
    return fresh_news
def main():
    if os.path.exists('kotaku_news_async.json'):
        print(check_news_update())
    else:
        asyncio.run(gather_data())

        cur_time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")

        with open(f'kotaku_news_async.json',"w", encoding="utf-8")as file:
            json.dump(news_data,file,indent=4, ensure_ascii=False)

        finish_time = time.time()-start_time
        print(f'Затраченное на работу проги время: {finish_time}')


if __name__ == "__main__":
    main()
