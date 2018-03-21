from flask import Flask
from flask_ask import Ask, statement, question, session
import json
import requests
import time
#import unidecode
import websocket

app = Flask(__name__)
ask = Ask(app, '/ask')


def get_info():
    try:
        conn = websocket.create_connection('ws://localhost:7999/chat/websocket?id=ask-whet', timeout=6)
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

def set_weather(setas="storm"):
    conn = websocket.create_connection('ws://localhost:7999/chat/websocket?id=ask-whet', timeout=6)
    conn.send('{"request": "settings" }')
    answer = str(conn.recv())
    print(answer)
    answer = json.loads(answer)
    answer['settings']['weather'] = setas
    print(str(answer))
    conn.send('{"update":' + json.dumps(answer) + '}')
    conn.close(reason='done listening')

def set_preview(setas=500):
    conn = websocket.create_connection('ws://localhost:7999/chat/websocket?id=ask-whet', timeout=6)
    conn.send('{"request": "light_schedule" }')
    answer = str(conn.recv())
    print(answer)
    answer = json.loads(answer)
    for c in answer['channels']:
        c['preview']['value'] = setas
        c['preview']['active'] = True
    print(str(answer))
    conn.send('{"update":' + json.dumps(answer) + '}')
    conn.close(reason='done listening')


@app.route('/')
def homepage():
    return "ayyyyyyy"

    


@ask.launch
def start_skill():
    welcome_message = "Connected. "  #this should be a question
    #welcome_message = get_info()
    return question(welcome_message)

@ask.intent("AMAZON.YesIntent")
def share_info():
    print("Received YesIntent")
    return statement(get_info())

@ask.intent("AMAZON.NoIntent")
def no_intent():
    return statement("Goodbye.")

@ask.intent("AMAZON.HelpIntent")
def help_intent():
    return statement('Welcome to Costco... I love you.')

@ask.intent("StormIntent")
def storm_intent():
    set_weather(setas="storm")
    return statement("Storms a comming!")

@ask.intent("NoWeatherIntent")
def no_weather_intent():
    set_weather(setas="normal")
    return statement("Ending weather")

@ask.intent('LightAdjustmentIntent', convert={'percent': int})
def weather(percent):
    print(percent)
    pwm = (percent / 100) * 4095
    set_preview(pwm)
    return statement('Setting lights to {}'.format(pwm))










if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
