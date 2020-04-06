import requests
import os.path
import json
from bs4 import BeautifulSoup
from bs4 import Comment
from enum import Enum
import re

# --Class PageFeed : Get facebook page/group's writing--
'''
Usage
fbc = FacebookCrawler()
fbc.set_user("username")

fbc.addPagetoList or GroupList
fbc.auto~~.
or
fbc.pageFeed(...)
'''
class FacebookCrawler:
    userName = ""
    targList = dict()

    def set_user(self, uname):
        self.userName = uname
        filePath = 'user_' + uname + '.dat'
        if os.path.isfile(filePath):
            with open(filePath, encoding='utf-8') as r:
               self.targList = json.load(r)
            return
        self.initDict()

    def initDict(self):
        self.targList['Page'] = dict()
        self.targList['Group'] = dict()

    def addPagetoList(self, page_Name, count = 5):
        if page_Name in self.targList['Page']:
            return
        self.targList['Page'][page_Name] = dict()
        self.targList["Page"][page_Name]['tData'] = ""
        self.targList['Page'][page_Name]['count'] = count

    def addGrouptoList(self, group_Name, count = 5):
        if group_Name in self.targList['Group']:
            return
        self.targList['Group'][group_Name] = dict()
        self.targList['Group'][group_Name]['tData'] = ""
        self.targList['Group'][group_Name]['count'] = count

    def getTimeData(self, targName, targType): #If page doesn't exist in file, return -1
        return self.targList[targType][targName]["tData"] if self.targList[targType][targName]['tData'] != "" else -1, self.targList[targType][targName]['count']

    def writeTimeData(self, pageName, targType, timeData):
        self.targList[targType][pageName]['tData'] = timeData

    def writeUserFile(self, data):
        with open('user_' + self.userName + '.dat', mode='wt', encoding='utf-8') as w:
            json.dump(self.targList, w, indent="\t")

    def remDup(self, html, oldTimeID):
        for child in reversed(html):
            html.pop()
            if(child.find('a', {'class':'_5pcq'})['href'] == oldTimeID):
                break

    def remNotice(self, respSoup):
        i = 0
        for child in respSoup:
            if(child.select('._449j')):
                i += 1
            else:
                break
        return respSoup[i : int(len(respSoup))]

    def pageFeed(self, pageName):
        if self.userName == "":
            print("Need username")
            return
        req = requests.get("https://www.facebook.com/pg/" + pageName + "/posts/?ref=page_internal")
        soup = BeautifulSoup(req.content, "html.parser")

        contents = soup.select('.userContentWrapper')
        contents_no_notice = [x for x in contents if not x.select('._449j')]

        timeID, count = self.getTimeData(pageName, 'Page')

        if timeID != -1:
            self.remDup(contents_no_notice, timeID)
        contents_reversed = list(reversed(contents_no_notice))

        texts = []
        for i in range(0, min(count, len(contents_reversed))):
            timeID = contents_reversed[i].find('a', {'class':'_5pcq'})['href']
            user_content = contents_reversed[i].find_all(attrs={'data-testid': 'post_message'})
            text = ' '.join(map(lambda x: x.text, user_content))
            print(text)
            texts.append(text)

        self.writeTimeData(pageName, 'Page', timeID)
        return '\n'.join(texts)


    def groupFeed(self, groupName):
        if self.userName == "":
            print("Need username")
            return
        req = requests.get("https://www.facebook.com/groups/" + groupName)
        mainSoup = BeautifulSoup(req.content, 'html.parser')

        commentData = mainSoup.find_all(string=lambda text: isinstance(text, Comment))
        soup = BeautifulSoup(bytes(commentData[1], 'utf-8'), 'html.parser')
        contents = soup.select('._3ccb')

        timeID , count= self.getTimeData(groupName, 'Group')
        if timeID != -1:
            self.remDup(contents, timeID)
        contents_reversed = list(reversed(contents))

        texts = []
        for i in range(0, min(count, len(contents_reversed))):
            timeID = contents_reversed[i].find('a', {'class':'_5pcq'})['href']

            user_content = contents_reversed[i].find_all(attrs={'data-testid':'post_message'})
            text = '\n[--Indented Text--]\n'.join(map(lambda x: x.text, user_content))
            print(text)
            texts.append(text)

        self.writeTimeData(groupName, 'Group', timeID)
        return '\n'.join(texts)

    def autoRunFromFile(self):
        result = []
        for targ in self.targList['Page']:
            result.append('[[Page Name: ' + targ + ']]' + str(self.pageFeed(targ)))
        for targ in self.targList['Group']:
            result.append('[[Group Name: ' + targ + ']]' + str(self.groupFeed(targ)))
        self.writeUserFile(self.targList)
        return '\n'.join(result)


#Letter Sending Class
class LetterClient:
    host = 'https://www.thecamp.or.kr'

    def __init__(self):
        self.session = requests.Session()

    def _post(self, endpoint, data):
        response = self.session.post(self.host + endpoint, data=data)
        if response.status_code != 200:
            raise ConnectionError(f'Connection failed: [{response.status_code}] - {response.text}')
        return response.text

    def login(self, userid, passwd):
        endpoint = '/login/loginA.do'
        data = {
            'state': 'email-login',
            'autoLoginYn': 'N',
            'userId': userid,
            'userPwd': passwd,
        }

        result = self._post(endpoint, data)
        result = json.loads(result, encoding='utf-8')

        if 'resultCd' in result and result['resultCd'] == '0000':
            print(f'Successfully Login! [{userid}]')
            return True
        print(f'Login failed. [{result["resultMsg"] if "resultMsg" in result else "Unknown Error"}]')
        return False

    def add_soldier(self, group, name, birth, enter_date, train_unit, relation, phone=''):
        recruit_code = '0000490001'

        group_code = self.get_group_code(group)
        train_unit_code = self.get_train_unit_table(group)[train_unit]
        relation_code = self.get_relation_code(relation)

        endpoint = '/missSoldier/insertDirectMissSoldierA.do'
        data = {
            'missSoldierClassCd': recruit_code,
            'grpCd': group_code,
            'name': name,
            'birth': birth,
            'enterDate': enter_date,
            'trainUnitCd': train_unit_code,
            'phoneNo': phone,
            'missSoldierRelationshipCd': relation_code
        }

        result = self._post(endpoint, data)
        result = json.loads(result, encoding='utf-8')

        if 'resultCd' in result and result['resultCd'] == '0000':
            print(f'Successfully Registered! [{name}]')
            return True
        print(f'Register failed. [{result["resultMsg"] if "resultMsg" in result else "Unknown Error"}]')
        return False

    def send_letter(self, name, title, content):
        chkedContent = self.splitContent(content)


        for cont in chkedContent:
            print("cont-------------" + cont + "\n")
            self.send(name, title, cont)

    def send(self, name, title, content):
        cafes = self.get_cafes()
        if name not in cafes:
            print(f'No Cafe with name: [{name}].')
            return False
        if cafes[name] is None:
            print(f'Cafe[{name}] is not open yet.')
            return False

        mgr_seq = self._get_mgr_seq(*cafes[name])
        endpoint = '/consolLetter/insertConsolLetterA.do'
        data = {
            'boardDiv': '',
            'tempSaveYn': 'N',
            'sympathyLetterEditorFileGroupSeq': '',
            'fileGroupMgrSeq': '',
            'fileMgrSeq': '',
            'sympathyLetterMgrSeq': '',
            'traineeMgrSeq': mgr_seq,
            'sympathyLetterSubject': title,
            'sympathyLetterContent': content,
        }

        result = self._post(endpoint, data)
        #result = json.loads(result, encoding='utf-8')
        print(result)

    def splitContent(self, content):
        splited = content.split('\n')
        slen = 0
        bodies = []
        for i in range(0, len(splited)):
            if slen + len(splited[i]) > 1450:
                bodies.append('\n'.join(splited[:i - 1]) + '\n' +splited[i][:1450 - slen])
                bodies += self.splitContent(splited[i][1450-slen:] + '\n' + '\n'.join(splited[i + 1:]))
                return bodies
            slen += len(splited[i])
            if i == 24:
                bodies.append("\n".join(splited[:i]))
                bodies += self.splitContent('\n'.join(splited[i + 1:]))
                return bodies
        bodies.append(content)
        return bodies

    def get_cafes(self):
        endpoint = '/eduUnitCafe/viewEduUnitCafeMain.do'
        data = {}
        result = self._post(endpoint, data)
        soup = BeautifulSoup(result, 'html.parser')

        cafe_table = {}

        cafes = soup.select('.cafe-card-box')
        for cafe in cafes:
            name_div = cafe.select('.profile-wrap .id span')[0]
            name = name_div.text.split()[0]

            buttons = cafe.select('.btn-wrap')[0].find_all('a')

            for button in buttons:
                if button.text == '위문편지':
                    regex = re.compile('\'\d+\'')
                    codes = regex.findall(button['href'])

                    edu_seq, train_unit_code = map(lambda x: int(x[1:-1]), codes)
                    cafe_table[name] = (edu_seq, train_unit_code)
                    break
            else:
                cafe_table[name] = None
                continue

        return cafe_table

    def _get_mgr_seq(self, edu_seq, train_unit_code):
        endpoint = '/consolLetter/viewConsolLetterMain.do'
        data = {
            'trainUnitEduSeq': edu_seq,
            'trainUnitCd': train_unit_code,
        }
        result = self._post(endpoint, data)
        soup = BeautifulSoup(result, 'html.parser')

        letter_box = soup.select('.letter-card-box')[0]
        regex = re.compile('\'\d+\'')
        codes = regex.findall(letter_box['href'])

        mgr_seq = map(lambda x: int(x[1:-1]), codes)
        return mgr_seq

    def get_group_code(self, group_name):
        group_code_table = {
            '육군':   '0000010001',
            '해군':   '0000010002',
            '공군':   '0000010003',
            '해병대':  '0000010004',
        }
        if group_name not in group_code_table:
            return ''
        return group_code_table[group_name]

    def get_train_unit_table(self, group_name):
        # endpoint = '/selectCmmnCodeListA.do'
        # endpoint = '/join/selectCommCdListA.do'
        endpoint = '/join/selectTrainUnitListA.do'
        data = {
            'grpCd': self.get_group_code(group_name),
        }
        result = self._post(endpoint, data)
        result = json.loads(result, encoding='utf-8')

        unit_table = {}
        for unit in result['trainUnitList']:
            unit_table[unit['trainUnitNm']] = unit['trainUnitCd']
        return unit_table

    def get_relation_code(self, relation_name):
        relation_code_table = {
            '부모': '0000420001',
            '형제/자매': '0000420002',
            '배우자': '0000420003',
            '친척': '0000420004',
            '애인': '0000420005',
            '친구/지인': '0000420006',
            '팬': '0000420007',
        }
        if relation_name not in relation_code_table:
            return ''
        return relation_code_table[relation_name]

#News Crawler Class
class NewsCrawler:
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
            texts = []
            for child in self.soup.select("#ranking_10" + str(newsType.value) + " > ul"):
                texts.append(child.get_text())
            return '\n'.join(texts)

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
            texts = []
            for i in range(0, num):
                texts.append(soup.select(".DY5T1d")[i].get_text())
            return '\n'.join(texts)

    class Corona:
        def getTodayData(self):
            soup = BeautifulSoup(requests.get("http://ncov.mohw.go.kr/").content, "html.parser")
            texts = []
            for child in soup.select(".liveNum > .liveNum"):
                texts.append(re.sub('\n\+|\?\n|\n','',child.get_text().strip()))
            return ' '.join(texts)

#Weather Crawler Class
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

    fbc = FacebookCrawler()
    fbc.set_user('ryu')
    fbcResult = fbc.autoRunFromFile()
    print(fbcResult)
    wtc = WeatherCrawler()
    wtcResult = wtc.getWeather()

    newsList = []
    nc = NewsCrawler.NaverNews()
    nc.getNewsPage()
    newsList.append(nc.getNewsTitles(nc.NewsType.LIFECULTURE))
    newsList.append(nc.getNewsTitles(nc.NewsType.WORLD))

    cc = NewsCrawler.Corona()
    newsList.append(cc.getTodayData())

    lc = LetterClient()
    #print('\n'.join(newsList))
    lc.login("rshtiger@naver.com", "")
    lc.send_letter("김재이", ".", fbcResult)
