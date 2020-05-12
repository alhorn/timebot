from stop import Stop
import json
import sqlite3
import telebot
from telebot import types
from math import radians, cos, sin, asin, sqrt
import operator


def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, (lon1, lat1, lon2, lat2))

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    if km < 1:
        return km
    else:
        return False



conn = sqlite3.connect("stops.db")
cursor = conn.cursor()

cursor.execute('SELECT * FROM Stops')
stops = cursor.fetchall()



class Stops:

    def __init__(self, latitude, longitude):
        self.closest_stops = None
        self.latitude = latitude
        self.longitude = longitude


    def get_stops(self):
        self.closest_stops = []

        for i in stops:
            if haversine(self.latitude, self.longitude, i[1], i[2]) != False:
                self.closest_stops.append(Stop(i[0],round(haversine(self.latitude, self.longitude, i[1], i[2]),2)))
        

        self.closest_stops = sorted(self.closest_stops, key=operator.attrgetter('stop_distance'))

    def close_stops_keyboard(self):
        keyboard = types.InlineKeyboardMarkup(row_width = 1)
        q = 0
        for i in self.closest_stops:
            if q == 3:
                break
            keyboard.add(types.InlineKeyboardButton(i.stop_name + ' ({} км)'.format(i.stop_distance), callback_data = 'stop_' + i.stop_name))
            q +=1
        if len(self.closest_stops) > 3:
            keyboard.add(types.InlineKeyboardButton('Показать все', callback_data = 'see_all'))
        return keyboard

    def all_stops_keyboard(self):
        keyboard = types.InlineKeyboardMarkup(row_width = 1)
        for i in self.closest_stops:
            keyboard.add(types.InlineKeyboardButton(i.stop_name + ' ({} км)'.format(i.stop_distance), callback_data = 'stop_' + i.stop_name))
        return keyboard

