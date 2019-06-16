from pymystem3 import Mystem
import re
import random
import telebot
#from telebot import apihelper

TOKEN = '877576601:AAG-krzg_06t4wD9GfOpMFhRQWZ2LD0qhms'

#telebot.apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hi! Я Нил Гейман. А может, нет. Проверим?")

m = Mystem()
with open('books.txt', 'r', encoding='utf-8') as f:
    text = f.read()

score = 0

#keyboard = types.ReplyKeyboardMarkup(row_width=2)
#btn1 = types.KeyboardButton('да')
#btn2 = types.KeyboardButton('нет')
#keyboard.add(btn1, btn2)

tb.send_message(chat_id, "Начнем? Напиши 'да' или 'нет', иначе я не пойму.", reply_markup=keyboard)
@bot.message_handler(content_types=["text"])
def handle_text(message):
    while message.text == 'да':
        bot.send_message(message.from_user.id, "Начинаем!")
        score = game(text, score)
        tb.send_message(chat_id, 'Еще раз?', reply_markup=keyboard)
    while message.text != 'да' and message.text != 'нет':
        bot.send_message(message.from_user.id, "Прости, не понимаю.")
    if (message.text == 'нет'):
        bot.send_message(message.from_user.id, "Ну и ладно, до встречи когда-нибудь в следующий раз. Твой результат - " + str(score))


def game(text, score):
    sentences = re.split("[.!?\n]", text)
    sent = ''
    while sent == '' or len(sent) < 20:
        sent = random.choice(sentences)

    cleaned = re.sub(r'\W[\s]', ' ', sent)
    splitwords = cleaned.split()
    cleaned = ''
    for word in splitwords:
        if len(word)<4:
            word = ''
        cleaned = cleaned + ' ' + word
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\+?n', '', cleaned)
    cleaned = re.sub(r'[«»]', '', cleaned)

    anachoice = m.analyze(cleaned)
    for entry in anachoice:
        if "'text': ' '" in str(entry) or '\n' in str(entry):
            anachoice.remove(entry)
    lexeme = ''


    while 'S' not in lexeme and 'ADV' not in lexeme and 'V' not in lexeme and 'A=' not in lexeme:
        lexeme = random.choice(anachoice)
        lexeme = str(lexeme)
        if 'гео' in lexeme or 'фам' in lexeme or 'SPRO' in lexeme:
            continue

    entry = re.findall(r"text': '(.*?)'", lexeme)
    entry = str(entry)
    entry = re.sub(r'[\[\]\'\s]', '', entry)
    grammar = re.findall(r"gr': '(.*?)'", lexeme)
    grammar = str(grammar)
    grammar = re.sub(r'[\[\]\']', '', grammar)

    gr = ''
    othersents = ''
    while gr != grammar:
        for i in range(3000):
            othersent = random.choice(sentences)
            othersents = othersents + ' ' + othersent
            i += 1
        analysis = m.analyze(othersents)
        for newentry in analysis:
            if 'analysis' in str(newentry):
                gr = re.findall(r"gr': '(.*?)'", str(newentry))
                gr = str(gr)
                gr = re.sub(r'[\[\]\']', '', gr)
                word = re.findall(r"text': '(.*?)'", str(newentry))
                word = str(word)
                word = re.sub(r'[\[\]\']', '', word)
                if gr == grammar and word.lower() != entry.lower():
                    break



    n = random.random()
    if n > 0.5:
        n = 1
        tb.send_message(chat_id, "Нил Гейман пишет:\n" + sent.replace(entry, word) + '.' + ' Правда?', reply_markup=keyboard)
    else:
        n = 0
        tb.send_message(chat_id, "Нил Гейман пишет:\n" + sent + '.' + ' Правда?', reply_markup=keyboard)

    def handle_answer(message):
        if n == 1 and message.text == 'да' or n == 0 and message.text == 'нет':
            bot.send_message(message.from_user.id, "Да! Ура!")
            score += 1
        elif message.text == 'дельфины':
            score += 5
            bot.send_message(message.from_user.id, "Ты нашел или нашла пасхалку! Пять баллов факультету!")
        else:
            bot.send_message(message.from_user.id, "А вот и нет!")
        

if __name__ == '__main__':
    bot.polling(none_stop=True)
