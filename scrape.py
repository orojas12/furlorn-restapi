import os
import time
import requests
from bs4 import BeautifulSoup


CAT_BREEDS_URL = "https://www.purina.com/cats/cat-breeds"
DOG_BREEDS_URL = "https://www.purina.com/dogs/dog-breeds"
CATS_HTML_FILE = "cats_html.txt"
DOGS_HTML_FILE = "dogs_html.txt"
CAT_BREEDS_FILE = "cat_breeds.txt"
DOG_BREEDS_FILE = "dog_breeds.txt"
PAGINATION = "https://www.purina.com/dogs/dog-breeds?page=15"


def get_html(url, path):
    """Requests html from url and saves text at path"""
    time.sleep(1)
    html = requests.get(url).text
    with open(path, "w") as f:
        f.write(html)


def scrape(html):
    def next_page(soup: BeautifulSoup):
        pass

    soup = BeautifulSoup(html, "html.parser")
    labels = soup.find_all(class_="callout-label")
    breeds = [label.h4.string for label in labels]

    soup = next_page(soup)

    while soup is not None:
        pass


def init():
    if CATS_HTML_FILE not in os.listdir("."):
        get_html(CAT_BREEDS_URL, CATS_HTML_FILE)
    if DOGS_HTML_FILE not in os.listdir("."):
        get_html(DOG_BREEDS_URL, DOGS_HTML_FILE)

    with open(CATS_HTML_FILE, "r") as f:
        cats_html = f.read()
    with open(DOGS_HTML_FILE, "r") as f:
        dogs_html = f.read()

    cat_breeds = scrape(cats_html)
    dog_breeds = scrape(dogs_html)

    print(cat_breeds, dog_breeds, sep="\n")


if __name__ == "__main__":
    init()
