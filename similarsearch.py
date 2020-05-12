import sqlite3
import telebot
from telebot import types


conn = sqlite3.connect("stops.db")
cursor = conn.cursor()


cursor.execute('SELECT * FROM Stops')
stops = cursor.fetchall()
stop_names = []


for i in stops:
    stop_names.append(i[0])


def distance(a, b):
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n, m)) space
        a, b = b, a
        n, m = m, n

    current_row = range(n + 1)  # Keep current and previous row, not entire matrix
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]


class Similar:

    def __init__(self):
        self.similar = None

    def get_similar(self, stop_name):
        min_val = 30
        first = ''
        second = ''
        third = ''

        for i in stop_names:
            if distance(i.lower(), stop_name.lower()) <= len(i) / 2:
                if distance(i.lower(), stop_name.lower()) < min_val:
                    min_val = distance(i.lower(), stop_name.lower())
                    third = second
                    second = first
                    first = i

        self.similar = [first, second, third]


        if self.similar != ['','','']:
            keyboard = types.InlineKeyboardMarkup(row_width = 1)
            for i in self.similar:
                if i != '':
                    keyboard.add(types.InlineKeyboardButton(i , callback_data = 'stopfromchat_' + i))
            return keyboard
        else:
            text = 'Ничего не найдено'
            return text


        