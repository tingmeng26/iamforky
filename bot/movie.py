import pandas as pd
import requests
import random
from bs4 import BeautifulSoup
# Create your views here.
def getMovie():
  # return '我想想'
  url = "https://movies.yahoo.com.tw/movie_thisweek.html"
  information = getNewMovie(url)
  # urlList = []
  # while url:
  #   urlList.append(url)
  #   url = getNext(url)
  # information = []
  # for row in urlList:
  #   data = getNewMovie(row)
  #   information = information.append(data)
  suggest = random.choice(information[0])
  key = information[0].index(suggest)
  answer = '最近有一部叫 '+ suggest + '\n'  + '介紹網址:'+ information[2][key] +'\n'+ information[3][key] 
  return answer
def getNext(url):
    r = requests.get(url)
    web_content = r.text
    soup = BeautifulSoup(web_content,'lxml')
    pageInfo = soup.find('div', class_='page_numbox')
    tagA = pageInfo.find('li', class_="nexttxt").find('a')
    if tagA:
        return tagA['href']
    else:
        return None
def getNewMovie(url):
 # 指定所要爬網的URL
  # url = 'https://movies.yahoo.com.tw/movie_thisweek.html'
# GET request from url and parse via BeautifulSoup
  r = requests.get(url)
# 擷取request回傳的文字部分
  web_content = r.text
# 使用BeautifulSoup來parse HTMl
  soup = BeautifulSoup(web_content, 'lxml')
  newMovie2 = soup.find_all('div', class_="release_movie_name")
  nameCHs = [t.find('a', class_='gabtn').text.replace('\n', '').replace(' ', '') for t in newMovie2]
  nameENs = [t.find('div', class_='en').find('a').text.replace('\n', '').replace(' ', '') for t in newMovie2]
  links = [t.find('a', class_='gabtn').get('href') for t in newMovie2]
  newMovie3 = soup.find_all('div', class_="release_movie_time")
  release = [t.text.replace('\n', '').replace(' ', '') for t in newMovie3]
  
  return [nameCHs,nameENs,links,release]
