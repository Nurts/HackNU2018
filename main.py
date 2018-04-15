import telebot
import constants
import requests
import json
import time
from currency_converter import CurrencyConverter
from emoji import emojize

BOLD = '\033[1m'
END = '\033[0m'

bot = telebot.TeleBot(constants.token)

def make_request():
    answer = constants.error_message
    cur_data = json.load(open('cur_data.json'))
    url = 'https://api.skypicker.com/flights?flyFrom=' + cur_data['cityFrom'] + '&to=' + cur_data['cityTo'] + '&dateFrom=' + cur_data['dateFrom'] + \
          '&dateTo=' + cur_data['dateTo'] + '&partner=picky' + '&passengers=' + cur_data['passengers'] + '&adults=' + cur_data['adults'] + '&children=' +\
          cur_data['children'] + '&infants' + cur_data['infants'] + '&curr' + cur_data['curr'] + '&dtimefrom=' + cur_data['dtimefrom'] +\
          '&dtimeto=' + cur_data['dtimeto']
    req = requests.get(url)
    write_json(req.json())
    req_dict = req.json()
    print(url)
    if 'data' not in req_dict:
        return answer
    elif len(req_dict['data']) == 0:
        answer = "No tickets"
    else:
        answer = jsontoString(req_dict['data'][0])
    return answer

def jsontoString(each):
    emm1 = emojize(":credit_card:", use_aliases=True)
    emm2 = emojize(":customs:", use_aliases=True)
    emm3 = emojize(":arrow_upper_right:", use_aliases=True)
    emm4 = emojize(":arrow_lower_right:", use_aliases=True)
    emm5 = emojize(":information_source:", use_aliases=True)
    ticket_url = each['deep_link']
    price = each['price']
    c = CurrencyConverter()
    tem1 = emm2 + "*From airport:* " + each['cityFrom'] + "\n" + emm2 + "*To airport:* " + each['cityTo'] + "\n"
    tem2 = emm3 + "*Time leaving:* " + time.strftime("%D %H:%M", time.gmtime(int(each['dTime']))) + "\n" + emm4 + "*Time arriving:* " + time.strftime("%D %H:%M",time.gmtime(int(each['aTime'])))
    tem3 = emm1 + "*The best Price:* €" + str(price) + " (" + str(c.convert(price, 'EUR', 'USD'))[:6] + " USD)" + "\n"
    answer = tem3 + tem1 + tem2 + "\n" + emm5 + "For more info:" + goo_shorten_url(ticket_url) + "\n"
    return answer

def translate_text(text):
    req_url = constants.translate_url + 'key=' + constants.translate_key + '&text=' + text + "&lang=en"
    r = requests.post(req_url)
    return r.json()['text'][0]

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


@bot.message_handler(commands=['start', 'help'])
def handle_text(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/start', '/end')
    user_markup.row('/next', '/choose_time')
    m1 = "Hello, my dear friend!\n I can find the cheapest airline tickets for you!"
    m2 = "You have to just write some information about destinations and date in the given order:\n"
    m3 = "City from you will fly out"
    m4 = "City where you will fly"
    m5 = "Date of the fly or first day of the interval"
    m6 = "Last day of the interval(optional)"
    m7 = "For example:\n Moscow - Astana - 19/05/2018"
    m8 = " Almaty - Kazan - 16/04/2018 - 25/04/2018"
    m9 = "*You can use any language that you want:3*"
    em1 = emojize(":airplane:", use_aliases=True)
    em2 = emojize(":date:", use_aliases=True)
    em3 = emojize(":small_orange_diamond:", use_aliases=True)
    em4 = emojize(":small_blue_diamond:", use_aliases=True)
    em8 = emojize(":arrow_upper_right:", use_aliases=True)
    em9 = emojize(":arrow_lower_right:", use_aliases=True)
    em5 = emojize(":white_check_mark:", use_aliases=True)
    em6 = emojize(":warning:", use_aliases=True)
    sendtext=m1+em1+"\n"+m2+em3+m3+em8+"\n"+em4+m4+em9+"\n"+em3+m5+em2+"\n"+em4+m6+em2+"\n"+m7+em5+"\n"+m8+em5+"\n\n"+em6+m9
    msg = bot.send_message(message.from_user.id, sendtext, reply_markup=user_markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, initial_case_step)

@bot.message_handler(commands=['end'])
def handle_text(message):
    open('cur_data.json', 'w').close()
    hide_markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, "GoodBye", reply_markup=hide_markup)


@bot.message_handler(commands=['next'])
def handle_text(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    answer = "No more tickets";
    cur_data = json.load(open('cur_data.json'))
    cur_data['id'] = cur_data['id'] + 1
    write_json(cur_data, 'cur_data.json')
    req_dict = json.load(open('answer.json'))
    if len(req_dict['data']) <= cur_data['id']:
        pass
    else:
        answer = jsontoString(req_dict['data'][cur_data['id']])
    #answer = make_request()
    bot.send_message(message.from_user.id, answer, parse_mode="Markdown")

@bot.message_handler(commands=['choose_time'])
def handle_text(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/morning', '/afternoon')
    user_markup.row('/night', '/midnight')
    user_markup.row('/start', '/end')
    msg = bot.send_message(message.from_user.id, "Choose time from-to e.g 20:00 - 23:30", reply_markup=user_markup)
    bot.register_next_step_handler(msg, choose_time_step)

def choose_time_step(message):
    tfrom, tito = message.text.split('-')
    tfrom = " ".join(tfrom.split())
    tito = " ".join(tito.split())
    cur_data = json.load(open('cur_data.json'))
    cur_data['dtimefrom'] = tfrom
    cur_data['dtimeto'] = tito
    write_json(cur_data, 'cur_data.json')
    answer = make_request()
    bot.send_message(message.from_user.id, answer,parse_mode="Markdown")

def initial_case_step(message):
    bot.send_chat_action(message.from_user.id,'typing')
    answer = "Input Error! Please Try again!"
    if message.text == "Hello" or message.text == "Привет" or message.text == "Пока" or message.text == "Bye":
        answer = message.text
    elif len(message.text) > 10:
        checker = True


        if len(message.text.split("-")) == 4:
            cityFrom, cityTo, dateFrom, dateTo = message.text.split("-")
            checker = False
        elif len(message.text.split("-"))== 3:
            cityFrom, cityTo, dateFrom = message.text.split("-")
            dateTo = dateFrom
            checker = False

        if(checker == False):
            cityFrom = " ".join(cityFrom.split())
            cityTo = " ".join(cityTo.split())
            dateFrom = " ".join(dateFrom.split())
            dateTo = " ".join(dateTo.split())
            cityFrom = translate_text(cityFrom)
            cityTo = translate_text(cityTo)
            data = {"cityFrom":cityFrom, "cityTo":cityTo, "dateFrom":dateFrom, "dateTo":dateTo,
                    "dtimefrom":'00:00', "dtimeto":"00:00", "passengers":'1', "adults":'1',"children":'0',
                    "infants":'0', "curr":'EUR', "id":0}
            write_json(data, filename='cur_data.json')
            answer = make_request()
    else:
        answer = constants.tryagain_message
    msg = bot.send_message(message.from_user.id, answer,parse_mode="Markdown")
    if answer == constants.tryagain_message:
        bot.register_next_step_handler(msg, initial_case_step)
    log(message, answer)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
