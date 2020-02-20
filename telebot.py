import urllib.request
import ssl
import json
import os
import dotenv
from html_telegraph_poster import TelegraphPoster
from telegram.ext import Updater

dotenv.load_dotenv()
updater = Updater(token=os.getenv('BOT_TOKEN'), use_context=True)  # telegram api updater
dispatcher = updater.dispatcher  # telegram dispetcher
telegraph = None  # telegraph connection


# init connection with telegraph
def init_telegraph(token):
    global telegraph
    telegraph = TelegraphPoster(access_token=token)


# send publish telegraph url to telegram channel
def send_2_channel(text):
    dispatcher.bot.send_message(chat_id=os.getenv('CHANNEL_ID'), text=text)


# get token for telegraph post
# return string access_token
def telegraph_get_token():
    request = urllib.request.Request('https://api.telegra.ph/createAccount?short_name=vestiAnon&author_name=Anonimous')
    context = ssl.SSLContext()
    response = urllib.request.urlopen(request, context=context)

    return json.loads(response.read().decode('UTF-8'))['result']['access_token']


# send html article to telegraph
# return dict with publish article link in telegram
def telegraph_create_page(article):
    return telegraph.post(title=article['title'], author='Unknown', text=article['content'])


# send message to monitoring channel
def send_to_monitoring_channel(message):
    dispatcher.bot.send_message(chat_id=os.getenv('MONITORING_CHANNEL_ID'), text=message)
