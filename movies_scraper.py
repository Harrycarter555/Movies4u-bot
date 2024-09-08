import requests
from bs4 import BeautifulSoup

url_list = {}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://mkvcinemas.cat/',
}

def search_movies(query):
    movies_list = []
    try:
        search_url = f"https://mkvcinemas.cat/?s={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=headers)
        website = BeautifulSoup(response.text, "html.parser")
        
        print(f"[DEBUG] Fetching URL: {search_url}")
        movies = website.find_all("a", {'class': 'ml-mask jt'})
        
        for index, movie in enumerate(movies):
            movie_details = {}
            title_span = movie.find("span", {'class': 'mli-info'})
            if title_span:
                movie_details["id"] = f"link{index}"
                movie_details["title"] = title_span.text
                url_list[movie_details["id"]] = movie['href']
                movies_list.append(movie_details)
    except Exception as e:
        print(f"[ERROR] Exception in search_movies: {e}")
    return movies_list

def get_movie(movie_id):
    movie_details = {}
    try:
        if movie_id in url_list:
            movie_url = url_list[movie_id]
            movie_page_link = BeautifulSoup(requests.get(movie_url, headers=headers).text, "html.parser")
            
            final_links = {}
            
            # Fetching specific links with class 'gdlink'
            links = movie_page_link.find_all("a", {'class': 'gdlink'})
            for i in links:
                final_links[f"{i.text}"] = i['href']
            
            # Fetching additional links with class 'button'
            button_links = movie_page_link.find_all("a", {'class': 'button'})
            for i in button_links:
                if "href" in i.attrs and "title" in i.attrs:
                    final_links[f"{i.text} [{i['title']}]"] = i['href']
            
            # Re-add the "Stream Online" link
            stream_section = movie_page_link.find(text="Stream Online Links:")
            if stream_section:
                stream_links = stream_section.find_next("a")
                if stream_links:
                    final_links["🔴 Stream Online"] = stream_links['href']
            
            movie_details["title"] = movie_page_link.find("h1").text if movie_page_link.find("h1") else "Movie"
            movie_details["links"] = final_links
            
            return movie_details  # Return movie details with all the links
        else:
            return "Invalid movie ID!"
    except Exception as e:
        return f"[ERROR] Exception in get_movie: {e}"

# Bot interaction function example:
def handle_movie_search_and_redirect(bot, update):
    query = update.message.text.split(' ', 1)[1]  # Extract search query from user input
    movies = search_movies(query)
    
    if movies:
        # Assuming the first movie result is the one we want to provide links for
        first_movie_id = movies[0]["id"]
        movie_details = get_movie(first_movie_id)
        
        if movie_details and "links" in movie_details:
            # Prepare the message with all download/stream links
            response_message = f"🎬 *{movie_details['title']}* ke download links:\n\n"
            for link_title, link_url in movie_details["links"].items():
                response_message += f"[{link_title}]({link_url})\n"
            
            # Send the download links to the user
            bot.send_message(chat_id=update.message.chat_id, text=response_message, parse_mode='Markdown')
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Maaf karein, movie ke links nahi mile.")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Maaf karein, koi result nahi mila.")
