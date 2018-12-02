from flask import Flask
from flask import url_for, request, render_template, Response
import json 
import csv
app = Flask(__name__)

keys = ['name','age','motherus','biling','1.1','1.2',
        '1.3','1.4','1.5','1.6','1.1.1','1.1.2','1.1.3',
        '1.1.4','1.1.5','1.1.6','2.1.1','2.2.1','2.3.1',
        'car','stuck1','stuck2']

database = [];

@app.route('/json')
def dump_database():
    json_string = json.dumps(database,ensure_ascii = False, indent=4)
    response = Response(json_string,content_type="application/json; charset=utf-8" )
    return response

@app.route('/stat')
def stat():
    total_age = 0
    total_motherus = 0
    total_biling = 0
    for result in database:
        print(result)
        total_age = total_age + (int(result['age']) if result['age'] != "" else 0)
        total_motherus = total_motherus + (1 if result['motherus'] == 'русский' else 0)
        total_biling = total_biling + (1 if result['biling'] == 'билингв' else 0)
    med_age = float(total_age) / (len(database) if len(database) != 0 else 1)

    return render_template('stat.html', total = len(database), 
    med_age=med_age, total_motherus=total_motherus, total_biling=total_biling)

@app.route('/', methods=['GET', 'POST'])
def indexpost():
    urls = {'главная (с анкетой)': url_for('indexpost'),
            'статистика': url_for('stat'),
            'json': url_for('dump_database'),
            'search': url_for('search')}

    database.append(request.form.to_dict())
    database_to_csv()
    return render_template('index.html', urls=urls)

@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template('search.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    motherus = request.form.to_dict()['motherus']
    text = request.form.to_dict()['word']
    last_search_result = []
    for record in database:
        print(record)
        if record['motherus'] == motherus:
            text_data = ', '.join(['%s:: %s' % (key, value) for (key, value) in record.items()])
            if text_data.find(text):
                last_search_result.append(text_data); 
    return render_template('results.html', motherus=motherus, word=text, results=last_search_result)

def database_to_csv(): 

    with open('database.csv', 'w', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(database)

if __name__ == '__main__':
    app.run(debug=True)
    
