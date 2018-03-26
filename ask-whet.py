from flask import Flask, render_template
from flask_ask import Ask, statement, question, session, audio
import json
import requests
import time
#import unidecode
import websocket
import logging

app = Flask(__name__)
ask = Ask(app, '/ask')
url = 'ws://localhost:7999/chat/websocket?id=ask-whet'
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


def create_connection():
    try:
        conn = websocket.create_connection(url, timeout=6)
        return conn
    except Exception as e:
        print(e)
        return e


def get_response(conn, keyword):
    i = 0
    while i < 5:
        response = conn.recv()
        j = json.loads(response)
        if keyword in j:
            return j
        else:
            print(j)
            i += 1
    print('error getting response')


def close_connection(conn):
    conn.close(reason='done listening')
    print("Connection closed")


def get_info():
    conn = create_connection()
    response = get_response(conn, 'status')
    speak = "Status..."
    for c in response['status']:
        speak += 'Channel {}... {} percent. '.format(
            c['alias'], c['percent'])

    close_connection(conn)

    return speak


def set_runmode(setas="normal"):
    conn = create_connection()
    conn.send('{"request": "settings" }')
    response = get_response(conn, 'settings')
    response['settings']['runmode'] = setas
    close_connection(conn)                          #TODO unsure why I have to close and reopen this connection to get result
    conn = create_connection()
    conn.send('{"update":' + json.dumps(response) + '}')
    close_connection(conn)


def set_preview(setas=500, isOn=False):
    conn = create_connection()
    conn.send('{"request": "light_schedule" }')
    response = get_response(conn, 'channels')
    for c in response['channels']:
        c['preview']['value'] = setas
        c['preview']['active'] = isOn
    close_connection(conn)
    conn = create_connection()
    conn.send('{"update":' + json.dumps(response) + '}')
    close_connection(conn)


@app.route('/')
def homepage():
    return "ayyyyyyy"


@ask.launch
def start_skill():
    welcome_message = "Connected. "  # this should be a question
    welcome_message = render_template('welcome')
    #welcome_message = get_info()
    return question(welcome_message)


@ask.intent("InfoIntent")
def share_info():
    print("Received Information Request")
    return statement(get_info())


@ask.intent("RunmodeIntent", mapping={'runmode': 'Runmode'})
def runmode_intent(runmode):
    set_runmode(setas=runmode)
    if runmode == 'storm':
        return statement(render_template('storm'))
    else:
        return statement("Aquarium runmode set to " + runmode)


@ask.intent("NoWeatherIntent")
def no_runmode_intent():
    set_runmode(setas="normal")
    return statement("Ending runmode")


@ask.intent('LightAdjustmentIntent', convert={'percent': int})
def light_adjustment_intent(percent):
    pwm = int((percent / 100) * 4095)
    set_preview(setas=pwm, isOn=True)
    return statement('Setting lights to {}'.format(pwm))


@ask.intent("AMAZON.StopIntent")
def normal_runmode_intent():
    set_preview(isOn=False)
    #time.sleep(1)
    set_runmode(setas='normal')
    return statement("Returning to normal run schedule.")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
