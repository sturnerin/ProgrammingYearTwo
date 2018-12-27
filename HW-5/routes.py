from flask import Flask, render_template, request
from pymystem3 import Mystem
import sqlite3
import string
import re
from collections import defaultdict

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    search_string = ""
    lemmas = []
    articles = {}
    if request.args:
        search_string = request.args['search']
        search_string = re.sub(r'[^\w\s]', '', search_string)
        search_string = search_string.rstrip()

        m = Mystem()
        print(search_string)

        lemmas = m.lemmatize(search_string)
        lemmas = list(filter(lambda str: not str == ' ',
                             lemmas))

        articles, articles_words = ask_for_words(lemmas)

    return render_template(
        'index.html',
        search_string=' '.join(lemmas),
        articles=articles.values())


def ask_for_words(words):
    articles = {}
    articles_words = defaultdict(list)

    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    print("Asks for words:", words)
    for word in words:
        for row in cursor.execute(
            """SELECT article_id, url, content
               FROM articles, occurences, words WHERE
               articles.id == occurences.article_id AND
               occurences.word_id = words.id AND
               words.word == ?
               GROUP BY articles.id""", (word,)):
            article = {'url': row[1],
                       'content': row[2]}
            articles[row[0]] = article
            articles_words[row[0]].append(word)
    return (articles, articles_words)
