import os
from io import BytesIO
from queue import Queue
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from dotenv import load_dotenv
from movies_scraper import search_movies, get_movie

load_dotenv()

TOKEN = os.getenv("TOKEN")
URL = "https://movies4u-bot.vercel.app"
CHANNEL_INVITE_LINK = "https://t.me/+dUXsdWu9dlk4ZTk9"  # Replace with your actual invitation link
bot = Bot(TOKEN)

def welcome(update, context) -> None:
    user_id = update.message.from_user.id
    if user_in_channel(user_id):
        start_bot_functions(update, context)
    else:
        update.message.reply_text(f"Please join our channel to use this bot: {CHANNEL_INVITE_LINK}")

def start_bot_functions(update, context) -> None:
    update.message.reply_text(f"Hello {update.message.from_user.first_name}, Welcome to Movie dekhee.\n"
                              f"🔥 Download Your Favourite Movies For 💯 Free And 🍿 Enjoy it.")
    update.message.reply_text("👇 Enter Movie Name 👇")

def user_in_channel(user_id):
    url = f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id=@your_channel_id&user_id={user_id}"
    try:
        response = requests.get(url).json()
        if 'ok' in response and response['ok'] and 'result' in response and 'status' in response['result']:
            return response['result']['status'] in ['member', 'administrator', 'creator']
        else:
            return False
    except Exception as e:
        print(f"Error fetching user channel status: {e}")
        return False

def find_movie(update, context):
    user_id = update.message.from_user.id
    if user_in_channel(user_id):
        search_results = update.message.reply_text("Processing...")
        query = update.message.text
        movies_list = search_movies(query)
        if movies_list:
            keyboards = []
            for movie in movies_list:
                keyboard = InlineKeyboardButton(movie["title"], callback_data=movie["id"])
                keyboards.append([keyboard])
            reply_markup = InlineKeyboardMarkup(keyboards)
            search_results.edit_text('Search Results...', reply_markup=reply_markup)
        else:
            search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')
    else:
        update.message.reply_text(f"Please join our channel to use this bot: {CHANNEL_INVITE_LINK}")

def movie_result(update, context) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    if user_in_channel(user_id):
        s = get_movie(query.data)
        response = requests.get(s["img"])
        img = BytesIO(response.content)
        query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
        link = ""
        links = s["links"]
        for i in links:
            link += "🎬" + i + "\n" + links[i] + "\n\n"
        caption = f"⚡ Fast Download Links :-\n\n{link}"
        if len(caption) > 4095:
            for x in range(0, len(caption), 4095):
                query.message.reply_text(text=caption[x:x+4095])
        else:
            query.message.reply_text(text=caption)
    else:
        query.message.reply_text(f"Please join our channel to use this bot: {CHANNEL_INVITE_LINK}")

def setup():
    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue, use_context=True)
    dispatcher.add_handler(CommandHandler('start', welcome))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, find_movie))
    dispatcher.add_handler(CallbackQueryHandler(movie_result))
    return dispatcher

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    update = Update.de_json(request.get_json(force=True), bot)
    setup().process_update(update)
    return 'ok'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "Webhook setup ok"
    else:
        return "Webhook setup failed"

@app.route('/userleft', methods=['POST'])
def user_left_channel():
    update = Update.de_json(request.get_json(force=True), bot)
    user_id = update.message.left_chat_member.id
    if user_id in context.user_data:
        del context.user_data[user_id]
        update.message.reply_text("You have left the channel. Please join the channel to use the bot.")

if __name__ == '__main__':
    app.run(debug=True)
