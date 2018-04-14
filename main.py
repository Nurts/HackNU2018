
import telebot
import constants
import requests
import json
import time
from currency_converter import CurrencyConverter

BOLD = '\033[1m'
END = '\033[0m'

bot = telebot.TeleBot(constants.token)


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.close()

def log(message, answer):
    print("\n ----------------")
    from datetime import datetime
    print(datetime.now())
    print("Message from {0} {1}. ( id = {2}) \n Text: {3}".format(message.from_user.first_name, message.from_user.last_name,
                                                                  str(message.from_user.id), message.text))
    print("Answer: " + answer)

def goo_shorten_url(url):
    post_url = constants.shortener_url
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    return r.json()['id']

#def sort_by_time(s, f):

@bot.message_handler(commands=['help'])
def handle_text(message):
    bot.send_message(message.from_user.id, """Я бот для поиска авиабилетов
Но я еще не готов к работе!""")

@bot.message_handler(commands=['start'])
def handle_text(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/start', '/end')
    user_markup.row('/next', '/choose time')
    bot.send_message(message.from_user.id, """Hello, I can help you to find the tickets to airplane.
    It will be easy to use me instead of surfing the Internet
    """, reply_markup=user_markup)

@bot.message_handler(commands=['end'])
def handle_text(message):
    hide_markup = telebot.types.ReplyKeyboardHide
    bot.send_message(message.from_user.id, "GoodBye" ,reply_markup=hide_markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.send_chat_action(message.from_user.id,'typing')
    answer = ""
    if message.text == "Hello" or message.text == "Привет" or message.text == "Пока" or message.text == "Bye":
        answer = message.text + "hello"
    elif len(message.text) > 10:
        checker = True

        if len(message.text.split(" "))== 4:
            cityFrom, cityTo, dateFrom, dateTo = message.text.split(" ")
            answer = cityFrom + " || " + cityTo + " || " + dateFrom + " || " + dateTo
            checker = False
        elif len(message.text.split(" "))== 3:
            cityFrom, cityTo, dateFrom = message.text.split(" ")
            dateTo = dateFrom
            checker = False


        if(checker == False):
            url = 'https://api.skypicker.com/flights?flyFrom=' + cityFrom + '&to=' + cityTo + '&dateFrom=' + dateFrom + '&dateTo=' + dateTo + '&partner=picky'
            req = requests.get(url)
            # req = unicode(req, "utf-8")
            # print(req.json())
            write_json(req.json())
            req_dict = req.json()

            tem1 = ""
            tem2 = ""
            tem3 = ""
            if 'data' in req_dict:
                if len(req_dict['data']) == 0:
                    answer = "No tickets"
                else:
                    ticket_url = None
                    min_cost = 10000
                    for each in req_dict['data']:
                        if min_cost > each['conversion']['EUR']:
                            ticket_url = each['deep_link']
                            min_cost = each['conversion']['EUR']
                            price = each['price']
                            c = CurrencyConverter()
                            tem1 = "From airport: " + BOLD + each['cityFrom'] +END + "  To airport: " + each['cityTo'] + "\n"
                            tem2 = "Time leaving: " + time.strftime("%D %H:%M", time.localtime(int(each['dTime']))) + "  Time arriving: " + time.strftime("%D %H:%M", time.localtime(int(each['aTime'])))
                            tem3 = "The best Price: €" + str(price) + " (" + str(c.convert(price,'EUR','USD'))[:6] + " USD)\n"

                    answer = tem3 + tem1 + tem2 + "\nFor more info:" + goo_shorten_url(ticket_url) + "\n"
            else:
                answer = "Input Error! Please try again!"

    else:
        answer = "I don't know"
    bot.send_message(message.from_user.id)
    log(message, answer)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

#if __name__ == 'hello':
