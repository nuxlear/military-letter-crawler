import requests
import os.path
import json
import sys
import builtins
from bs4 import BeautifulSoup
from bs4 import Comment
from enum import Enum
import re
from datetime import datetime
'''
'''

class UserFileManager:
    username = ""
    userdata = []

    def __init__(self, username):
        self.username = username

    def addFunction(self, featName, params, className="builtins"):
        self.userdata.append([className, featName, params])
        print(self.userdata)

    def getData(self):
        return self.userdata

    def writeFile(self):
        text = ""
        for data in self.userdata:
            text = text + data[0] + "*::*" + data[1] + "*::*" + data[2] + "@##@"
        text = text.rstrip("@##@")

        with open('user_' + self.username + '.dat', mode='wt', encoding='utf-8') as w:
            w.write(text)

    def readFile(self):
        filePath = 'user_' + self.username + '.dat'
        self.userdata = []
        if os.path.isfile(filePath):
            print("[LOG] File exists. Start reading user data file.")
            with open(filePath, encoding='utf-8') as r:
                datas = r.readlines()[0].split("@##@")

            for data in datas:
                self.userdata.append(data.split("*::*"))
            return 0
        print("[LOG] File not exist. You should create user data file with UserDataFileManager class.")
        return -1

class AutoBodyMaker:
    username = ""
    userdata = []
    bodyResult = ""

    def __init__(self, username):
        self.username = username

    def run(self):
        self.userdata = self.__readFileData()
        for data in self.userdata:
            #Parse arguments for function call
            args = dict(arg for arg in data[2].split(",")) if data[2].find(",") != -1 else data[2]
            self.bodyResult += getattr(getattr(sys.modules[__name__],data[0]), data[1])(args) + "<br>"
            print("[LOG] " + data[1] + " function successfully called")
        return self.bodyResult

    def __readFileData(self):
        udfm = UserFileManager(self.username)
        udfm.readFile()
        return udfm.getData()

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
            splitForNL = cont.split("\n")
            pkg = []
            for line in splitForNL:
                pkg.append('<p>' + line + '</p>')
            print("cont-------------" + cont + "\n")
            self.send(name, title, ''.join(pkg))

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



if __name__ == "__main__":
    usfm = UserFileManager("sanop")
    usfm.addFunction("print", "프린트")
    usfm.addFunction("getWeather", "", "WeatherCrawler")
    usfm.writeFile()

    ar = AutoBodyMaker("sanop")
    print(ar.run())

