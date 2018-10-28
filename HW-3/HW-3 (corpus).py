import os
import re
import xml
import urllib.request
import csv


def makecatalog(m): # make directories for articles written during a particular month
    if not os.path.exists('newspaper/plain/2018/%d/' % m):
        os.makedirs('newspaper/plain/2018/%d' % m)
        
    if not os.path.exists('newspaper/mystem-plain/2018/%d/' % m):
        os.makedirs('newspaper/mystem-plain/2018/%d' % m)
        
    if not os.path.exists('newspaper/mystem-xml/2018/%d/' % m):
        os.makedirs('newspaper/mystem-xml/2018/%d' % m)
    return


def downloadpage(pageurl, text):
    regPostTitleAuthor = re.compile('<div class="field field-name-field-author.*?"><div class="field-item even">.*?</div>', flags=re.DOTALL)
    author = regPostTitleAuthor.findall(text)
    regTag = re.compile('<.*?>', re.DOTALL)
    regSpace = re.compile('\s{2,}', re.DOTALL)
    if author:
        for a in author:
            new_author = []
            clean_a = regSpace.sub("", a)
            clean_a = regTag.sub("", clean_a)
            new_author.append(clean_a) # find the author(s) using re
    else:
        new_author = 'no author'

    regPostTitle = re.compile('<h1 class="title" id="page-title">.*?</h1>', flags=re.DOTALL)
    title = regPostTitle.search(text)
    title = regSpace.sub('', title.group())
    title = regTag.sub('', title) # find the title

    regPostdate = re.compile('<span property="dc:date dc:created".*?>.*?</span>', flags=re.DOTALL)
    date = regPostdate.findall(text)
    new_date = []
    for d in date:
        clean_d = re.sub(' - .*', '', d)
        clean_d = regTag.sub('', clean_d)
        clean_d.replace('&nbsp;', ' ')
        new_date.append(clean_d)
    for d in new_date:
        d = d.split()
        if d[1] == 'января,':
            d[1] = '01'
        if d[1] == 'февраля,':
            d[1] = '02'
        if d[1] == 'марта,':
            d[1] = '03'
        if d[1] == 'апреля,':
            d[1] = '04'
        if d[1] == 'мая,':
            d[1] = '05'
        if d[1] == 'июня,':
            d[1] = '06'
        if d[1] == 'июля,':
            d[1] = '07'
        if d[1] == 'августа,':
            d[1] = '08'
        if d[1] == 'сентября,':
            d[1] = '09'
        if d[1] == 'октября,':
            d[1] = '10'
        if d[1] == 'ноября,':
            d[1] = '11'
        if d[1] == 'декабря,':
            d[1] = '12'
        month = d[1]
        datestring = d[0] + '.' + d[1] + '.' + d[2] # find the date and make it look how it should, then memorize the month and make a string variable

        regPostTopic = re.compile('typeof="skos:Concept" property="rdfs:label skos:prefLabel" datatype="">.*?</a>', flags=re.DOTALL)
        topics = regPostTopic.findall(text)
        newtopics = []
        for to in topics:
            clean_to = re.sub('typeof="skos:Concept" property="rdfs:label skos:prefLabel" datatype="">', '', to)
            clean_to = regTag.sub('', clean_to)
            newtopics.append(clean_to) # find the topics
                
        if new_author == 'no author':
            regPostcontent = re.compile('<div class="field-item even" property="content:encoded">.*?<div class="link-wrapper">', flags=re.DOTALL)
        else:
            regPostcontent = re.compile('<div class="field-item even" property="content:encoded">.*?<div class="field field-name-field-author.*?>', flags=re.DOTALL)
        content = regPostcontent.findall(text)
        new_content = []
        regTag2 = re.compile('<.*?>', re.DOTALL)
        regSpace2 = re.compile('\s{2,}', re.DOTALL)
        for c in content:
            clean_c = regSpace2.sub('', c)
            clean_c = regTag2.sub('', clean_c)
            new_content.append(clean_c) # extract the content

    return new_author, title, datestring, month, newtopics, pageurl, new_content


def makecsv():
    with open('newspaper/metadata.csv', mode='a', encoding="utf-8") as csv_file:
        fieldnames = ['path', 'author', 'sex', 'birthday',
                      'header', 'created', 'sphere', 'genre_fi',
                      'type', 'topic', 'chronotop', 'style',
                      'audience_age', 'audience_level', 'audience_size',
                      'source', 'publication', 'publisher', 'publ_year',
                      'medium', 'country', 'region', 'language']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader() # create a csv with the right header
    return fieldnames


def writefiles(month, i, new_author, title, datestring, newtopics, pageurl, new_content, text):
    new_author, title, datestring, month, newtopics, pageurl, new_content = downloadpage(pageurl, text)
    f = open('newspaper/plain/2018/%d/article%d.txt' % (int(month), i), "w", encoding="utf-8")
    f.write(''.join(new_content))
    f.close() # make a file with raw content for mystem
    os.system('C:\\Users\\user\\Desktop\\mystem.exe -cgid newspaper//plain//2018//%d//article%d.txt newspaper//mystem-plain//2018//%d//article%d.txt'
                        % (int(month), i, int(month), i))
    os.system('C:\\Users\\user\\Desktop\\mystem.exe -cgid --format xml newspaper//plain//2018//%d//article%d.txt newspaper//mystem-xml//2018//%d//article%d.xml'
                        % (int(month), i, int(month), i)) # create files with stemmed text
    with open("newspaper/plain/2018/%d/article%d.txt" % (int(month), i), "r", encoding="utf-8") as f:
        content = f.read()
    with open("newspaper/plain/2018/%d/article%d.txt" % (int(month), i), "w", encoding="utf-8") as f:
        if new_author == 'no author':
            f.write('@au ')
            f.write(new_author)
            f.write('\n')
        else:
            for a in new_author:
                f.write('@au ')
                f.write(a)
                f.write('\n')
        f.write('@ti ')
        f.write(title)
        f.write('\n')
        f.write('@da ')
        f.write(datestring)
        f.write('\n')
        for topic in newtopics: 
            f.write('@topic ')
            f.write(topic)
            f.write('\n')
        f.write('@url ')
        f.write(pageurl)
        f.write('\n')
        f.write(content) # make a file with content and all the needed metadata
    return


def main():
    for m in range(6,11):
        makecatalog(m)
    url = 'http://kbpravda.ru/node/'
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' # masquerade
    fieldnames = makecsv()
    for i in range(21338, 22760): # go to all the pages from http://kbpravda.ru/node/21338 to http://kbpravda.ru/node/22760
        pageurl = url + str(i)
        try:
            page = urllib.request.urlopen(pageurl)
            text = page.read().decode('utf-8') # get html
            new_author, title, datestring, month, newtopics, pageurl, new_content = downloadpage(pageurl, text) # get content and metadata
            writefiles(month, i, new_author, title, datestring, newtopics, pageurl, new_content, text)
            with open('newspaper/metadata.csv', mode='a', encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='\t')
                if new_author == 'no author':
                    writer.writerow({'path': 'newspaper/plain/2018/%d/article%d.txt' % (int(month), i), 'author': new_author,
                                    'sex': '', 'birthday': '',
                                    'header': title,
                                    'created': datestring.replace('@da ', ''),
                                    'sphere': 'публицистика', 'genre_fi': '',
                                    'type': '', 'topic': ' '.join(newtopics),
                                    'chronotop': '', 'style': 'нейтральный',
                                    'audience_age': 'н-возраст',
                                    'audience_level': 'н-уровень',
                                    'audience_size': 'республиканская',
                                    'source': pageurl,
                                    'publication': 'Кабардино-Балкарская правда',
                                    'publisher': '', 'publ_year': '2018',
                                    'medium': 'газета', 'country': 'Россия',
                                    'region': 'респ. Кабардино-Балкария',
                                    'language': 'ru'})
                else:
                    writer.writerow({'path': 'newspaper/plain/2018/%d/article%d.txt' % (int(month), i), 'author': ' '.join(new_author),
                                    'sex': '', 'birthday': '',
                                    'header': title,
                                    'created': datestring.replace('@da ', ''),
                                    'sphere': 'публицистика', 'genre_fi': '',
                                    'type': '', 'topic': ' '.join(newtopics),
                                    'chronotop': '', 'style': 'нейтральный',
                                    'audience_age': 'н-возраст',
                                    'audience_level': 'н-уровень',
                                    'audience_size': 'республиканская',
                                    'source': pageurl,
                                    'publication': 'Кабардино-Балкарская правда',
                                    'publisher': '', 'publ_year': '2018',
                                    'medium': 'газета', 'country': 'Россия',
                                    'region': 'респ. Кабардино-Балкария',
                                    'language': 'ru'}) # for each article write a row in the table
        except:
            print('Probably there is no article on page', pageurl)


main()
