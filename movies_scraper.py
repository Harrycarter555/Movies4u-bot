import requests
from bs4 import BeautifulSoup

# Dictionary to store movie URLs by ID
url_list = {}

def search_movies(query):
    """
    Search for movies based on the given query on MKVcinemas.
    Returns a list of dictionaries containing movie IDs and titles.
    """
    movies_list = []
    movies_details = {}
    try:
        # Request the search results page and parse it
        response = requests.get(f"https://mkvcinemas.cat/?s={query.replace(' ', '+')}")
        website = BeautifulSoup(response.text, "html.parser")
        
        # Find all movie links on the page
        movies = website.find_all("a", {'class': 'ml-mask jt'})
        
        # Extract movie details and store URLs
        for movie in movies:
            if movie:
                movies_details["id"] = f"link{movies.index(movie)}"
                movies_details["title"] = movie.find("span", {'class': 'mli-info'}).text
                url_list[movies_details["id"]] = movie['href']
                movies_list.append(movies_details)
                movies_details = {}
    except Exception as e:
        print(f"[ERROR] Exception in search_movies: {e}")
    return movies_list

def get_movie(movie_id):
    """
    Get movie details including download links for the given movie ID.
    Returns a dictionary containing movie title, image URL, and links.
    """
    movie_details = {}
    try:
        # Fetch the movie page and parse it
        response = requests.get(url_list[movie_id])
        movie_page_link = BeautifulSoup(response.text, "html.parser")
        
        if movie_page_link:
            # Extract movie title and image
            title = movie_page_link.find("div", {'class': 'mvic-desc'}).h3.text
            movie_details["title"] = title
            
            img = movie_page_link.find("div", {'class': 'mvic-thumb'})['data-bg']
            movie_details["img"] = img
            
            final_links = {}
            
            # Fetching download links
            links = movie_page_link.find_all("a", {'class': 'gdlink'})
            for i in links:
                link_text = i.text
                final_links[f"{link_text}"] = i['href']
            
            # Format the links into a readable string
            movie_details["links"] = "\n".join(f"{key}: {value}" for key, value in final_links.items())
    except Exception as e:
        print(f"[ERROR] Exception in get_movie: {e}")
    return movie_details
