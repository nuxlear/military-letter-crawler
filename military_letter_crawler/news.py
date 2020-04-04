from bs4 import BeautifulSoup
import requests
from enum import Enum
import re

class NaverNews:
    soup = ""
    class NewsType(Enum):
        POLITIC     = 0
        ECONOMY     = 1
        SOCIETY     = 2
        LIFECULTURE = 3
        WORLD       = 4
        ITSCIENCE   = 5

    def getNewsPage(self):
        newsPage = requests.get("https://news.naver.com/")
        self.soup = BeautifulSoup(newsPage.content, "html.parser")

    def getNewsTitles(self, newsType):
        for child in self.soup.select("#ranking_10" + str(newsType) + " > ul"):
            print(child.get_text())

class GoogleNews:
    soup = ""
    CONST_HEADLINE_URL = "https://news.google.com/?hl=ko&gl=KR&ceid=KR%3Ako"
    CONST_KOR_URL = "https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRFp4WkRNU0FtdHZLQUFQAQ?hl=ko&gl=KR&ceid=KR%3Ako"
    CONST_WORLD_URL = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtdHZHZ0pMVWlnQVAB?hl=ko&gl=KR&ceid=KR%3Ako"
    CONST_BUSINESS_URL = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtdHZHZ0pMVWlnQVAB?hl=ko&gl=KR&ceid=KR%3Ako"
    CONST_SCI_TECH_URL = "https://news.google.com/topics/CAAqKAgKIiJDQkFTRXdvSkwyMHZNR1ptZHpWbUVnSnJieG9DUzFJb0FBUAE?hl=ko&gl=KR&ceid=KR%3Ako"
    CONST_ENTERTAIN_URL = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtdHZHZ0pMVWlnQVAB?hl=ko&gl=KR&ceid=KR%3Ako"
    CONST_SPORTS_URL = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtdHZHZ0pMVWlnQVAB?hl=ko&gl=KR&ceid=KR%3Ako"
    CONST_HEALTH_URL = "https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtdHZLQUFQAQ?hl=ko&gl=KR&ceid=KR%3Ako"

    def getNewsTitles(self, newsURL, num):
        newsPage = requests.get(newsURL)
        soup = BeautifulSoup(newsPage.content, "html.parser")
        for i in range(0, num):
            print(soup.select(".DY5T1d")[i].get_text())

class Corona:
    def getTodayData(self):
        soup = BeautifulSoup(requests.get("http://ncov.mohw.go.kr/").content, "html.parser")
        for child in soup.select(".liveNum > .liveNum"):
            print(re.sub('\n\+|\?\n|\n','',child.get_text().strip()))


#Main 4 test
if __name__ == "__main__":
    naverNews = NaverNews()
    naverNews.getNewsPage()
    for i in range(0, 5):
        naverNews.getNewsTitles(i)
    #gNews = GoogleNews()
    #gNews.getNewsTitles(GoogleNews.CONST_HEADLINE_URL, 5)
    cor = Corona()
    cor.getTodayData()
