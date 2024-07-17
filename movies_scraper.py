import requests
from bs4 import BeautifulSoup

url_list = {}
api_key = "d15e1e3029f8e793ad6d02cf3343365ac15ad144"

def search_movies(query):
    movies_list = []
    movies_details = {}
    try:
        website = BeautifulSoup(requests.get(f"https://mkvcinemas.bet/?s={query.replace(' ', '+')}").text, "html.parser")
        movies = website.find_all("a", {'class': 'ml-mask jt'})
        for movie in movies:
            if movie:
                movies_details["id"] = f"link{movies.index(movie)}"
                movies_details["title"] = movie.find("span", {'class': 'mli-info'}).text
                url_list[movies_details["id"]] = movie['href']
                movies_list.append(movies_details)
                movies_details = {}  # Reset after appending
    except Exception as e:
        print(f"[ERROR] Exception in search_movies: {e}")
    return movies_list

def get_movie(query):
    movie_details = {}
    try:
        movie_page_link = BeautifulSoup(requests.get(f"{url_list[query]}").text, "html.parser")
        if movie_page_link:
            title = movie_page_link.find("div", {'class': 'mvic-desc'}).h3.text
            movie_details["title"] = title
            img = movie_page_link.find("div", {'class': 'mvic-thumb'})['data-bg']
            movie_details["img"] = img
            links = movie_page_link.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'})
            final_links = {}
            for i in links:
                link_text = i.text.lower()
                url = f"https://publicearn.com/api?api={api_key}&url={i['href']}"
                response = requests.get(url)
                link = response.json()
                if 'watch online' in link_text:
                    final_links[f"🔴 Watch Online"] = link['shortenedUrl']
                else:
                    final_links[f"{i.text}"] = link['shortenedUrl']
            movie_details["links"] = final_links
    except Exception as e:
        print(f"[ERROR] Exception in get_movie: {e}")
    return movie_details
