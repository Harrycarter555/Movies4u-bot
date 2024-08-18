import requests
from bs4 import BeautifulSoup

url_list = {}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://movies4u.diy/',
}

def search_movies(query):
    movies_list = []
    try:
        search_url = f"https://movies4u.diy/?s={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=headers)
        website = BeautifulSoup(response.text, "html.parser")
        
        print(f"[DEBUG] Fetching URL: {search_url}")
        print(f"[DEBUG] Response Status Code: {response.status_code}")
        print(f"[DEBUG] Response Text: {response.text[:1000]}")  # Print first 1000 characters for inspection
        
        movie_links = website.find_all("a", href=True, rel="bookmark")
        print(f"[DEBUG] Found Movies: {len(movie_links)}")
        
        for index, movie in enumerate(movie_links):
            movie_details = {}
            if movie:
                movie_details["id"] = f"link{index}"
                movie_details["title"] = movie.text.strip()
                url_list[movie_details["id"]] = movie['href']
                movies_list.append(movie_details)
            else:
                print(f"[DEBUG] No title found for movie {index}")
    except Exception as e:
        print(f"[ERROR] Exception in search_movies: {e}")
    return movies_list

def get_movie(movie_id):
    movie_details = {}
    try:
        movie_url = url_list.get(movie_id)
        if not movie_url:
            raise ValueError(f"No URL found for movie_id: {movie_id}")
        
        response = requests.get(movie_url, headers=headers)
        movie_page_link = BeautifulSoup(response.text, "html.parser")
        
        print(f"[DEBUG] Fetching Movie Page URL: {movie_url}")
        print(f"[DEBUG] Response Status Code: {response.status_code}")
        print(f"[DEBUG] Response Text: {response.text[:1000]}")  # Print first 1000 characters for inspection
        
        if movie_page_link:
            title_div = movie_page_link.find("div", {'class': 'mvic-desc'})
            if title_div and title_div.h3:
                title = title_div.h3.text.strip()
                movie_details["title"] = title
            
            # Extract movie info
            info_p = movie_page_link.find("p")
            if info_p:
                movie_details["info"] = info_p.text.strip()
            else:
                print(f"[DEBUG] No movie info found for movie {movie_id}")
                movie_details["info"] = None

            # Extract storyline
            storyline_p = movie_page_link.find("p", text=lambda t: t and "Yeh Kaali Kaali Ankhein" in t)
            if storyline_p:
                movie_details["storyline"] = storyline_p.text.strip()
            else:
                print(f"[DEBUG] No storyline found for movie {movie_id}")
                movie_details["storyline"] = None
            
            final_links = {}
            
            download_links = movie_page_link.find_all("a", {'class': 'btn'}, rel="nofollow noopener noreferrer", target="_blank")
            print(f"[DEBUG] Found Download Links: {len(download_links)}")
            for link in download_links:
                if "Download Links" in link.text:
                    final_links["Download"] = link['href']
                if "BATCH/ZIP" in link.text:
                    final_links["Batch/Zip"] = link['href']
            
            movie_details["links"] = final_links
        else:
            print(f"[DEBUG] No movie page link found for {movie_id}")
    except ValueError as ve:
        print(f"[ERROR] ValueError in get_movie: {ve}")
    except Exception as e:
        print(f"[ERROR] Exception in get_movie: {e}")
    return movie_details

def movie_result(update, context):
    movie_id = 'link0'  # Adjust based on how you get movie_id
    movie = get_movie(movie_id)
    if movie:
        title = movie.get('title', 'No title available')
        info = movie.get('info', 'No info available')
        storyline = movie.get('storyline', 'No storyline available')
        links = movie.get('links', 'No links available')

        print(f"Title: {title}")
        print(f"Info: {info}")
        print(f"Storyline: {storyline}")
        print(f"Links: {links}")

# Example usage
query = "Yeh Kaali Kaali Ankhein"
movies = search_movies(query)
print("Movies List:", movies)

if movies:
    movie_id = movies[0]["id"]
    movie = get_movie(movie_id)
    print("Movie Details:", movie)
