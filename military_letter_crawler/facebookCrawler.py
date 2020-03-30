import argparse
import requests
import urllib.parse
import os.path
from bs4 import BeautifulSoup

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

#Will be changed : Managing page/group data for reading
def readTimeFile(pageName): #If file doesn't exist, return -1
    filePath = pageName + '_time.dat'
    if os.path.isfile(filePath):
        with open(filePath, encoding='utf-8') as r:
            return r.readline()
    return -1

def writeTimeFile(pageName, timeData):
    with open(pageName + '_time.dat', mode='wt', encoding='utf-8') as w:
        w.write(timeData)


# --Class PageFeed : Get facebook page/group's writing--
class FacebookCrawler:
    def remNotice(self, respSoup):
        i = 0
        for child in respSoup:
            if(child.select('._449j')):
                i += 1
            else:
                break
        return respSoup[i : int(len(respSoup))]


#  !Need to get pageName from page's URL manually!
    def pageFeed(self, pageName):
        req = requests.get("https://www.facebook.com/pg/" + pageName + "/posts/?ref=page_internal")
        soup = BeautifulSoup(req.content, "html.parser")

        respSoup = self.remNotice(soup.select('._4-u2 ._4-u8'))

        timeid = readTimeFile(pageName)
        writeTimeFile(pageName, respSoup[0].get_text().split(' · ')[0].split('대나무숲')[1])
        for child in respSoup:
            inf = child.get_text().split(' · ')[0]
            body = child.get_text().split(' · ')[1]
            if(inf.split('대나무숲')[1] == timeid):
                break
            print(inf + "----" + body)

    #Implementing.. need to add id checking feature
    def groupFeed(self, groupName):
        req = requests.get("https://www.facebook.com/groups/" + groupName)

        splited = req.content.decode('utf-8').split('<div data-testid="post_message" class="_5pbx userContent _3576" data-ft="&#123;&quot;tn&quot;:&quot;K&quot;&#125;"><p>')
        for i in range(1, len(splited)):
            print(splited[i].split("</p>")[0].replace("<br />", "\n"))


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
    pfc.groupFeed('System.out.Coding')