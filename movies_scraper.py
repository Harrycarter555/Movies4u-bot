import requests
from bs4 import BeautifulSoup

url_list = {}

def search_movies(query):
    movies_list = []
    try:
        search_url = f"https://mkvcinemas.cat/?s={query.replace(' ', '+')}"
        response = requests.get(search_url)
        website = BeautifulSoup(response.text, "html.parser")
        
        print(f"[DEBUG] Fetching URL: {search_url}")
        print(f"[DEBUG] Response Text: {response.text[:1000]}")  # Print first 1000 characters for inspection
        
        movies = website.find_all("a", {'class': 'ml-mask jt'})
        print(f"[DEBUG] Found Movies: {len(movies)}")
        
        for index, movie in enumerate(movies):
            movie_details = {}
            title_span = movie.find("span", {'class': 'mli-info'})
            if title_span:
                movie_details["id"] = f"link{index}"
                movie_details["title"] = title_span.text
                url_list[movie_details["id"]] = movie['href']
                movies_list.append(movie_details)
            else:
                print(f"[DEBUG] No title span found for movie {index}")
    except Exception as e:
        print(f"[ERROR] Exception in search_movies: {e}")
    return movies_list

def get_movie(movie_id):
    movie_details = {}
    try:
        movie_url = url_list[movie_id]
        movie_page_link = BeautifulSoup(requests.get(movie_url).text, "html.parser")
        
        print(f"[DEBUG] Fetching Movie Page URL: {movie_url}")
        print(f"[DEBUG] Response Text: {requests.get(movie_url).text[:1000]}")  # Print first 1000 characters for inspection
        
        if movie_page_link:
            title_div = movie_page_link.find("div", {'class': 'mvic-desc'})
            if title_div:
                title = title_div.h3.text
                movie_details["title"] = title
            img_div = movie_page_link.find("div", {'class': 'mvic-thumb'})
            if img_div and 'data-bg' in img_div.attrs:
                movie_details["img"] = img_div['data-bg']
            
            final_links = {}
            
            # Fetching links with class 'gdlink'
            links = movie_page_link.find_all("a", {'class': 'gdlink'})
            print(f"[DEBUG] Found Links: {len(links)}")
            for i in links:
                final_links[f"{i.text}"] = i['href']
            
            # Fetching stream online links
            stream_section = movie_page_link.find(text="Stream Online Links:")
            if stream_section:
                stream_links = stream_section.find_next("a")
                if stream_links:
                    final_links["🔴 Stream Online"] = stream_links['href']
            
            movie_details["links"] = final_links
        else:
            print(f"[DEBUG] No movie page link found for {movie_id}")
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
