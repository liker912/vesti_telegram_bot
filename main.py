import parser
import db
import telebot
import time
import os
import helpers
import dotenv

dotenv.load_dotenv()

xml_rss = parser.get_rss_xml(os.getenv('URL_RSS'))  # xml body from URL_RSS
news_links = parser.get_links(xml_rss)  # artcles links

db.create_connection('./vesti_links.db')  # create connection to db

for index, link in enumerate(news_links):
    if db.check_link(link) is False:
        # Check if link is valid and
        # add to db not valid link
        if parser.run_parse(link) is False:
            db.add_link_to_db(link)
            continue

        news_article = parser.run_parse(link).copy()
        current_token = telebot.telegraph_get_token()
        try:
            telebot.init_telegraph(current_token)
            telegraph = telebot.telegraph_create_page({'title': news_article['title'], 'content': news_article['body']})
            telebot.send_2_channel(telegraph['url'])
            db.add_link_to_db(link)
            news_article.clear()
            time.sleep(int(os.getenv('DELAY_TIME')))
        except Exception as e:
            helpers.write_to_log("Catch from main\n" + str(e))
    else:
        continue

helpers.write_to_log("Bot finish", send_to_montitor_channel=False)
