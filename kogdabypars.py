import requests
from bs4 import BeautifulSoup as Soup
import urllib3
import sqlite3
import json
import telebot
from telebot import types
from operator import itemgetter
from datetime import datetime, date, time



def get_list(stop_name):
    stop_name_ = stop_name
    try:
        stop_name_.replace(' ','\u0020')
    except:
        pass

    http = urllib3.PoolManager()
    r = http.request('GET','https://kogda.by/stops/brest/{}'.format(stop_name_))
    soup = Soup(r.data, 'html.parser')
    a = soup.select('[class~=js-time-row]')
    b = soup.select('[class~=direction]')
    all_transport = list()

    for i in range(len(a)):
        direct = b[i].contents[0]
        direct = direct.replace('\r', '')
        direct = direct.replace('\n', '')
        direct = direct.lstrip()
        direct = direct.rstrip()

        all_transport.append([direct, a[i]['data-route'], int(a[i]['data-interval']), a[i]['data-transport']])

    all_transport =  sorted(all_transport, key=itemgetter(2))
    return all_transport


def get_time_closest(stop_name):

    all_transport = get_list(stop_name)

    text = ''; iteration = 0
    for i in all_transport:
        if i[3] == 'autobus':
            text += '🚌 № ' + i[1] + ' через ' + str(i[2]) + ' мин., направление: '+ i[0]  +  '\n\n'
        elif i[3] == 'trolleybus':
            text += '🚎 № ' + i[1] + ' через ' + str(i[2]) + ' мин., направление: '+ i[0]  +  '\n\n'
        iteration += 1

        if iteration == 4:
            break

    keyboard = types.InlineKeyboardMarkup(row_width = 1)
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data = 'back'))

    if len(all_transport) > 5:
        keyboard.add(types.InlineKeyboardButton('Показать больше', callback_data = 'more_' + stop_name))
 

    return text, keyboard
        

def get_time_all(stop_name):
    
    all_transport = get_list(stop_name)

    text = ''
    for i in all_transport:
        if i[3] == 'autobus':
            text += '🚌 № ' + i[1] + ' через ' + str(i[2]) + ' мин., направление: '+ i[0]  +  '\n\n'
        elif i[3] == 'trolleybus':
            text += '🚎 № ' + i[1] + ' через ' + str(i[2]) + ' мин., направление: '+ i[0]  +  '\n\n'

    keyboard = types.InlineKeyboardMarkup(row_width = 1)
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data = 'back'))

    return text, keyboard



def get_busses(stop_name):
    stop_name_ = stop_name
    try:
        stop_name_.replace(' ','\u0020')
    except:
        pass

    http = urllib3.PoolManager()
    r = http.request('GET','https://kogda.by/stops/brest/{}'.format(stop_name_))
    soup = Soup(r.data, 'html.parser')

    numbers_class = soup.select('[class~=btn]')

    keyboard = types.InlineKeyboardMarkup(row_width = 3)

    for i in numbers_class:
        try:
            if i["data-transport"] == 'autobus':
                keyboard.add(types.InlineKeyboardButton('🚌 ' + i["data-route"], callback_data = i["data-transport"] + '_' + i["data-route"]))
            else:
                keyboard.add(types.InlineKeyboardButton('🚎 ' + i["data-route"], callback_data = i["data-transport"] + '_' + i["data-route"]))

        except:
            pass
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data = 'back_to_stops'))

    return keyboard


def get_directs(transport,number):

    http = urllib3.PoolManager()
    r = http.request('GET','https://kogda.by/routes/brest/{transport}/{number}'.format(transport = transport, number = number))
    soup = Soup(r.data, 'html.parser')
    directs_classes = soup.select('[class~=panel-title]')

    keyboard = types.InlineKeyboardMarkup(row_width = 1)

    for i in directs_classes:
        direct = str(i.contents)
        direct = direct[direct.find('\n') : ]
        direct = direct[ : direct.find('</a>')]
        direct = direct.lstrip()
        direct = direct.rstrip()

        keyboard.add(types.InlineKeyboardButton(direct , callback_data = 'd_' + direct))
        print('direct_' + direct)
    
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data = 'back_to_numbers'))

    return keyboard


def get_time_for_day(transport, number, direct, stop):

    url = """https://kogda.by/api/getTimetable?city=brest
    &transport={transport}
    &route={number}
    &direction={direct}
    &busStop={stop}
    &date={date}""".format(
        transport = transport,
        number = number,
        direct = direct.replace(' ', '+'),
        stop = stop.replace(' ', '+'),
        date = datetime.strftime(datetime.today(), "%Y-%m-%d")        
        )

    payload = {}
    headers = {
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    }

    response = requests.request("GET", url, headers=headers, data = payload)


    rasp = json.loads(response.text)

    amount = 0
    text = ''
    for i in rasp['timetable']:
        if amount < 4:
            text += 'ℹ️' + i + ' '
            amount += 1
        if amount == 4:
            text += '\n'
            amount = 0 
    

    keyboard = types.InlineKeyboardMarkup(row_width = 1)
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data = 'back_to_directs'))
    
    return text, keyboard

