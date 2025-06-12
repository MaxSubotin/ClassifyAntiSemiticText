import telebot
import numpy as np
import bot_secrets
import logging
import io
import joblib
import re
import nltk

from nltk.corpus import stopwords

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(bot_secrets.TOKEN)

normalizer = joblib.load('bestModel/normalizer.pkl')
vectorizer = joblib.load('bestModel/vectorizer.pkl')
model = joblib.load('bestModel/rf_model.pkl')

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def tokenize_remove_stopwords(text):
    words = text.lower().split()
    filtered_words = [word for word in words if word not in stop_words]
    return filtered_words

def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = ' '.join(text.split())
    return text


def classify_text(input_text, model, vectorizer, normalizer):
    # Clean the text
    input_text = tokenize_remove_stopwords(input_text)
    input_text = " ".join(input_text)
    input_text = clean_text(input_text)

    # Vectorize and normalize the input text
    X = vectorizer.transform([input_text])
    X = normalizer.transform(X)

    # Predict the label
    prediction = model.predict(X)[0]

    # Print the output and return the prediction
    label_str = 'Benign (0)' if prediction == 0 else 'Antisemitic (1)'
    print(f'Input: {input_text}')
    print(f'Predicted Label: {label_str}')
    return prediction

@bot.message_handler(commands=['start'])
def send_requirements(message):
    """Send the explanation and requirements when the user starts."""
    explanation = """
Welcome!
This bot analyzes whether a given text contains antisemitic content.
The underlying model was trained using Reddit posts, combining publicly available labeled data from Kaggle and manually analyzed examples.

📥 Simply send any text, and the bot will respond with a prediction:

Antisemitic (1)

Benign (0)

    """
    bot.reply_to(message, explanation)



@bot.message_handler(content_types=["text"])
def handle_text(message: telebot.types.Message):
    logger.info(f"- received text from {message.chat.username}: {message.text}")
    
    prediction = classify_text(message.text, model, vectorizer, normalizer)

    if prediction == 1:
        response = "Predicted Label: Antisemitic (1)"
    else:
        response = "Predicted Label: Benign (0)"
    
    bot.send_message(message.chat.id, response)



@bot.message_handler(func=lambda x:True)
def handle_photo(message: telebot.types.Message):
    bot.reply_to(message, 'Please uploading a text for instructions write /start')




logger.info("* starting bot")
bot.infinity_polling()
logger.info("* goodbye!")