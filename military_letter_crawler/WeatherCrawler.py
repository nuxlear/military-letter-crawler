import requests
from bs4 import BeautifulSoup

class WeatherCrawler:

    def parseWeatherInfo(self, tBodySoup):
        mTemp = tBodySoup.select(".cell")[0].select(".temp")[0].get_text()
        aTemp = tBodySoup.select(".cell")[1].select(".temp")[0].get_text()

        if len(tBodySoup.select("th")) == 0:
            date = "내일"
            mSplit = tBodySoup.select(".cell")[0].select(".info")[0].get_text().split("강수확률")
            aSplit = tBodySoup.select(".cell")[1].select(".info")[0].get_text().split('강수확률')
            morning = mTemp + "℃ - " + mSplit[0] + ' - 강수확률' + mSplit[1]
            afternoon = aTemp + "℃ - " + aSplit[0] + ' - 강수확률 ' + aSplit[1]
        else:
            date = tBodySoup.select("th")[0].get_text()
            morning = mTemp + "℃ - " + tBodySoup.select(".cell")[0].select(".info")[0].get_text()
            afternoon = aTemp + "℃ - " + tBodySoup.select(".cell")[1].select(".info")[0].get_text()

        return '(' + date + ', ' + morning + ', ' + afternoon + ')'

    def getWeather(self):
        req = requests.get("https://weather.naver.com/rgn/townWetr.nhn?naverRgnCd=15230253")
        soup = BeautifulSoup(req.content, 'html.parser')
        respSoup = soup.select("table")

        result = []
        result.append(self.parseWeatherInfo(respSoup[1].select("td")[1]))
        for child in respSoup[2].select("tr"):
            result.append(self.parseWeatherInfo(child))

        return '\n'.join(result)


if __name__ == "__main__":
    wc = WeatherCrawler()
    print(wc.getWeather())