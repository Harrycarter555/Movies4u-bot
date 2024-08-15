import requests
from bs4 import BeautifulSoup

url_list = {}

def search_movies(query):
    """
    Search for movies based on the given query on MKVcinemas.
    Returns a list of dictionaries containing movie IDs and titles.
    """
    movies_list = []
    try:
        search_url = f"https://mkvcinemas.cat/?s={query.replace(' ', '+')}"
        response = requests.get(search_url)
        response.raise_for_status()

        website = BeautifulSoup(response.text, "html.parser")
        movies = website.find_all("a", {'class': 'ml-mask jt'})

        for index, movie in enumerate(movies):
            movie_details = {}
            movie_details["id"] = f"link{index}"
            movie_details["title"] = movie.find("span", {'class': 'mli-info'}).text.strip()
            url_list[movie_details["id"]] = movie['href']
            movies_list.append(movie_details)
    except Exception as e:
        print(f"[ERROR] Exception in search_movies: {e}")
    return movies_list

def get_movie(movie_id):
    """
    Fetch the details of a specific movie based on the given movie ID.
    Returns a dictionary containing the title, image URL, and download/watch links.
    """
    movie_details = {}
    try:
        movie_page_link = BeautifulSoup(requests.get(url_list[movie_id]).text, "html.parser")
        if movie_page_link:
            title = movie_page_link.find("div", {'class': 'mvic-desc'}).h3.text
            movie_details["title"] = title
            img = movie_page_link.find("div", {'class': 'mvic-thumb'})['data-bg']
            movie_details["img"] = img
            final_links = {}

            # Fetching download links
            download_section = movie_page_link.find(text="G-Drive [GDToT] Links:")
            if download_section:
                download_links = download_section.find_next("a")
                while download_links:
                    final_links[f"⚡ Fast Download Links :- {download_links.text.strip()}"] = download_links['href']
                    download_links = download_links.find_next("a")
                    
            # Fetching stream online links
            stream_section = movie_page_link.find(text="Stream Online Links:")
            if stream_section:
                stream_links = stream_section.find_next("a")
                while stream_links:
                    final_links[f"🔴 Watch Online {stream_links.text.strip()}"] = stream_links['href']
                    stream_links = stream_links.find_next("a")

            movie_details["links"] = final_links
    except Exception as e:
        print(f"[ERROR] Exception in get_movie: {e}")
    return movie_details

# Example usage
query = "Stree 2 2024"
movies = search_movies(query)
print("Movies List:", movies)

if movies:
    movie_id = movies[0]["id"]
    movie = get_movie(movie_id)
    print("Movie Details:", movie)
