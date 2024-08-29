import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from dotenv import load_dotenv
from io import BytesIO
import logging
from movies_scraper import search_movies, get_movie  # Ensure movies_scraper.py is included in the deployment package

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = "-1002170013697"  # Replace with your actual private channel ID
CHANNEL_INVITE_LINK = "https://t.me/+dUXsdWu9dlk4ZTk9"  # Replace with your actual invitation link
bot = Bot(TOKEN)

# Dummy storage for demonstration (replace with actual persistent storage solution)
user_membership_status = {}

def welcome(update: Update, context) -> None:
    user_id = update.message.from_user.id
    logging.debug(f"User ID: {user_id}")
    if user_in_channel(user_id):
        user_membership_status[user_id] = True
        logging.debug(f"User {user_id} joined the channel and is now verified.")
        start_bot_functions(update, context)
    else:
        user_membership_status[user_id] = False
        logging.debug(f"User {user_id} did not join the channel.")
        update.message.reply_text(f"Please join our channel to use this bot: {CHANNEL_INVITE_LINK}")

def user_in_channel(user_id):
    url = f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}"
    logging.debug(f"Checking membership status for user {user_id} with URL: {url}")
    try:
        response = requests.get(url).json()
        logging.debug(f"Response from Telegram API: {response}")
        if response.get('ok') and 'result' in response:
            status = response['result']['status']
            logging.debug(f"User {user_id} status in channel: {status}")
            return status in ['member', 'administrator', 'creator']
        else:
            logging.error("Invalid response structure or 'ok' field is False.")
            return False
    except Exception as e:
        logging.error(f"Exception while checking user channel status: {e}")
        return False

def start_bot_functions(update: Update, context) -> None:
    update.message.reply_text(f"Hello {update.message.from_user.first_name}, Welcome to Movie dekhee.\n"
                              f"🔥 Download Your Favourite Movies For 💯 Free And 🍿 Enjoy it.")
    update.message.reply_text("👇 Enter Movie Name 👇 and link ko Chrome me hi open kare wrna Download link nhi milenga okay ")

def find_movie(update: Update, context) -> None:
    search_results = update.message.reply_text("Processing...")
    query = update.message.text
    movies_list = search_movies(query)
    logging.debug(f"Movies List: {movies_list}")
    if movies_list:
        keyboards = [[InlineKeyboardButton(movie["title"], callback_data=movie["id"])] for movie in movies_list]
        reply_markup = InlineKeyboardMarkup(keyboards)
        search_results.edit_text('Search Results...', reply_markup=reply_markup)
    else:
        search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')

def get_image_url(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    img_tag = soup.find('img', {'itemprop': 'image'})
    if img_tag and 'src' in img_tag.attrs:
        return img_tag['src']
    return None

def movie_result(update: Update, context) -> None:
    query = update.callback_query
    movie_data = get_movie(query.data)
    
    # Fetch page content from the movie URL
    page_url = movie_data.get('page_url')  # Assuming `page_url` is available in the movie data
    if page_url:
        try:
            response = requests.get(page_url)
            if response.status_code == 200:
                img_url = get_image_url(response.text)
                if img_url:
                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        img = BytesIO(img_response.content)
                        query.message.reply_photo(photo=img, caption=f"🎥 {movie_data['title']}")
                    else:
                        query.message.reply_text(text=f"🎥 {movie_data['title']}")
                else:
                    query.message.reply_text(text=f"🎥 {movie_data['title']}")
            else:
                query.message.reply_text(text=f"🎥 {movie_data['title']}")
        except Exception as e:
            logging.error(f"Exception while fetching image: {e}")
            query.message.reply_text(text=f"🎥 {movie_data['title']}")
    else:
        query.message.reply_text(text=f"🎥 {movie_data['title']}")

    # Prepare and send the download links
    link = ""
    links = movie_data.get("links", {})
    for i in links:
        link += f"🎬 {i}\n{links[i]}\n\n"
    caption = f"⚡ Fast Download Links :-\n\n{link}"
    
    if len(caption) > 4095:
        for x in range(0, len(caption), 4095):
            query.message.reply_text(text=caption[x:x+4095])
    else:
        query.message.reply_text(text=caption)

def setup_dispatcher():
    dispatcher = Dispatcher(bot, None, use_context=True)
    dispatcher.add_handler(CommandHandler('start', welcome))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, find_movie))
    dispatcher.add_handler(CallbackQueryHandler(movie_result))  # Handler for movie details
    return dispatcher

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    update = Update.de_json(request.get_json(force=True), bot)
    setup_dispatcher().process_update(update)
    return 'ok'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook(f'https://movies4u-bot.vercel.app/{TOKEN}')
    return "Webhook setup ok" if s else "Webhook setup failed"

if __name__ == '__main__':
    app.run(debug=True)
