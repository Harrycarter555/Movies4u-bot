import os
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from dotenv import load_dotenv
from io import BytesIO
import threading

# Import functions from your movie scraper
from movies_scraper import search_movies, get_movie

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = "-1002170013697"  # Replace with your actual private channel ID
CHANNEL_INVITE_LINK = "https://t.me/+dUXsdWu9dlk4ZTk9"  # Replace with your actual invitation link
bot = Bot(TOKEN)

app = Flask(__name__)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all types of log messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def welcome(update: Update, context) -> None:
    user_id = update.message.from_user.id
    logger.info(f"User {user_id} started the bot.")
    
    if user_in_channel(user_id):
        context.user_data['is_member'] = True
        start_bot_functions(update, context)
    else:
        context.user_data['is_member'] = False
        update.message.reply_text(f"Please join our channel to use this bot: {CHANNEL_INVITE_LINK}")

def user_in_channel(user_id):
    url = f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}"
    try:
        response = requests.get(url, timeout=10).json()
        if response.get('ok') and 'result' in response:
            status = response['result']['status']
            logger.debug(f"User {user_id} status in channel: {status}")
            return status in ['member', 'administrator', 'creator']
        else:
            logger.warning(f"Failed to verify user {user_id} status in channel. Response: {response}")
            return False
    except requests.RequestException as e:
        logger.error(f"Exception while checking user channel status for user {user_id}: {e}")
        return False

def start_bot_functions(update: Update, context) -> None:
    logger.debug(f"Starting bot functions for user {update.message.from_user.id}")
    update.message.reply_text(f"Hello {update.message.from_user.first_name}, Welcome to Movie dekhee.\n"
                              f"🔥 Download Your Favourite Movies For 💯 Free And 🍿 Enjoy it.")
    update.message.reply_text("👇 Enter Movie Name 👇 and link ko Chrome me hi open kare wrna Download link nhi milenga okay ")

def find_movie(update: Update, context) -> None:
    # Start a new thread for handling the movie search
    threading.Thread(target=process_movie_search, args=(update, context)).start()

def process_movie_search(update, context):
    try:
        search_results = update.message.reply_text("Processing...")
        query = update.message.text
        logger.debug(f"Searching for movies with query: {query}")
        
        movies_list = search_movies(query)

        if movies_list:
            keyboards = [[InlineKeyboardButton(movie["title"], callback_data=movie["id"])] for movie in movies_list]
            reply_markup = InlineKeyboardMarkup(keyboards)
            search_results.edit_text('Search Results...', reply_markup=reply_markup)
            logger.info(f"Movies found for query '{query}': {movies_list}")
        else:
            search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')
            logger.info(f"No movies found for query '{query}'")
    except Exception as e:
        logger.error(f"Exception during movie search: {e}")
        update.message.reply_text('An error occurred while processing your request. Please try again later.')

def movie_result(update, context) -> None:
    query = update.callback_query
    logger.debug(f"Fetching movie result for callback data: {query.data}")
    
    try:
        movie_data = get_movie(query.data)

        if movie_data.get('img'):  # Check if the image is available
            try:
                response = requests.get(movie_data["img"], timeout=10)
                img = BytesIO(response.content)
                query.message.reply_photo(photo=img, caption=f"🎥 {movie_data['title']}")
                logger.info(f"Sent photo for movie: {movie_data['title']}")
            except Exception as e:
                logger.error(f"Exception while fetching image for movie: {e}")
                query.message.reply_text(text=f"🎥 {movie_data['title']}")
        else:
            query.message.reply_text(text=f"🎥 {movie_data['title']}")

        links = "\n\n".join([f"🎬 {name}\n{url}" for name, url in movie_data["links"].items()])
        caption = f"⚡ Fast Download Links :-\n\n{links}"

        if len(caption) > 4095:
            for x in range(0, len(caption), 4095):
                query.message.reply_text(text=caption[x:x+4095])
                logger.debug(f"Sent message chunk: {caption[x:x+4095]}")
        else:
            query.message.reply_text(text=caption)
            logger.debug(f"Sent message: {caption}")
    except Exception as e:
        logger.error(f"Exception while fetching movie details: {e}")
        query.message.reply_text('An error occurred while fetching movie details. Please try again later.')

def setup_dispatcher():
    dispatcher = Dispatcher(bot, None, use_context=True)
    dispatcher.add_handler(CommandHandler('start', welcome))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, find_movie))
    dispatcher.add_handler(CallbackQueryHandler(movie_result))  # Handler for movie details
    return dispatcher

@app.route('/')
def index():
    logger.debug("Index route called")
    return 'Hello World!'

@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    update = Update.de_json(request.get_json(force=True), bot)
    logger.info("Received update from Telegram")
    setup_dispatcher().process_update(update)
    return 'ok'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook(f'https://movies4u-bot.vercel.app/{TOKEN}')
    logger.info("Webhook set up successfully" if s else "Webhook setup failed")
    return "Webhook setup ok" if s else "Webhook setup failed"

if __name__ == '__main__':
    app.run(threaded=True)  # Enable threaded mode to handle multiple requests
