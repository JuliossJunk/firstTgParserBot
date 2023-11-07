import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import asyncio
import aiohttp

def counted_news(req):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0"
    }
    url = f'https://kotaku.com/search?blogId=9&q={req}'

    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    news_count = soup.find("div", class_="j48i5d-1 fuDdQ").find("span", class_='j48i5d-0 keLEgo').text.strip()
    news_count = int((re.findall('(\d+)', news_count))[0])
    return news_count

def get_searched_news(index, news_count):
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }

    url = f'https://kotaku.com/search?blogId=9&q={index}'
    r = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(r.text, "lxml")
    articles_cards = soup.find_all("article", class_="cw4lnv-0 iTueKC js_post_item")

    news_dict = {}

    i=0

    while i<news_count:
        for article in articles_cards:
            article_title = article.find("div",class_='cw4lnv-5 aoiLP').find('h2', class_='sc-759qgu-0 cAqwZL cw4lnv-6 ilhXHI').text.strip()
            article_desc = article.find('div', class_="b8i51y-0 bdlErW cw4lnv-7 eGhCTd").find('p', class_="sc-77igqf-0 bOfvBY").text.strip()
            article_url = article.find('div', class_='cw4lnv-5 aoiLP').find('a', class_="sc-1out364-0 hMndXN js_link").get('href')

            article_date_time = article.find("time", class_="uhd9ir-0 iziAPV").get("datetime")
            date_from_iso = datetime.fromisoformat(article_date_time)
            date_time = datetime.strftime(date_from_iso, "%Y-%m-%d %H:%M:%S")
            article_date_timestamp = time.mktime(datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").timetuple())

            article_id = article_url.split('-')[-1]

            # print(f"{article_title} | {article_url} | {article_date_timestamp}")

            news_dict[article_id] = {
                "article_date_timestamp": article_date_timestamp,
                "article_title": article_title,
                "article_url": article_url,
                "article_desc": article_desc
            }
        i+=1

    return news_dict



def main(req):
    req = req.strip().replace(' ', '%20')

    news_count=3#counted_news(req)
    print(get_searched_news(req, news_count))

if __name__ == '__main__':
    main('doom ')