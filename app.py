from flask import Flask, session, render_template, request, redirect
from flask_session import Session 
from os import listdir
from random import shuffle, randrange
import json

def initioal_data():

    with open('data.json') as f:
        dog_races = json.load(f)

    dog_races = add_image_to_data(dog_races)
    return dog_races

def add_image_to_data(dog_races):
    images = listdir(path='static/images')
    for image in images:
        image_name = image.split('.')
        image_name = image_name[0]
        try:
            dog_races[image_name].update({'image' : '/static/images/' + image})
        
        except KeyError as ke:
            pass

        except Exception as e:
            raise e

    for dog in dog_races.keys():
        if not 'image' in dog_races[dog].keys():
            dog_races[dog].update({'image' : '/static/images/image_not_fuond.jpg'})

    return dog_races

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static' 
SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
dog_races = initioal_data()
Session(app)


@app.route('/')
def home():
    if type(session.get('dog_names')) == list:
        return redirect('/game')

    return redirect('/set')

@app.route('/set')
def set_session():
    dog_names = list(dog_races.keys())
    shuffle(dog_names)
    session['dog_names'] = dog_names
    session['score'] = 0
    session['i'] = -1
    if not 'template' in session.keys(): session['template'] = 'game.html'
    if not 'subject' in session.keys(): session['subject'] = ''

    return redirect(f'/subject/{session["subject"]}')
 
@app.route('/clear')
def clear_session():
    if 'template' in session.keys(): template = session['template']  
    else: template = 'game.html'  

    if 'subject' in session.keys(): subject = session['subject']
    else: subject = ''  

    session.clear()
    session['template'] = template  
    session['subject'] = subject  
    return redirect(f'/')


@app.route('/subject/')
@app.route('/subject/<string:subject>')
def change_subject(subject='year'):
    session['subject'] = subject
    if subject == 'image': session['template'] = 'image.html'
    else: session['template'] = 'game.html'
    return redirect('/')

@app.route('/game')
def game():
    check_answ()
    next_answ()
    colect_options()
    answer = session['dog_names'][session['i']]
    template = session['template']
    return render_template(template, answer=answer, options=session['options'], score=session['score'])

def check_answ():
    answ = request.args.get('name')
    if answ == str(colect_answ(session['i'])):
        session['score'] += 1 

def colect_answ(num):
    subject = session['subject']
    dog_name = session['dog_names'][num]
    answ = dog_races[dog_name][subject]
    return answ

def next_answ():
    session['i'] += 1
    if session['i'] >= len(session['dog_names']):
        session['i'] = 0 
        shuffle(session['dog_names'])

def colect_options():
    corect_answ_num = session['i']
    corect_answ = colect_answ(session['i'])

    num_1 = corect_answ_num
    answ_1 = colect_answ(num_1)
    
    num_2 = corect_answ_num
    answ_2 = colect_answ(num_2)
    
    max_range = len(session['dog_names']) -1
    while (answ_1 == corect_answ or
          answ_2 == corect_answ or
          answ_1 == answ_2):
        
        num_1 = randrange(0, max_range)
        num_2 = randrange(0, max_range)
        answ_1 = colect_answ(num_1)
        answ_2 = colect_answ(num_2)

    corect_answ = list_to_string(corect_answ)
    answ_1 = list_to_string(answ_1)
    answ_2 = list_to_string(answ_2)
    session['options'] = [answ_1, answ_2, corect_answ]
    shuffle(session['options'])

def list_to_string(my_object):
    if type(my_object) == list: 
        my_object = ', '.join(my_object)
    
    return my_object

if __name__ == '__main__':
    app.run(debug=True)
