import json
import requests
from bs4 import BeautifulSoup
import re


HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0', 'accept': '*/*'}
SEED = "https://techno.nv.ua/innovations.html/"


def get_page_content(link):
    page_info = {
        "url": link,  # ссылка на новость
        "title": "",  # заголовок новости
        "img": "",  # ссылка на изображение
        "body": "",  # текст новости
        "author": "",  # автор новости (если указывается)
        "date": "",  # дата публикации новости в формате YYYY-MM-DD
        "time": "",  # время публикации новости в формате HH:MM
    }
    page = requests.get(link)
    soup = BeautifulSoup(page.content.decode("utf-8"), "html.parser")
    wrapper = soup.find("div", class_="content_wrapper")
    # Парсинг в зависимости от типа html страницы
    body_list = None
    if wrapper:
        if img := soup.find("div", class_="article__content__head_img").find("img"):
            page_info["img"] = img.get("src")
        else:
            print(f'No image (line 32).')
        body_list = wrapper.find_all("p")
    elif wrapper := soup.find("div", class_="main-wrapper"): # content-grid 
        page_info["img"] = wrapper.find("img").get("src")
        body_list = wrapper.find_all("p")
    # автор новости (если указывается)
    try:
        page_info["author"] = wrapper.find("a", class_="opinion_author_name").text
    except AttributeError:
        print('author not specified')
    # текст новости
    if body_list :
        for i in body_list:
            page_info["body"] += i.text + "\n\n"
    else:
        print('No body')
    # заголовок новости
    h1 = soup.h1 # soup.find("h1")
    if h1:
        page_info["title"] = h1.text
    # дата и время
    script = soup.find("script", type="application/ld+json")
    if script:
        json_script = script.text
        try:
            data = json.loads(json_script)
        except json.decoder.JSONDecodeError:
            script = script.find_next("script", type="application/ld+json")
            json_script = script.text
            data = json.loads(json_script)
        date_time = data[3]["datePublished"]
        page_info["date"] = re.search(r"\d{4}-\d{2}-\d{2}", date_time)[0]
        page_info["time"] = re.search(r"\d{2}:\d{2}", date_time)[0]
    return page_info


def get_links_sub(url):
    '''Возвращает список ссылок на страницы, где опубликована новость.
    Используется функцией get_links()'''
    links = []
    page = requests.get(url, headers=HEADERS)
    if not page.ok :
        return None
    soup = BeautifulSoup(page.content, "html.parser")
    content_grid = soup.find_all("a", class_="atom-wrapper-body")
    for i in content_grid :
        url = i.get("href")
        links.append(url)
    return links


def get_links():
    '''Ищет ссылки на новости на всех страницах рубрики и возвращает их список'''
    begin_i = 2; end_i = 31
    links = []
    print(f'Загрузка ссылок из страницы 1 из {end_i-1}. Загружено {len(links)} ссылок.')
    ls = get_links_sub(SEED)
    if ls :
        links.extend(ls)
    for i in range (begin_i, end_i) :
        print(f'Загрузка ссылок из страницы {i} из {end_i-1}. Загружено {len(links)} ссылок.')
        ls = get_links_sub(SEED + "?page=" + str(i))
        if not ls :
            break
        links.extend(ls)
    return links


def main():
    links = get_links()
    top_news = []
    i = 1
    for link in links:
        print(f"{i} из {len(links)} Обрабатывается {link}")
        info = get_page_content(link)
        if not info:
            continue
        top_news.append(info)
        i += 1
    with open("www-techno-nv-ua.json", "wt", encoding="utf-8") as f:
        json.dump(top_news, f, indent=4, ensure_ascii=False)
    print("Работа завершена")


if __name__ == "__main__":
    main()