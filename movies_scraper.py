import requests
from bs4 import BeautifulSoup

url_list = {}

def search_movies(query):
    """
    Search for movies based on the given query on MKVcinemas.
    Returns a list of dictionaries containing movie IDs and titles.
    """
    movies_list = []
    movies_details = {}
    try:
        search_url = f"https://mkvcinemas.skin/?s={query.replace(' ', '+')}"
        print(f"Searching at URL: {search_url}")  # Debug line
        response = requests.get(search_url)
        response.raise_for_status()
        
        website = BeautifulSoup(response.text, "html.parser")
        movies = website.find_all("a", {'class': 'ml-mask jt'})
        
        if not movies:
            print("No movies found.")
        
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
    Get movie details including download links for the given movie ID.
    Returns a dictionary containing movie title, image URL, and links.
    """
    movie_details = {}
    try:
        movie_url = url_list.get(movie_id)
        if not movie_url:
            print(f"Movie URL not found for ID: {movie_id}")
            return movie_details
        
        print(f"Fetching movie details from URL: {movie_url}")  # Debug line
        response = requests.get(movie_url)
        response.raise_for_status()
        
        movie_page_link = BeautifulSoup(response.text, "html.parser")
        
        title_element = movie_page_link.find("div", {'class': 'mvic-desc'}).h3
        img_element = movie_page_link.find("div", {'class': 'mvic-thumb'})
        
        if title_element and img_element:
            movie_details["title"] = title_element.text.strip()
            movie_details["img"] = img_element['data-bg']
            
            # Fetching download links
            final_links = {}
            download_section = movie_page_link.find("span", text="G-Drive [GDToT] Links:")
            if download_section:
                download_links = download_section.find_next_sibling("div").find_all("a", {'class': 'gdlink'})
                for link in download_links:
                    link_text = link.text.strip()
                    final_links[link_text] = link['href']
            
            movie_details["links"] = "\n".join(f"{key}: {value}" for key, value in final_links.items())
        else:
            print("Error: Missing title or image in movie details.")
    
    except Exception as e:
        print(f"[ERROR] Exception in get_movie: {e}")
    
    return movie_details

# Example usage
if __name__ == "__main__":
    # Search for movies
    query = "Hello 2023 Gujarati Movie"
    movies = search_movies(query)
    print("Movies List:", movies)
    
    # Get details for the first movie from the search results
    if movies:
        movie_id = movies[0]["id"]
        movie = get_movie(movie_id)
        print("Movie Details:", movie)
