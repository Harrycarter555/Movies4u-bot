import requests
from bs4 import BeautifulSoup

url_list = {}
api_key = "d15e1e3029f8e793ad6d02cf3343365ac15ad144"

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
            
            # Fetching only links under "G-Drive [GDToT] Links"
            gdrive_section = movie_page_link.find("strong", text="G-Drive [GDToT] Links:")
            if gdrive_section:
                links_section = gdrive_section.find_next("ul")
                if links_section:
                    links = links_section.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'})
                    for i in links:
                        link_text = i.text.lower()
                        url = f"https://publicearn.com/api?api={api_key}&url={i['href']}"
                        response = requests.get(url)
                        link = response.json()
                        if 'shortenedUrl' in link:
                            if 'watch online' in link_text:
                                final_links[f"🔴 Watch Online"] = link['shortenedUrl']
                            else:
                                final_links[f"{i.text}"] = link['shortenedUrl']
            movie_details["links"] = final_links
    except Exception as e:
        print(f"[ERROR] Exception in get_movie: {e}")
    return movie_details

# Example usage
query = "Hello 2023 Gujarati Movie"
movies = search_movies(query)
print("Movies List:", movies)

if movies:
    movie_id = movies[0]["id"]
    movie = get_movie(movie_id)
    print("Movie Details:", movie)
