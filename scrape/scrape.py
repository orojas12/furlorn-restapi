import os
import time
import requests
import json
from json.decoder import JSONDecodeError
from bs4 import BeautifulSoup

ROOT_PATH = os.path.realpath(__file__)
ROOT_DIR, _ = os.path.split(ROOT_PATH)
BREEDS_FILENAME = "breeds.json"
BREEDS_PATH = os.path.join(ROOT_DIR, BREEDS_FILENAME)
CAT_PAGES_DIR = os.path.join(ROOT_DIR, "pages/cats")
DOG_PAGES_DIR = os.path.join(ROOT_DIR, "pages/dogs")
CATS_URL = "https://www.purina.com/cats/cat-breeds"
DOGS_URL = "https://www.purina.com/dogs/dog-breeds"


def get_html(url, base_url, dirpath):
    """Requests html from url and saves text at path"""
    time.sleep(2)
    print(f"[INFO] Downloading from {url}")
    html = requests.get(url).text
    save_page(html, dirpath)
    next_page = get_next_page_url(html, base_url)
    if next_page is None:
        return
    get_html(next_page, base_url, dirpath)


def save_page(html, dirpath):
    soup = BeautifulSoup(html, "html.parser")
    current_page_link = soup.find("a", class_="pagination-list-item-link_isActive")
    if current_page_link is None:
        raise Exception("Current page number could not be determined from html.")
    current_page_num = current_page_link["data-page-num"]
    with open(os.path.join(dirpath, f"page_{current_page_num}.txt"), "w") as f:
        f.write(html)


def get_next_page_url(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    next_page_link = soup.find("a", class_="paginationSkip_next")
    if next_page_link is None:
        return None
    next_page_url = base_url + next_page_link["href"]
    return next_page_url


def get_breeds(html):
    soup = BeautifulSoup(html, "html.parser")
    labels = soup.find_all(class_="callout-label")
    breeds = [label.h4.string for label in labels]
    return breeds


def create_empty_json_file(file):
    with open(file, "w") as f:
        data = dict()
        f.write(json.dumps(data))


def save(file, data: dict, key, value):
    with open(file, "w") as f:
        try:
            data[key] += value
        except KeyError:
            data[key] = value
        finally:
            f.write(json.dumps(data))


def save_to_file(file, key, value: list):
    try:
        with open(file, "r") as f:
            data = json.loads(f.read())
    except (FileNotFoundError, JSONDecodeError):
        save(file, dict(), key, value)
    save(file, data, key, value)


def scrape(src, dst, name):
    for i, file in enumerate(sorted(os.listdir(src))):
        with open(os.path.join(src, file), "r") as f:
            html = f.read()
        breeds = get_breeds(html)
        print(f"Page {i}", breeds, sep="\n")
        save_to_file(dst, name, breeds)


def init():
    if BREEDS_FILENAME not in os.listdir(ROOT_DIR):
        get_html(CATS_URL, CATS_URL, CAT_PAGES_DIR)
        get_html(DOGS_URL, DOGS_URL, DOG_PAGES_DIR)

    scrape(CAT_PAGES_DIR, BREEDS_PATH, "cat_breeds")
    scrape(DOG_PAGES_DIR, BREEDS_PATH, "dog_breeds")


if __name__ == "__main__":
    init()
