import sqlite3
import xml.etree.ElementTree as ET
import os

conn = sqlite3.connect('news.db')


def db_inited():
    cursor = conn.cursor()
    cursor.execute("""SELECT count(*)
                      FROM sqlite_master
                      WHERE type='table'
                      AND name='articles'""")
    return True if cursor.fetchone()[0] == 1 else False


def create_db():
    print("Initializing DB")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE articles
                     ( id INTEGER PRIMARY KEY,
                       au TEXT,
                       ti TEXT,
                       da TEXT,
                       topic TEXT,
                       url   TEXT,
                       content TEXT)""")
    cursor.execute("""CREATE TABLE words
                      (id INTEGER PRIMARY KEY,
                       word TEXT UNIQUE ON CONFLICT IGNORE)""")
    cursor.execute("""CREATE TABLE occurences
                     (article_id INTEGER,
                      word_id INTEGER)""")
    cursor.execute("""CREATE INDEX occ_artl_ind ON occurences (article_id)""")
    cursor.execute("""CREATE INDEX occ_word_ind ON occurences (word_id)""")
    conn.commit()


def files_to_db(rootDir):
    for dirName, subdirList, fileList in os.walk(rootDir):
        print('Found directory: %s' % dirName)
        for fname in fileList:
            with open(os.path.join(dirName, fname), encoding='utf-8') as plain:
                content = []
                for line in plain:
                    if '@au' in line:
                        au = line.rstrip('\n').replace('@au ', '')
                    elif '@ti' in line:
                        ti = line.rstrip('\n').replace('@ti ', '')
                    elif '@da' in line:
                        da = line.rstrip('\n').replace('@da ', '')
                    elif '@topic' in line:
                        topic = line.rstrip('\n').replace('@topic ', '')
                    elif '@url' in line:
                        url = line.rstrip('\n').replace('@url ', '')
                    else:
                        content.append(line)

            cursor = conn.cursor()
            cursor.execute("""INSERT INTO articles (au,ti,da,topic,url,content)
                              VALUES (?,?,?,?,?,?)""",
                           (au, ti, da, topic, url, "".join(content)))
            article_id = cursor.lastrowid

            mystemDirName = dirName.replace('plain', 'mystem-xml')
            fullName = os.path.join(mystemDirName, fname)
            fullName = os.path.abspath(fullName)
            fullName = fullName.replace('txt', 'xml')

            with open(fullName, encoding='utf-8') as inf:
                data = inf.read()
            root = ET.fromstring(data)
            for elem in root.findall('.//ana'):
                word = elem.attrib['lex']
                cursor.execute(
                    """INSERT INTO words (word) VALUES (?)""", (word,))
                cursor.execute(
                    """SELECT id FROM words id WHERE word=?""", (word,))
                word_id = cursor.fetchone()[0]
                cursor.execute(
                    """INSERT INTO occurences VALUES (?,?)""",
                    (article_id, word_id))
    conn.commit()


if __name__ == '__main__':
    print("Hello")
    if not db_inited():
        create_db()
        files_to_db('./newspaper/plain/2018')
