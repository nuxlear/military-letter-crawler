from bs4 import BeautifulSoup
import requests
from enum import Enum

class NaverNewsType(Enum):
    POLITIC     = 0
    ECONOMY     = 1
    SOCIETY     = 2
    LIFECULTURE = 3
    WORLD       = 4
    ITSCIENCE   = 5

def getNaverNewsPage():
    newsPage = requests.get("https://news.naver.com/")
    return BeautifulSoup(newsPage.content, "html.parser")

def readNaverNews(soup, newsType):
    for child in soup.select("#ranking_10" + str(newsType.value) + " > ul"):
        print(child.get_text())

#Main 4 test
if __name__ == "__main__":
    soup = getNaverNewsPage()
    readNaverNews(soup, NaverNewsType.POLITIC)
