import requests
import json
from models import *
from googletrans import Translator
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler

sentiment_ai_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment"


def get_sentiment_score(message):
    response = requests.post(sentiment_ai_url, data={input: message})
    sentiment_labels = json.loads(response.text)[0]

    return [label_dict['score'] for label_dict in sentiment_labels if label_dict['label'] == "LABEL_0"][0]


def translate(message):
    translator = Translator()

    return translator.translate(message).text


app = Flask(__name__)


@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    eval = get_sentiment_score(translate(data['input']))

    return str(eval)


@app.route('/parent', methods=['POST'])
def add_parent():
    data = request.json
    save_parent(data['id'])

    return 'Success'


@app.route('/chat', methods=['POST'])
def add_chat():
    data = request.json
    save_chat(data['parent_id'], data['chat_id'])

    return 'Success'


@app.route('/message', methods=['POST'])
def add_message():
    data = request.json
    save_message(data['chat_id'], data['text'], data['sender'], get_sentiment_score(data['text']))

    return 'Success'


scheduler = BackgroundScheduler()
scheduler.add_job(func=run_analysis, trigger="interval", seconds=600)
scheduler.start()


if __name__ == '__main__':
    app.run(debug=True)

