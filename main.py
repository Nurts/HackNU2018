
import telebot
import constants
import requests
import json
import time

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


@bot.message_handler(commands=['help'])
def handle_text(message):
    bot.send_message(message.from_user.id, """Я бот для поиска авиабилетов
Но я еще не готов к работе!""")

@bot.message_handler(commands=['start'])
def handle_text(message):
    bot.send_message(message.from_user.id, """Hello, I can help you to find the tickets to airplane.
    It will be easy to use me instead of surfing the Internet
    """)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    answer = ""
    if message.text == "Hello" or message.text == "Привет" or message.text == "Пока" or message.text == "Bye":
        answer = message.text + "hello"
    elif len(message.text) > 10:
        if len(message.text.split(" "))== 4:
            cityFrom, cityTo, dateFrom, dateTo = message.text.split(" ")
            answer = cityFrom + " || " + cityTo + " || " + dateFrom + " || " + dateTo
        elif len(message.text.split(" "))== 3:
            cityFrom, cityTo, dateFrom = message.text.split(" ")
            dateTo = dateFrom
        answer = cityFrom + " || " + cityTo + " || " + dateFrom + " || " + dateTo
        url = 'https://api.skypicker.com/flights?flyFrom=' + cityFrom + '&to=' + cityTo + '&dateFrom=' + dateFrom + '&dateTo=' + dateTo + '&partner=picky'
        req = requests.get(url)
        #req = unicode(req, "utf-8")
        #print(req.json())
        write_json(req.json())
        req_dict = req.json()
<<<<<<< HEAD
        ticket_url = None
        min_cost = 10000
        tem1 = ""
        tem2= ""
=======
>>>>>>> caa89f31a2ab532ecb9da4671fdd58829847044a
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
<<<<<<< HEAD
                        tem1 = "From airport: " + each['cityFrom']+"  To airport: "+ each['cityTo']+"\n"
                        tem2 = "Time leaving: " + time.strftime("%D %H:%M", time.localtime(int(each['dTime']))) +"  Time arriving: " + time.strftime("%D %H:%M", time.localtime(int(each['aTime']))) +"\n Time in flight"

                    answer = tem1 + tem2 + "For more info:" + ticket_url + "\n"
=======
                answer = goo_shorten_url(ticket_url)

>>>>>>> caa89f31a2ab532ecb9da4671fdd58829847044a
        else:
            answer = "Input Error! Please try again!"

    else:
        answer = "I don't know"
    bot.send_message(message.from_user.id, answer)
    log(message, answer)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

#if __name__ == 'hello':
