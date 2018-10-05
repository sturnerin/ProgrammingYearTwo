import json
import urllib.request
import re

def getdata(n):
    with open(n, encoding = 'utf-8') as n:
        usernames = n.read().splitlines() # make a list of usernames
    username = input('Введите имя пользователя: ')
    while username not in usernames:
        username = input('Нет, вы ввели что-то не то, давайте еще раз: ')
    print('Наш пользователь - ', username, end = '')
    print('!\n')
    token = '' # insert your token
    url = 'https://api.github.com/users/{}/repos?access_token={}'.format(username, token)
    response = urllib.request.urlopen(url)
    text = response.read().decode('utf-8')
    data = json.loads(text) # open url and decode the data
    return data, username

def getnames(data):
    print('Названия репозиториев:\n')
    n = 0
    for element in data:
        print(element["name"], end = '') # print names of the repositories
        if element["description"] == None:
            print(', нет описания\n')
        else:
            print(', описание:', element["description"], '\n') # and their descriptions
    return

def getlanguages(data, username):
    langdict = {}
    for element in data:
        lang = element["language"]
        if lang != None:
            if lang not in langdict.keys():
                dictpart = {lang: 1}
                langdict.update(dictpart) # if this language is not in the dictionary, make an entry
            else:
                langdict[lang] += 1 # if it is, continue counting
            langlist = list(langdict.keys())
    print('\nПользователь {} использует языки {}.'.format(username, ', '.join(langlist)))
    for key, value in langdict.items():
        if str(value).endswith('1'):
            print('{} используется в {} репозитории.'.format(key, value))
        else:
            print('{} используется в {} репозиториях.'.format(key, value))
    return

def compete(n):
    with open(n, encoding = 'utf-8') as n:
        usernames = n.read().splitlines()
    competedict = {}
    for un in usernames: 
        token = '' # insert your token
        url = 'https://api.github.com/users/{}/repos?per_page=100&access_token={}'.format(un, token) 
        response = urllib.request.urlopen(url) 
        text = response.read().decode('utf-8') 
        data = json.loads(text) # download the data for every username
        n = 0
        for element in data:
            if element["name"]:
                n += 1 # count the repositories
        namenum = {un: n}
        competedict.update(namenum) # make a username - number of repositories entry
    leadnum = 0
    leader = []
    for num in competedict.values():
        if num > leadnum:
            leadnum = num
    for key, value in competedict.items():
        if value == leadnum:
            leader.append(key) # calculate
    if len(leader) == 1:
        print('\nБольше всего репозиториев ({}) - у пользователя {}.'.format(leadnum, leader))
    else:
        print('\nБольше всего репозиториев ({}) - у пользователей {}.'.format(leadnum, ', '.join(leader)))
    return

def poplang(n):
    with open(n, encoding = 'utf-8') as n:
        usernames = n.read().splitlines()
    poplangdict = {}
    for un in usernames:
        token = '' # insert your token
        url = 'https://api.github.com/users/{}/repos?per_page=100&access_token={}'.format(un, token)
        response = urllib.request.urlopen(url)
        text = response.read().decode('utf-8')
        data = json.loads(text)
        for element in data:
            lang = element["language"]
            if lang not in poplangdict.keys():
                dictpart = {lang: 1}
                poplangdict.update(dictpart) # make a language - number of repositories entry
            else:
                poplangdict[lang] += 1
    leadnum = 0
    for num in poplangdict.values():
        if num > leadnum:
            leadnum = num
    for key, value in poplangdict.items():
        if value == leadnum:
            leader = key # calculate
    print('\nСамый часто используемый язык - {} (количество репозиториев - {}).'.format(leader, leadnum))
    return

def popuser(n):
    with open(n, encoding = 'utf-8') as n:
        usernames = n.read().splitlines()
    foldict = {}
    for un in usernames:
        followers = []
        token = '' # insert your token
        url = 'https://api.github.com/users/{}/followers?per_page=1000&access_token={}'.format(un, token)
        response = urllib.request.urlopen(url)
        text = response.read().decode('utf-8')
        data = json.loads(text) # download the data for every username
        for element in data:
            if element["login"]:
                followers.append(element)
        folnum = len(followers)
        namefol = {un: folnum}
        foldict.update(namefol) # make a username - followers entry
    leadnum = 0
    leader = []
    for num in foldict.values():
        if num > leadnum:
            leadnum = num
    for key, value in foldict.items():
        if value == leadnum:
            leader = key # calculate
    if len(leader) == 1:
        print('\nСамый популярный пользователь - {} (количество подписчиков - {}).'.format(leader, leadnum))
    else:
        print('\nСамые популярные пользователи - {} (количество подписчиков - {}).'.format(leader, leadnum))
    return

def main():
    data, username = getdata('usernames.txt')
    getnames(data)
    getlanguages(data, username)
    compete('usernames.txt')
    poplang('usernames.txt')
    popuser('usernames.txt')
    return

main()
