import requests
from bs4 import BeautifulSoup

# Global dictionary to store movie URLs
url_list = {}
# Replace with your actual API key for URL shortening
api_key = "d15e1e3029f8e793ad6d02cf3343365ac15ad144"

def search_movies(query):
    """
    Search for movies based on the given query.
    Returns a list of dictionaries containing movie IDs and titles.
    """
    movies_list = []
    try:
        # Make a request to the search page and parse it
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
    """
    Get movie details including download and streaming links for the given movie ID.
    Returns a dictionary containing movie title, image URL, and links.
    """
    movie_details = {}
    try:
        # Fetch the movie page content
        movie_page_link = BeautifulSoup(requests.get(url_list[movie_id]).text, "html.parser")
        
        # Debug: Print the HTML content of the movie page
        print(movie_page_link.prettify())

        if movie_page_link:
            # Extract movie title
            title = movie_page_link.find("div", {'class': 'mvic-desc'}).h3.text
            movie_details["title"] = title
            
            # Extract image URL
            img = movie_page_link.find("div", {'class': 'mvic-thumb'})['data-bg']
            movie_details["img"] = img
            
            final_links = []

            # Fetch GDToT links
            gd_link_section = movie_page_link.find("span", {'class': 'button2'}, text="G-Drive [GDToT] Links:")
            if gd_link_section:
                gd_links_div = gd_link_section.find_next_sibling()
                if gd_links_div:
                    # Debug: Print the HTML content of the GDToT section
                    print(gd_links_div.prettify())
                    
                    links = gd_links_div.find_all("a", {'class': 'gdlink'})
                    for link in links:
                        link_text = link.get('title', 'No title available')
                        download_url = link['href']
                        shortened_url = get_shortened_url(download_url)
                        if shortened_url:
                            link_entry = f"🔗 **{link_text}**\n📥 [Download Here]({shortened_url})"
                            final_links.append(link_entry)

            # Fetch Stream Online links (if available)
            stream_link_section = movie_page_link.find("span", {'class': 'button2'}, text="Stream Online Links:")
            if stream_link_section:
                stream_links_div = stream_link_section.find_next_sibling()
                if stream_links_div:
                    # Debug: Print the HTML content of the Stream Online section
                    print(stream_links_div.prettify())
                    
                    links = stream_links_div.find_all("a", {'class': 'gdlink'})
                    for link in links:
                        link_text = link.get('title', 'No title available')
                        stream_url = link['href']
                        shortened_stream_url = get_shortened_url(stream_url)
                        if shortened_stream_url:
                            stream_entry = f"🔴 **Stream Online**\n▶️ [Watch Here]({shortened_stream_url})"
                            final_links.append(stream_entry)

            movie_details["links"] = "\n\n".join(final_links) if final_links else "No links available."
    except Exception as e:
        print(f"[ERROR] Exception in get_movie: {e}")
    return movie_details

def get_shortened_url(original_url):
    """
    Shortens a given URL using the URL shortening service.
    Returns the shortened URL or None if an error occurs.
    """
    try:
        url = f"https://publicearn.com/api?api={api_key}&url={original_url}"
        response = requests.get(url)
        response_data = response.json()
        if 'shortenedUrl' in response_data:
            return response_data['shortenedUrl']
    except Exception as e:
        print(f"[ERROR] Exception in get_shortened_url: {e}")
    return None

# Example Usage
if __name__ == "__main__":
    # Search for movies
    query = "Hello 2023 Gujarati Movie"
    movies = search_movies(query)
    print("Search Results:")
    for movie in movies:
        print(f"ID: {movie['id']}, Title: {movie['title']}")

    # Get details for the first movie from the search results
    if movies:
        movie_id = movies[0]['id']
        movie_details = get_movie(movie_id)
        print(f"Title: {movie_details['title']}")
        print(f"Image URL: {movie_details['img']}")
        print(f"Links:\n{movie_details['links']}")
