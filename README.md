# Military Letter & Crawler

## Introduction

훈련소에서 인터넷편지를 통해 외부 소식을 전해 들을 수 있도록 웹페이지에서 내용을 크롤해 와서 편지로 보내는 라이브러리입니다. 

## Requirements
Python 3.7 에서 작성된 코드입니다. 정상 동작을 위해 Python 3 버전 이상을 사용해주세요. 

필요한 라이브러리 및 패키지는 다음과 같습니다. 
```text
requests
beautifulsoup4
```

## Usage
```python
import military_letter_crawler as mlc

client = mlc.LetterClient()
client.login('username@email.com', 'password')
```

## Contribution

- [Junwon Hwang](https://github.com/nuxlear)