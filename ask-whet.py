from flask import Flask
from flask_ask import Ask, statement, question, session
import json
import requests
import time
import unidecode
import websocket

app = Flask(__name__)
ask = Ask(app, '/ask')


def get_info():
    try:
        conn = websocket.create_connection('ws://localhost:7999/chat/websocket?id=ask-whet', timeout=6)
        answer = ""
        response = conn.recv()
        print(str(response))
        j = json.loads(response)
        if 'status' in j:
            for c in j['status']:
                answer += 'Channel {}... {} percent. '.format( c['c_id'], c['percent'])
            conn.close(reason='done listening')
        return answer
    except Exception as e:
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
    return str(answer)


@app.route('/')
def homepage():
    return get_info() + set_weather()

    


@ask.launch
def start_skill():
    #welcome_message = "Hi, Welcome to Whet!. I am your slave."  #this should be a question
    welcome_message = get_info()
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










if __name__ == '__main__':
    app.run(debug=True)
