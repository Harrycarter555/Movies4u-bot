import requests
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler

url_list = {}

def search_movies(query):
    movies_list = []
    try:
        website = BeautifulSoup(requests.get(f"https://mkvcinemas.cat/?s={query.replace(' ', '+')}").text, "html.parser")
        movies = website.find_all("a", {'class': 'ml-mask jt'})
        for index, movie in enumerate(movies):
            movie_details = {}
            movie_details["id"] = f"link{index}"
            movie_details["title"] = movie.find("span", {'class': 'mli-info'}).text
            url_list[movie_details["id"]] = movie['href']
            movies_list.append(movie_details)
    except Exception as e:
        print(f"[ERROR] Exception in search_movies: {e}")
    return movies_list

def get_movie(movie_id):
    movie_details = {}
    try:
        movie_page_link = BeautifulSoup(requests.get(url_list[movie_id]).text, "html.parser")
        if movie_page_link:
            title = movie_page_link.find("div", {'class': 'mvic-desc'}).h3.text
            movie_details["title"] = title
            img = movie_page_link.find("div", {'class': 'mvic-thumb'})['data-bg']
            movie_details["img"] = img
            final_links = {}
            
            # Fetching links with class 'gdlink'
            links = movie_page_link.find_all("a", {'class': 'gdlink'})
            for i in links:
                link_text = i.text.lower()
                if 'watch online' in link_text:
                    final_links[f"🔴 Watch Online"] = i['href']
                else:
                    final_links[f"{i.text}"] = i['href']
            
            # Fetching stream online links
            stream_section = movie_page_link.find(text="Stream Online Links:")
            if stream_section:
                stream_links = stream_section.find_next("a")
                if stream_links:
                    final_links["🔴 Stream Online"] = stream_links['href']
            
            movie_details["links"] = final_links
    except Exception as e:
        print(f"[ERROR] Exception in get_movie: {e}")
    return movie_details

# Telegram Bot Setup
REQUEST_KWARGS = {
    'read_timeout': 20,
    'connect_timeout': 20,
}

updater = Updater("YOUR_BOT_TOKEN", request_kwargs=REQUEST_KWARGS)

def start(update, context):
    update.message.reply_text('Send me a movie name to search for.')

def search(update, context):
    query = ' '.join(context.args)
    movies = search_movies(query)
    if movies:
        movie_id = movies[0]["id"]
        movie = get_movie(movie_id)
        if movie:
            update.message.reply_text(f"🎥 {movie['title']}\n🔗 Links: {movie['links']}")
        else:
            update.message.reply_text("Sorry, no details found for this movie.")
    else:
        update.message.reply_text("Sorry, no movies found with that name.")

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('search', search))

updater.start_polling()
updater.idle()
