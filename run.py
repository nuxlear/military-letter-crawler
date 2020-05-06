from military_letter_crawler import *

from datetime import datetime


if __name__ == "__main__":
    client=LetterClient()
    client.login('julia981028@gmail.com', 'qwer1234!')
    fbc = FacebookCrawler()
    fbc.set_user('hwang')
    fbc.addPagetoList('SKKUBamboo',5)
    fbc.addPagetoList('yonseibamboo',5)
    fbc.addGrouptoList('KerasKorea', 5)
    fbc.addGrouptoList('System.out.Coding',5)
    fbcResult = fbc.autoRunFromFile()
    #print(fbcResult)
    client.send_letter("황준원","facebook M:"+str(datetime.today().month)+' D:'+str(datetime.today().day), fbcResult)
    client.send_letter("강원모","facebook M:"+str(datetime.today().month)+' D:'+str(datetime.today().day), fbcResult)
    
    wtc = WeatherCrawler()
    wtcResult = wtc.getWeather()
    client.send_letter("황준원","weather M:"+str(datetime.today().month)+' D:'+str(datetime.today().day), wtcResult)
    client.send_letter("강원모","weather M:"+str(datetime.today().month)+' D:'+str(datetime.today().day), wtcResult)
    
    naverResult = []
    googleResult = []
    coronaResult = []
    nc = NewsCrawler().NaverNews()
    nc.getNewsPage()
    naverResult.append(nc.getNewsTitles(nc.NewsType.LIFECULTURE))
    naverResult.append(nc.getNewsTitles(nc.NewsType.WORLD))
    naverResult.append(nc.getNewsTitles(nc.NewsType.ECONOMY))
    naverResult.append(nc.getNewsTitles(nc.NewsType.POLITIC))
    naverResult.append(nc.getNewsTitles(nc.NewsType.SOCIETY))
    naverResult.append(nc.getNewsTitles(nc.NewsType.ITSCIENCE))
    client.send_letter("황준원","NAVERN M:"+str(datetime.today().month)+' D:'+str(datetime.today().day), str(naverResult))
    client.send_letter("강원모","NAVERN M:"+str(datetime.today().month)+' D:'+str(datetime.today().day), str(naverResult))
    
    '''gc = NewsCrawler().GoogleNews()
    googleResult.append(gc.getNewsTitles(gc.CONST_HEADLINE_URL,5))
    googleResult.append(gc.getNewsTitles(gc.CONST_KOR_URL,5))
    googleResult.append(gc.getNewsTitles(gc.CONST_WORLD_URL,5))
    googleResult.append(gc.getNewsTitles(gc.CONST_BUSINESS_URL,5))
    googleResult.append(gc.getNewsTitles(gc.CONST_SCI_TECH_URL,5))
    googleResult.append(gc.getNewsTitles(gc.CONST_ENTERTAIN_URL,5))
    googleResult.append(gc.getNewsTitles(gc.CONST_SPORTS_URL,5))
    googleResult.append(gc.getNewsTitles(gc.CONST_HEALTH_URL,5))
    client.send_letter("황준원","googleN M:"+str(datetime.today().month)+' D:'+str(datetime.today().day), str(googleResult))
    client.send_letter("강원모","googleN M:"+str(datetime.today().month)+' D:'+str(datetime.today().day), str(googleResult))'''

    cc = NewsCrawler().Corona()
    coronaResult.append(cc.getTodayData())
    client.send_letter("황준원","coronaN M:"+str(datetime.today().month)+' D:'+str(datetime.today().day), str(coronaResult))
    client.send_letter("강원모","coronaN M:"+str(datetime.today().month)+' D:'+str(datetime.today().day), str(coronaResult))
    #fbc = FacebookCrawler()
    #fbc.set_user('ryu')
    #fbcResult = fbc.autoRunFromFile()
    #print(fbcResult)
    #wtc = WeatherCrawler()
    #wtcResult = wtc.getWeather()

    #newsList = []
    #nc = NewsCrawler.NaverNews()
    #nc.getNewsPage()
    #newsList.append(nc.getNewsTitles(nc.NewsType.LIFECULTURE))
    #newsList.append(nc.getNewsTitles(nc.NewsType.WORLD))

    #cc = NewsCrawler.Corona()
    #newsList.append(cc.getTodayData())

    #lc = LetterClient()

    #lc.login("rshtiger@naver.com", "")
    #lc.send_letter("김재이", "Facebook_SKKUBamboo", fbcResult)
