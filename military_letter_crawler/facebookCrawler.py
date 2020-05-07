import argparse
import requests
import urllib.parse
import os.path
import json
from bs4 import BeautifulSoup
from bs4 import Comment

'''
def login(session, email, password):
    # 원본 코드 : https://gist.github.com/UndergroundLabs/fad38205068ffb904685

    세션으로 페이스북 로그인을 시도하는 함수
    성공 여부를 bool값으로 반환함 (`True` : 성공)

    # Facebook 쿠키 로드를 위한 홈페이지 탐색
    response = session.get('https://m.facebook.com')

    # 로그인 POST 요청
    response = session.post('https://m.facebook.com/login.php', data={
        'email': email,
        'pass': password
    }, allow_redirects=False)

    # 응답에 c_user 쿠키가 있으면 성공
    if 'c_user' in response.cookies:
        # fb_dtsg 토큰 파싱을 위해 홈페이지 로드
        # homepage_resp = session.get('https://m.facebook.com/home.php')
        # soup = BeautifulSoup(homepage_resp.text.encode('utf8'), 'html.parser')
        # fb_dtsg = soup.find('input', {'name':'fb_dtsg'}).get('value')

        return True
    else:
        print(response.status_code)
        return False
    '''



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

    def setUser(self, uname):
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
            return False
        self.targList['Page'][page_Name] = {'tData': "", 'count': count}
        return True

    def addGrouptoList(self, group_Name, count = 5):
        if group_Name in self.targList['Group']:
            return
        self.targList['Group'][group_Name] = {'tData': "", 'count': count}
        return True

    def getTimeData(self, targName, targType):
        # If page doesn't exist in file, return -1
        return self.targList[targType][targName]["tData"] if self.targList[targType][targName]['tData'] != "" else -1, self.targList[targType][targName]['count']

    def writeTimeData(self, pageName, targType, timeData):
        self.targList[targType][pageName]['tData'] = timeData

    def writeUserFile(self, data):
        with open('user_' + self.userName + '.dat', mode='wt', encoding='utf-8') as w:
            json.dump(self.targList, w, indent="\t")

    def remDup(self, html, oldTimeID):
        '''Remove duplicated feeds which are already sent. '''
        bup = html[:]
        for child in reversed(html):
            bup.pop()
            if child.find('a', {'class':'_5pcq'})['href'] == oldTimeID:
                return bup
        return html

    def remNotice(self, respSoup):
        '''Remove notice feed. '''
        i = 0
        for child in respSoup:
            if child.select('._449j'):
                i += 1
            else:
                break
        return respSoup[i : int(len(respSoup))]

    def pageFeed(self, pageName):
        if self.userName == "":
            print("Need username")
            return None

        req = requests.get("https://www.facebook.com/pg/" + pageName + "/posts/?ref=page_internal")
        soup = BeautifulSoup(req.content, "html.parser")

        contents = soup.select('.userContentWrapper')
        contents_no_notice = [x for x in contents if not x.select('._449j')]

        timeID, count = self.getTimeData(pageName, 'Page')
        if timeID != -1:
            contents_no_notice = self.remDup(contents_no_notice, timeID)
        contents_reversed = list(reversed(contents_no_notice))

        print(contents_reversed)
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
            contents = self.remDup(contents, timeID)
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


if __name__ == "__main__":
    '''
    parser = argparse.ArgumentParser(description='Facebook 로그인')
    parser.add_argument('email', help='이메일')
    parser.add_argument('password', help='비밀번호')

    args = parser.parse_args()

    session = requests.session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:39.0) Gecko/20100101 Firefox/39.0'
    })

    if login(session, args.email, args.password):
        print('로그인 성공')
    else:
        print('로그인 실패')
    '''
    pfc = FacebookCrawler()
    pfc.set_user("ryu")
    pfc.addPagetoList('SKKUBamboo')
    pfc.addGrouptoList('KerasKorea', 5)
    pfc.addGrouptoList('System.out.Coding')
    pfc.autoRunFromFile()
    # pfc.groupFeed('System.out.Coding')
    pages = [
    #    'thisisgamecom',
        'SKKUBamboo',
    #    'yonseibamboo',
    #    'SNUBamboo',
    #    'ggyuggyuggyaggya',
    ]

    #for page in pages:
    #    pfc.pageFeed(page)

    groups = [
        'KerasKorea',
        'System.out.Coding',
    ]

    #for group in groups:
    #    pfc.groupFeed(group)