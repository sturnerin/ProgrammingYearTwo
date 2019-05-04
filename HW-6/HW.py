from pymystem3 import Mystem
from string import punctuation
import urllib.request
import json
import re
import collections
import requests
import os
import matplotlib.pyplot as plt
from requests.exceptions import HTTPError, Timeout
from datetime import date, datetime

groupid = '-170569428'
count = '100'
token = '46148e1fa80fd093e60b155b66c01fb5a9a2845c070bd904b239f29f52ec15d5b65bf0a68a903f6ed18d4'
offset = 0
lendict = {}
lemlendict = {}
lemposts = ''
justposts = ''

# С моим компьютером что-то случилось после перезагрузки, и он не видит matplotlib, что бы я не делала,
# поэтому не дает запускать скрипт. Загружаю то, на чем проверяла его до. :(

mystem = Mystem() 
with open('stopwords.txt', 'r', encoding='utf-8') as f:
    stopwords = f.read()
    stopwords = stopwords.split('\n')


def makecatalog():
    if not os.path.exists('community/plain/'):
        os.makedirs('community/plain')
        
    if not os.path.exists('community/mystem/'):
        os.makedirs('community/mystem/')
    return

def writefiles(postid, text, lemtext):
    f = open('community/plain/post%d.txt' % (int(postid)), "w", encoding="utf-8")
    f.write(''.join(text))
    f.close()

    f = open('community/mystem/post%d.txt' % (int(postid)), "w", encoding="utf-8")
    f.write(''.join(lemtext))
    f.close()
    return


def getage(birthday):
    today = date.today()
    age = today.year - birthday.year
    if today.month < birthday.month:
        age -= 1
    elif today.month == birthday.month and today.day < birthday.day:
        age -= 1
    return age


def textfrequencies(text, postid, lemposts, justposts, stopwords):
    lemtext = ''
    wordcount = 0
    templist = text.split(' ')
    justposts = justposts + text
    for word in templist:
        wordcount = wordcount + 1
    lendict[postid] = wordcount
    tokens = mystem.lemmatize(text.lower())
    tokens = [token for token in tokens if token not in stopwords\
              and token != " " \
              and token.strip() not in punctuation]
    for token in tokens:
        if token == '\s+':
            tokens.remove(token)
        lemtext = lemtext + ' ' + token
        lemtext = re.sub(r'[^a-z^A-Z^а-я^А-Я]', ' ', lemtext)
        lemtext = re.sub(r'n', '', lemtext)
        lemtext = re.sub(r'\s\s+', ' ', lemtext)
    lemposts = lemposts + lemtext


    num = 0
    length = 0
    for key in lendict.keys():
        num += 1
    for value in lendict.values():
        length += int(value)
    averagelen = length / num
    return averagelen, lemposts, justposts, lemtext


def graphfreq(freq, lemfreq):
    nums = [c[1] for c in sorted(freq.items(), key = lambda x: x[0], reverse=False)]
    labs = sorted([post for post in freq])
    x = range(len(labs))
    plt.title('просто тексты')
    plt.bar(x, nums)
    plt.ylabel('частотность\n',  fontsize=10)
    plt.xlabel('\nслово',  fontsize=10)
    plt.xticks(x, labs, rotation=90)
    plt.show()

    nums = [c[1] for c in sorted(lemfreq.items(), key = lambda x: x[0], reverse=False)]
    labs = sorted([post for post in lemfreq])
    x = range(len(labs))
    plt.title('лемматизированные тексты')
    plt.bar(x, nums)
    plt.ylabel('частотность\n',  fontsize=10)
    plt.xlabel('\nслово',  fontsize=10)
    plt.xticks(x, labs, rotation=90)
    plt.show()
    return


def makestringcsv(status, postid, posterid, firstname, lastname,
                 sex, city, bdate, age, education, text):
    length = len(text)
    string = '%s,%s,%s,%s,%s,%s,%s,%s,%s,"%s",%s,"%s"' % (
        status, postid, posterid, firstname, lastname,
        sex, city, bdate, age, education, length, text)
    return string


def makecsv(string):
    line = 'status,post_id,owner_id,name,surname,sex,city,' \
             'bdate,age,education,length,text,comments_id\n'
    if not os.path.exists('stats.csv'):
        with open('stats.csv', 'w', encoding='utf-8') as f:
            f.write(line)
    with open('stats.csv', 'a', encoding='utf-8') as f:
        f.write(string)
    return


def getposterinfo(posterid, token):
    if int(posterid) < 0:
        firstname, lastname, sex, city, bdate, age, education = '-', '-', '-', '-', '-', '-', '-'
        return firstname, lastname, sex, city, bdate, age, education
    fields = 'city,sex,first_name,last_name,bdate,education'
    try:
        req = urllib.request.Request('https://api.vk.com/method/wall.get?owner_id=%s&count=%s&v=5.92&offset=%s&fields=%s&access_token=%s' % (groupid, count, offset, fields, token)) 
        response = urllib.request.urlopen(req) 
        result = response.read().decode('utf-8')
    except HTTPError or Timeout:
        print('Could not get User Info')
        firstname, lastname, sex, city, bdate, age, education = '-', '-', '-', '-', '-', '-', '-'
        return firstname, lastname, sex, city, bdate, age, education
    else:
        data = json.loads(result)
        try:
            items = data['response'][0]
        except KeyError:
            firstname, lastname, sex, city, bdate, age, education = '-', '-', '-', '-', '-', '-', '-'
            return firstname, lastname, sex, city, bdate, age, education
        else:
            firstname = items['first_name']
            lastname = items['last_name']
            sex = items['sex']
            if sex == 1:
                sex = 'female'
            elif sex == 2:
                sex = 'male'
            else:
                sex = 'unspecified'
            try:
                city = items['city']['title']
            except KeyError:
                city = '-'
            try:
                bdate = items['bdate']
            except KeyError:
                bdate = '-'
                age = '-'
            else:
                try:
                    day, month, year = bdate.split('.')
                except ValueError:
                    age = '-'
                else:
                    time_string = day + '/' + month + '/' + year
                    birthday = datetime.strptime(time_string, '%d/%m/%Y')
                    age = getage(birthday)
            try:
                education = items['university_name']
            except KeyError:
                education = '-'
    return firstname, lastname, sex, city, bdate, age, education


def getcommentinfo(postid, communid, token):
    comments = []
    strings = []
    offset = 0
    while True:
        if offset:
            params = {'access_token': token, 'v': '5.95',
                      'owner_id': communid, 'post_id': postid,
                      'count': 100, 'offset': offset}
        else:
            params = {'access_token': token, 'v': '5.95',
                      'owner_id': communid, 'post_id': postid,
                      'count': 100}
        try:
            req = urllib.request.Request('https://api.vk.com/method/wall.get?owner_id=%s&count=%s&v=5.92&offset=%s&access_token=%s' % (groupid, count, offset, token)) 
            response = urllib.request.urlopen(req) 
            result = response.read().decode('utf-8')
        except HTTPError or Timeout:
            print('something went boom.')
        else:
            status = 'comment'
            data = json.loads(result)
            items = data['response']['items']
            break
            offset += 100
            for item in items:
                try:
                    text = item['text']
                except KeyError:
                    text = '-'
                commentid = str(item['id'])
                try:
                    posterid = str(item['from_id'])
                except KeyError:
                    pass
                else:
                    firstname, lastname, sex, city, bdate, age, education = getposterinfo(posterid, token)
                    comments.append(commentid)
                    string = makestringcsv(status, postid, posterid,
                                          firstname, lastname, sex,
                                          city, bdate, age, education, text)
                    string += ',' + str(commentid) + '\n'
                    strings.append(string)
    return comments, strings


def getposts(groupid, count, lendict, lemposts, justposts, stopwords):
    offset = 0
    alltext = ''
    while True:
        print('posts mined: ', offset)
        try:
            req = urllib.request.Request('https://api.vk.com/method/wall.get?owner_id=%s&count=%s&v=5.92&offset=%s&access_token=%s' % (groupid, count, offset, token)) 
            response = urllib.request.urlopen(req) 
            result = response.read().decode('utf-8')
        except HTTPError or Timeout:
            print('something went boom.')
        else:
            data = json.loads(result)
            items = data['response']['items']
            if not items:
                break
            for item in items:
                postid = str(item['id'])
                communid = str(item['owner_id'])
                text = str(item['text'])
                text = text.replace('\n', '\\n')
                averagelen, lemposts, justposts, lemtext = textfrequencies(text, postid, lemposts, justposts, stopwords)
                writefiles(postid, text, lemtext)
                try:
                    posterid = str(item['signer_id'])
                    print(type(posterid))
                    print(type(token))
                except KeyError:
                    posterid = communid
                if posterid != communid:
                    firstname, lastname, sex, city, bdate, age, education = getposterinfo(posterid, token)
                    status = 'post'
                    comments, strings = getcommentinfo(postid, communid, token)
                    post = makestringcsv(status, postid,
                                        posterid, firstname, lastname,
                                        sex, city, bdate, age, education, text)
                    post += ',' + str(comments) + '\n'
                    makecsv(post)
                    for string in strings:
                        makecsv(string)
            offset += 100
            if offset == 400:
                break
    print(lemposts)
    lempostsplit = lemposts.split(' ')
    for w in lempostsplit:
        if w == ' ':
            lempostsplit.remove(word)
    justpostsplit = justposts.split(' ')
    for w in justpostsplit:
        if w == ' ':
            justpostsplit.remove(word)
    lemfreq = collections.Counter(lempostsplit).most_common(20)
    freq = collections.Counter(justpostsplit).most_common(20)
    freq = dict(freq)
    lemfreq = dict(lemfreq)
    graphfreq(freq, lemfreq)
    print('all clear!')
    return


makecatalog()
getposts(groupid, count, lendict, lemposts, justposts, stopwords)


