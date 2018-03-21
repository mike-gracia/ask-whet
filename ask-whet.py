from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import json
import requests
import time
#import unidecode
import websocket

app = Flask(__name__)
ask = Ask(app, '/ask')
url = 'ws://localhost:7999/chat/websocket?id=ask-whet'


def get_info():
    try:
        conn = websocket.create_connection(url, timeout=6)
        answer = ""
        while len(answer) == 0:
            response = conn.recv()
            print(str(response))
            j = json.loads(response)
            if 'status' in j:
                for c in j['status']:
                    answer += 'Channel {}... {} percent. '.format( c['alias'], c['percent'])
                conn.close(reason='done listening')

        return answer
    except Exception as e:
        print(e)
        return e

def set_runmode(setas="normal"):
    conn = websocket.create_connection(url, timeout=6)
    conn.send('{"request": "settings" }')
    answer = str(conn.recv())
    print(answer)
    answer = json.loads(answer)
    answer['settings']['weather'] = setas
    print(str(answer))
    conn.close(reason='done listening')
    conn = websocket.create_connection(url, timeout=6)
    conn.send('{"update":' + json.dumps(answer) + '}')
    conn.close(reason='done listening')

def set_preview(setas=500, isOn=False):
    conn = websocket.create_connection(url, timeout=6)
    conn.send('{"request": "light_schedule" }')
    answer = str(conn.recv())
    answer = json.loads(answer)
    for c in answer['channels']:
        c['preview']['value'] = setas
        c['preview']['active'] = isOn
    update = answer
    conn.close(reason='done listening')
    conn = websocket.create_connection(url, timeout=6)
    #conn.send('{"update":' + json.dumps(answer) + '}')
    conn.send('{"update":' + json.dumps(update) + '}')
    conn.close(reason='done listening')


@app.route('/')
def homepage():
    return "ayyyyyyy"

    


@ask.launch
def start_skill():
    welcome_message = "Connected. "  #this should be a question
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
def no_weather_intent():
    set_runmode(setas="normal")
    return statement("Ending weather")

@ask.intent('LightAdjustmentIntent', convert={'percent': int})
def light_adjustment_intent(percent):
    pwm = int((percent / 100) * 4095)
    set_preview(setas=pwm, isOn=True)
    return statement('Setting lights to {}'.format(pwm))

@ask.intent("AMAZON.StopIntent")
def normal_runmode_intent():
    set_preview(isOn=False)
    time.sleep(1)
    set_runmode(setas='normal')
    return statement("Returning to normal run schedule.")











if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
