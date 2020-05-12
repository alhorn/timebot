import config
import telebot
from telebot import types
import requests 
import json
import sqlite3
from math import radians, cos, sin, asin, sqrt

from similarsearch import Similar
from stoplist import Stops
import kogdabypars
from stop_from_chat import Stop_From_Chat

bot = telebot.TeleBot(config.TOKEN)

Users = {}
Stops_from_chat = {}

@bot.message_handler(commands = ['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton("GEO", request_location = True)
    markup.add(item1)
    bot.send_message(message.chat.id,'Здравствуйте, ' + message.from_user.first_name, reply_markup = markup)



@bot.message_handler(content_types = ['location'])
def answ(message):
    if message.chat.type == 'private':
        Users[message.from_user.id] = Stops(message.location.latitude , message.location.longitude)
        Users[message.from_user.id].get_stops()
        bot.send_message(message.chat.id, 'Ближайшие остановки:', reply_markup = Users[message.from_user.id].close_stops_keyboard())
# message.location.latitude , message.location.longitude



@bot.message_handler(content_types = ['text'])
def send_mes(message):
    keyboard_or_nothing = Similar().get_similar(message.text)
    if keyboard_or_nothing != 'Ничего не найдено':        
        Stops_from_chat[message.from_user.id] = Stop_From_Chat(keyboard_or_nothing)

        bot.send_message(message.chat.id, "Наиболее подходящие названия:" , reply_markup = keyboard_or_nothing, parse_mode= "Markdown")
    else:
        bot.send_message(message.chat.id, "Ничего не найдено" , reply_markup = None, parse_mode= "Markdown")







@bot.callback_query_handler(func = lambda call: True)
def callback_inline(call):

    if call.data == 'see_all':
        bot.edit_message_reply_markup(message_id = call.message.message_id, 
        chat_id = call.message.chat.id,
        reply_markup = Users[call.from_user.id].all_stops_keyboard())
    
    if call.data.split('_')[0] == 'stop':
        # print(call.data.split('_')[1])
        text, keyboard = kogdabypars.get_time_closest(call.data.split('_')[1])
        bot.edit_message_text(
        message_id = call.message.message_id, 
        chat_id = call.message.chat.id,
        text = text, 
        reply_markup = keyboard
        )
        

    if call.data == 'back':
        bot.edit_message_text(
        message_id = call.message.message_id, 
        chat_id = call.message.chat.id,
        text = 'Ближайшие остановки:', 
        reply_markup = Users[call.from_user.id].close_stops_keyboard()  
        )
    
    if call.data.split('_')[0] == 'more':
        text, keyboard = kogdabypars.get_time_all(call.data.split('_')[1])
        bot.edit_message_text(
        message_id = call.message.message_id, 
        chat_id = call.message.chat.id,
        text = text, 
        reply_markup = keyboard  
        )

    if call.data.split('_')[0] == 'stopfromchat':
        Stops_from_chat[call.from_user.id].chosen_stop = call.data.split('_')[1]
        Stops_from_chat[call.from_user.id].busses = kogdabypars.get_busses(Stops_from_chat[call.from_user.id].chosen_stop)

        bot.edit_message_text(
        message_id = call.message.message_id, 
        chat_id = call.message.chat.id,
        text = 'Транспорт для остановки ' + Stops_from_chat[call.from_user.id].chosen_stop, 
        reply_markup = Stops_from_chat[call.from_user.id].busses  
        )

    if call.data == 'back_to_stops':
        bot.edit_message_text(
        message_id = call.message.message_id, 
        chat_id = call.message.chat.id,
        text = 'Наиболее подходящие названия:', 
        reply_markup = Stops_from_chat[call.from_user.id].similar_stops 
        )

    if call.data.split('_')[0] == 'autobus' or call.data.split('_')[0] == 'trolleybus':
        Stops_from_chat[call.from_user.id].directions = kogdabypars.get_directs(call.data.split('_')[0], call.data.split('_')[1])
        Stops_from_chat[call.from_user.id].transport = call.data.split('_')[0]
        Stops_from_chat[call.from_user.id].chosen_bus = call.data.split('_')[1]
        print(call.message.message_id)
        print(call.message.chat.id)
        print(Stops_from_chat[call.from_user.id].directions)
        bot.edit_message_text(
        message_id = call.message.message_id, 
        chat_id = call.message.chat.id,
        text = 'Выберите направление:', 
        reply_markup = Stops_from_chat[call.from_user.id].directions 
        )

    
    if call.data == 'back_to_numbers':
        bot.edit_message_text(
        message_id = call.message.message_id, 
        chat_id = call.message.chat.id,
        text = 'Транспорт для остановки ' + Stops_from_chat[call.from_user.id].chosen_stop, 
        reply_markup = Stops_from_chat[call.from_user.id].busses
        )
    
    
    if call.data.split('_')[0] == 'd':
        Stops_from_chat[call.from_user.id].chosen_direct = call.data.split('_')[1]
        text, keyboard = kogdabypars.get_time_for_day(
            Stops_from_chat[call.from_user.id].transport,
            Stops_from_chat[call.from_user.id].chosen_bus,
            Stops_from_chat[call.from_user.id].chosen_direct,
            Stops_from_chat[call.from_user.id].chosen_stop
        )

        bot.edit_message_text(
        message_id = call.message.message_id, 
        chat_id = call.message.chat.id,
        text = text, 
        reply_markup = keyboard
        )

    if call.data == 'back_to_directs':
        bot.edit_message_text(
        message_id = call.message.message_id, 
        chat_id = call.message.chat.id,
        text = "Выберите направление:", 
        reply_markup = Stops_from_chat[call.from_user.id].directions 
        )


bot.polling(none_stop=True)

