import requests
from dotenv import load_dotenv
import os
load_dotenv()


class Unsplash:
    def __init__(self):
        self.access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    
    def search_unsplash(self, query, per_page=2):
        """Searches for images on Unsplash based on the given query. and returns the images links"""
        url = "https://api.unsplash.com/search/photos"
    
        params = {
            "query": query,
            "per_page": per_page,
            "client_id": self.access_key
        }
    
        response = requests.get(url, params=params)
        data = response.json()
    
        images = []
        for photo in data.get('results', []):
            images.append({
            'url': photo['urls']['regular'],
            'thumbnail': photo['urls']['small'],
            'description': photo.get('description', '')
        })
    
        return images