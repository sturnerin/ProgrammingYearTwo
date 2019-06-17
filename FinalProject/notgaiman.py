from pymystem3 import Mystem
import re
import random
import telebot
#from telebot import apihelper

TOKEN = '877576601:AAG-krzg_06t4wD9GfOpMFhRQWZ2LD0qhms'

#telebot.apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}
bot = telebot.TeleBot(TOKEN)


d = {}
ans = {}
sb = {}


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    global sb
    global ans
    global d
    sb.update({message.chat.id:0})
    d.update({message.chat.id:False})
    bot.send_message(message.chat.id, "Hi! Я Нил Гейман. А может, нет. Проверим?")
    handle_text(message)
m = Mystem()
with open('books.txt', 'r', encoding='utf-8') as f:
    text = f.read()

#keyboard = types.ReplyKeyboardMarkup(row_width=2)
#btn1 = types.KeyboardButton('да')
#btn2 = types.KeyboardButton('нет')
#keyboard.add(btn1, btn2)

@bot.message_handler(commands=["dop"])
def handle_text(message):
    chat_id = message.chat.id
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('/да', '/нет')
    global score
    bot.send_message(chat_id, "Начнем?", reply_markup=markup)

@bot.message_handler(commands=['завершить'])
def go_out(message):
    bot.send_message(message.from_user.id, "Ну и ладно, до встречи когда-нибудь в следующий раз. Твой результат - " + str(sb[message.chat.id]))


@bot.message_handler(commands=['да'])
def ex(message):
    global sb
    global ans
    global d
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('/да', '/нет')
    if (d[message.chat.id] == True):
        if ans[message.chat.id] == 1:
            bot.send_message(message.from_user.id, "Да! Ура!")
            sb.update({message.chat.id:sb[message.chat.id]+1})
        else:
            bot.send_message(message.from_user.id, "А вот и нет!")
        d.update({message.chat.id:False})
        bot.send_message(message.from_user.id, "Еще раз?", reply_markup=markup)
    else:
        game(message, text)


@bot.message_handler(commands=['нет'])
def nope(message):
    global sb
    global ans
    global d
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('/да', '/нет')
    if (d.get(message.chat.id) == True):
        if ans[message.chat.id] == 0:
            bot.send_message(message.from_user.id, "Да! Ура!")
            sb.update({message.chat.id:sb[message.chat.id]+ 1})
        else:
            bot.send_message(message.from_user.id, "А вот и нет!")
        d.update({message.chat.id:False})
        bot.send_message(message.from_user.id, "Еще раз?", reply_markup=markup)
    else:
        go_out(message)

@bot.message_handler(commands=['игра'])
def game(message, text):
    global sb
    global ans
    global d
    d.update({message.chat.id:True})
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
    chat_id = message.from_user.id
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('/да', '/нет')
    if n > 0.5:
        n = 1
        bot.send_message(chat_id, "Нил Гейман пишет:\n" + sent.replace(entry, word) + '.' + ' Есть подвох?', reply_markup=markup)
    else:
        n = 0
        bot.send_message(chat_id, "Нил Гейман пишет:\n" + sent + '.' + ' Есть подвох?', reply_markup=markup)
    ans.update({chat_id:n})

if __name__ == '__main__':
    bot.polling(none_stop=True)
