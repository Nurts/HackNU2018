#hmmm
"""
so this is a comment
"""
import telebot
import constants
import requests
import json

bot = telebot.TeleBot(constants.token)


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log(message, answer):
    print("\n ----------------")
    from datetime import datetime
    print(datetime.now())
    print("Message from {0} {1}. ( id = {2}) \n Text: {3}".format(message.from_user.first_name, message.from_user.last_name,
                                                                  str(message.from_user.id), message.text))
    print("Answer: " + answer)


@bot.message_handler(commands=['help'])
def handle_text(message):
    bot.send_message(message.from_user.id, """Я бот для поиска авиабилетов
Но я еще не готов к работе!""")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    answer = ""
    if message.text == "Hello" or message.text == "Привет" or message.text == "Пока" or message.text == "Bye":
        answer = message.text + "!"
    else:
        cityFrom, cityTo, dateFrom, dateTo = message.text.split(" ")
        answer = cityFrom + " || " + cityTo + " || " + dateFrom + " || " + dateTo
        url = 'https://api.skypicker.com/flights?flyFrom=' + cityFrom + '&to=' + cityTo + '&dateFrom=' + dateFrom + '&dateTo=' + dateTo + '&partner=picky'
        req = requests.get(url)
        print(req.json())
        #write_json(req.json())

    bot.send_message(message.from_user.id, answer)
    log(message, answer)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

#if __name__ == 'hello':
