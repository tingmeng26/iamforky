# import 必要的函式庫
from django.conf import settings
from . import food
from . import movie
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import random
from datetime import datetime
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
# 這邊是Linebot的授權TOKEN(等等註冊LineDeveloper帳號會取得)，我們為DEMO方便暫時存在settings裡面存取，實際上使用的時候記得設成環境變數，不要公開在程式碼裡喔！
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):

    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                answer = get_answer(event.message.text)
                if "findWeather" in answer and "tomorrow" in answer:
                  city = answer[-3:]
                  answer = get_tomorrow_weather(city)
                elif "findWeather" in answer:
                  city = answer[-3:]
                  answer = get_weather(city)
                elif "giveMeFood" in answer:
                  answer = get_food()
                elif "findMovie" in answer:
                  answer = get_movie()
                elif "No good match found in KB." in answer:
                  answer = '我不是很瞭解你的意思，可以再說的清楚一點嗎?'
                line_bot_api.reply_message(
                    event.reply_token,
                   TextSendMessage(text=answer)
                
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def get_answer(message_text):
  url = " https://coderbottest.azurewebsites.net/qnamaker/knowledgebases/b7c53c1a-161d-44cd-9564-a29690e16b15/generateAnswer"
  response = requests.post(
                   url,
                   json.dumps({'question': message_text}),
                   headers={
                       'Content-Type': 'application/json',
                       'Authorization': 'EndpointKey f45fa2e5-7e47-4797-9796-8336fabc078b'
                   }
               )


  data = response.json()

  try:
    if "error" in data:
      return data["error"]["message"]
    answer = data['answers'][0]['answer']
    if answer == 'No good match found in KB.':
      answer = '我不是很瞭解你的意思，可以再說的清楚一點嗎?'
      
    return answer
  except Exception:
    return "Error occurs when finding answer"
# 取得近6小時氣象預報
def get_weather(city='臺中市'):
  url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWB-6FD89976-0056-4F5B-9D7F-CC1A137C75CF&locationName="+city
  response = requests.get(url)
  data = response.json()
  answer = data['records']['location'][0]['locationName'] + ' 未來6小時為 ' + data['records']['location'][0]['weatherElement'][0]['time'][0]['parameter']['parameterName'] + '\n' + '氣溫' + data['records']['location'][0]['weatherElement'][2]['time'][0]['parameter']['parameterName'] + ' ~ ' + data['records']['location'][0]['weatherElement'][4]['time'][0]['parameter']['parameterName'] + '度 ' + '\n' + '降雨機率 ' + data['records']['location'][0]['weatherElement'][1]['time'][0]['parameter']['parameterName'] + '%'
  if int(data['records']['location'][0]['weatherElement'][1]['time'][0]['parameter']['parameterName']) > 50:
    answer = answer+ '\n要記得帶傘喔'
  return answer
# 取得明日該地區氣象預報
def get_tomorrow_weather(city='臺中市'):
  url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWB-6FD89976-0056-4F5B-9D7F-CC1A137C75CF&format=JSON&locationName="+city
  response = requests.get(url)
  data = response.json()
  now = datetime.now()
  answer = '明日 '+ city+' '
  i=0
  for row in data['records']['location'][0]['weatherElement'][0]['time']:
    if now.strftime('%Y-%m-%d') != row['startTime'][0:10]:
      answer = answer + row['startTime'][0:-3] + ' ~ ' + row['endTime'][-8:-3] + '\n' +data['records']['location'][0]['weatherElement'][0]['time'][i]['parameter']['parameterName']+ '\n' + '氣溫' + data['records']['location'][0]['weatherElement'][2]['time'][i]['parameter']['parameterName'] + ' ~ ' + data['records']['location'][0]['weatherElement'][4]['time'][i]['parameter']['parameterName'] + '度 ' +'\n'+ '降雨機率 ' + data['records']['location'][0]['weatherElement'][1]['time'][i]['parameter']['parameterName'] + '%'+'\n'
      i += 1
  return answer
# 取得食物推薦
def get_food():
  foodList = food.food
  foodItem = random.choice(foodList)
  return '來個' + foodItem + '如何?'
# 取得電影推薦
def get_movie():
  # answer = '我想想'
  answer = movie.getMovie()
  return answer
