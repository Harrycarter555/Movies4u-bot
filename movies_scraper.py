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
        movie_url = url_list[movie_id]
        response = requests.get(movie_url, headers=headers)
        movie_page_link = BeautifulSoup(response.text, "html.parser")
        
        print(f"[DEBUG] Fetching Movie Page URL: {movie_url}")
        print(f"[DEBUG] Response Text: {response.text[:1000]}")  # Print first 1000 characters for inspection
        
        if movie_page_link:
            title_div = movie_page_link.find("div", {'class': 'mvic-desc'})
            if title_div:
                title = title_div.h3.text.strip()
                movie_details["title"] = title
            img_div = movie_page_link.find("div", {'class': 'mvic-thumb'})
            if img_div and img_div.img:
                movie_details["img"] = img_div.img['src']
            
            final_links = {}
            
            # Fetching download links
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
    except Exception as e:
        print(f"[ERROR] Exception in get_movie: {e}")
    return movie_details

# Example usage
query = "Yeh Kaali Kaali Ankhein"
movies = search_movies(query)
print("Movies List:", movies)

if movies:
    movie_id = movies[0]["id"]
    movie = get_movie(movie_id)
    print("Movie Details:", movie)
