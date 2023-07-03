import requests
import json
from googletrans import Translator

sentiment_ai_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment"


def get_sentiment_ratings(message):
    response = requests.post(sentiment_ai_url, data={input: message})

    return json.loads(response.text)


def translate(message):
    translator = Translator()

    return translator.translate(message).text


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    a = translate('עידו לפידות ילד זבל חבל שנולד, לא היה צריך לקום היום בבוקר')
    print(a)
    print(get_sentiment_ratings(a)[0])
