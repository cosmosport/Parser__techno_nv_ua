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

    
    def parse_content_wrapper():
        nonlocal body_list, page_info, wrapper, soup
        try:
            page_info["img"] = soup.find("div", class_="article__content__head_img").find("img").get("src")
        except Exception:
            pass
        body_list = wrapper.find_all("p")


    def parse_main_wraper():
        nonlocal body_list, page_info, wrapper
        page_info["img"] = wrapper.find("img").get("src")
        if wrapper.find("div", class_="content_wrapper"):
            print("content_wrapper inside main_wrapper -- cosmosport")
        elif wrapper.find("div", class_="content-grid"):
            print("content-grid inside main_wrapper -- cosmosport")
        body_list = wrapper.find_all("p")


    page = requests.get(link)
    soup = BeautifulSoup(page.content.decode("utf-8"), "html.parser")
    body_list = None
    wrapper = soup.find("div", class_="content_wrapper")
    # Выбор функции для парсинга в зависимости от типа html страницы
    if wrapper:
        parse_content_wrapper()
    else:
        wrapper = soup.find("div", class_="main-wrapper") # content-grid 
        if wrapper:
            parse_main_wraper()
    # автор новости (если указывается)
    try:
        page_info["author"] = wrapper.find("a", class_="opinion_author_name").text
    except Exception:
        pass
    # текст новости
    if body_list :
        for i in body_list :
            page_info["body"] += i.text + "\n\n"
    # заголовок новости
    h1 = soup.h1 # soup.find("h1")
    if h1:
        page_info["title"] = h1.text
    # дата и время
    script = soup.find("script", type="application/ld+json")
    if script:
        json_script = script.text
        # print(json_script)
        try:
            data = json.loads(json_script)
        except json.decoder.JSONDecodeError:
            print("Exception: json.decoder.JSONDecodeError -- cosmosport")
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
    links = []
    ls = get_links_sub(SEED)
    if ls :
        links.extend(ls)
    for i in range (2, 31) :
        ls = get_links_sub(SEED + "?page=" + str(i))
        if not ls :
            break
        links.extend(ls)
    return links


def main():
    links = get_links()
    top_news = []
    for link in links:
        print(f"Обрабатывается {link}")
        try:
            info = get_page_content(link)
        except Exception:
            continue
        top_news.append(info)

    with open("www-techno.nv.ua.json", "wt", encoding="utf-8-sig") as f:
        try:
            json.dump(top_news, f, indent=4, ensure_ascii=False)
        except Exception:
            print("json.dump error -- cosmosport")
    print("Работа завершена")


if __name__ == "__main__":
    main()