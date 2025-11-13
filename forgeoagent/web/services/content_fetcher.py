#!/usr/bin/env python3
"""
Content Image Fetcher Service

This module provides functionality to fetch content with images using Gemini API,
download images from URLs, and convert them to base64 format.

File: services/content_fetcher.py
"""

import base64
import requests
from typing import List, Dict, Optional
from forgeoagent.clients.gemini_engine import GeminiAPIClient
from google.genai import types
from google import genai
import json
import webbrowser
import time
from urllib.parse import quote
import logging
import re
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentImageFetcher:
    """
    Fetches relevant images for a given title/description using Gemini API,
    downloads the images, converts them to base64, and returns structured data.
    """
    
    def __init__(self, api_keys: List[str]):
        """
        Initialize the ContentImageFetcher.
        
        Args:
            api_keys: List of Gemini API keys
            system_prompt: Custom system prompt (optional)
        """
        self.api_keys = api_keys
        self.system_prompt = "Give relevant topic working images links  and title based on the given description. Output format : {'images_links':[link1,link2],'main_title':relevant_title,'response':relevant_response}"
        
        # Define output schema
        self.output_properties = {
            "response": types.Schema(
                type=genai.types.Type.STRING, 
                description="The agent's response to the given task"
            ),
            "main_title": types.Schema(
                type=genai.types.Type.STRING, 
                description="The main title of the content"
            ),
            "images_links": types.Schema(
                type=genai.types.Type.ARRAY,
                items=types.Schema(type=genai.types.Type.STRING),
                description="List of image links related to the topic"
            )
        }
        self.output_required = ["response", "main_title", "images_links"]
        
        # Initialize Gemini client
        self.client = GeminiAPIClient(
            system_instruction=self.system_prompt,
            api_keys=self.api_keys,
            # output_properties=self.output_properties,
            # output_required=self.output_required
        )
    
    def fetch_image_as_base64(self, image_url: str, timeout: int = 10) -> Optional[str]:
        """
        Download an image from URL and convert it to base64.
        
        Args:
            image_url: URL of the image to download
            timeout: Request timeout in seconds
            
        Returns:
            Base64 encoded string of the image, or None if failed
        """
        try:
            response = requests.get(image_url, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Read image content
            image_content = response.content
            
            # Convert to base64
            base64_encoded = base64.b64encode(image_content).decode('utf-8')
            
            # Get content type for data URI
            content_type = response.headers.get('Content-Type', 'image/jpeg')
            
            # Return as data URI format
            return f"data:{content_type};base64,{base64_encoded}"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching image from {image_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            return None
    
    def launch_browser_and_search_images(self, search_query: str, open_browser: bool = True) -> List[str]:
        """
        Launch browser and search for images using Google Images.
        
        Args:
            search_query: The search query/title to search for images
            open_browser: Whether to open browser for user interaction (default: True)
            
        Returns:
            List of image URLs found (from Gemini API results)
        """
        try:
            # Prepare Google Images search URL
            search_url = f"https://www.google.com/search?q={quote(search_query)}&tbm=isch"
            
            if open_browser:
                logger.info(f"Launching browser for search: {search_query}")
                webbrowser.open(search_url, new=2)  # new=2 opens in new window
                logger.info(f"Browser opened with URL: {search_url}")
            
            return [search_url]
            
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            return []
    
    def extract_images_from_page_source(self, search_query: str, max_images: int = 10, start_percentage: float = 30.0) -> List[str]:
        """
        Fetch page source from Google Images and extract image links (.jpg, .png).
        Starts extraction from 30% of the page content and gets up to 10 images.
        
        Args:
            search_query: The search query to search for images
            max_images: Maximum number of images to extract (default: 10)
            start_percentage: Percentage of page to start extraction from (default: 30.0)
            
        Returns:
            List of extracted image URLs
        """
        try:
            # Prepare Google Images search URL
            search_url = f"https://www.google.com/search?q={quote(search_query)}&tbm=isch"
            
            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            logger.info(f"Fetching page source from: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            page_source = response.text
            logger.info(f"Page source fetched. Total length: {len(page_source)} characters")
            
            # Calculate start position (30% of page)
            start_pos = int(len(page_source) * (start_percentage / 100.0))
            page_section = page_source[start_pos:]
            
            logger.info(f"Starting extraction from position {start_pos} (30% of page)")
            
            # Extract image URLs ending with .jpg or .png using regex
            # Pattern to match URLs with .jpg or .png
            image_pattern = r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png)(?:\?[^\s"\'<>]*)?'
            
            image_urls = re.findall(image_pattern, page_section, re.IGNORECASE)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_images = []
            for url in image_urls:
                if url not in seen:
                    seen.add(url)
                    unique_images.append(url)
                    if len(unique_images) >= max_images:
                        break
            
            logger.info(f"Found {len(unique_images)} unique images from page source")
            return unique_images
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page source: {e}")
            return []
        except Exception as e:
            logger.error(f"Error extracting images from page source: {e}")
            return []
    
  
        
    def get_title_and_images(
        self, 
        title: str, 
        description: Optional[str] = None,
        convert_to_base64: bool = True,
        launch_browser: bool = False,
        fetch_from_page_source: bool = False,
        max_images_from_page: int = 10
    ) -> Dict:
        """
        Get images for a specific title with optional description.
        
        Args:
            title: Main title for content
            description: Additional description (optional)
            convert_to_base64: Whether to convert images to base64
            launch_browser: Whether to launch browser for Google Images search
            fetch_from_page_source: Whether to fetch images from Google Images page source
            max_images_from_page: Maximum images to extract from page source (default: 10)
            
        Returns:
            Dictionary with title, images, and optionally base64 encoded images
        """
        prompt = f"Title: {title}"
        if description:
            prompt += f"\nDescription: {description}"
        prompt += "\n Give relevant images valid links for this topic from google search "
        
        gemini_response = self.client.search_content(prompt=prompt,system_instruction=self.system_prompt)
        gemini_response = json.loads(gemini_response.replace("```json","").replace("```",""))
        logger.info(f"Gemini response: {gemini_response}")
        
        # Initialize result
        result = {
            "response": gemini_response.get("response", ""),
            "main_title": gemini_response.get("main_title", ""),
            "images_links": gemini_response.get("images_links", []),
        }
        
        # Fetch images from page source if requested
        if fetch_from_page_source:
            search_title = result.get("main_title", title)
            logger.info(f"Fetching images from page source for: {search_title}")
            page_source_images = self.extract_images_from_page_source(
                search_title, 
                max_images=max_images_from_page,
                start_percentage=30.0
            )
            result["page_source_images"] = page_source_images
            result["page_source_count"] = len(page_source_images)
            logger.info(f"Extracted {len(page_source_images)} images from page source")
            
            # Optionally merge with Gemini images
            result["images_links"].extend(page_source_images)
            result["images_links"] = list(dict.fromkeys(result["images_links"]))  # Remove duplicates
        
        # Launch browser with main_title search if requested
        if launch_browser:
            search_title = result.get("main_title", title)
            logger.info(f"Launching browser to search for: {search_title}")
            self.launch_browser_and_search_images(search_title, open_browser=True)
            result["browser_search_url"] = f"https://www.google.com/search?q={quote(search_title)}&tbm=isch"
        
        # Convert images to base64 if requested
        if convert_to_base64:
            result["images_base64"] = []
            result["failed_images"] = []
            
            for image_url in result["images_links"]:
                base64_image = self.fetch_image_as_base64(image_url)
                if base64_image:
                    result["images_base64"].append(base64_image)
                else:
                    result["failed_images"].append(image_url)
        
        return result
    

# Standalone function for quick usage
def fetch_content_images(
    title: str,
    description: Optional[str] = None,
    api_keys: Optional[List[str]] = None,
    convert_to_base64: bool = True,
    launch_browser: bool = True,
    fetch_from_page_source: bool = False,
    max_images_from_page: int = 10
) -> Dict:
    """
    Standalone function to fetch and convert images for a given title/description.
    
    Args:
        title: Main title for content
        description: Additional description (optional)
        api_keys: List of Gemini API keys
        convert_to_base64: Whether to convert images to base64
        launch_browser: Whether to launch browser for Google Images search of main_title
        fetch_from_page_source: Whether to fetch images from Google Images page source (30% start, up to 10 images)
        max_images_from_page: Maximum images to extract from page source (default: 10)
        
    Returns:
        Dictionary containing title, images, and optionally base64 encoded images
    """
    if not api_keys:
        raise ValueError("API keys are required")
    
    fetcher = ContentImageFetcher(api_keys=api_keys)
    values = fetcher.get_title_and_images(
        title=title, 
        description=description,
        convert_to_base64=convert_to_base64,
        launch_browser=launch_browser,
        fetch_from_page_source=fetch_from_page_source,
        max_images_from_page=max_images_from_page
    )
    
    return values

if __name__ == "__main__":
    # Example usage
    API_KEYS = ["AIzaSyD3IKFXcKGbh8oX6yWz3zkk41iefTMf5z8"]
    title = "The Beauty of Nature"
    description = "Exploring the wonders of the natural world through stunning imagery."
    
    result = fetch_content_images(
        title=title,
        description=description,
        api_keys=API_KEYS,
        convert_to_base64=True,
        launch_browser=True,
        fetch_from_page_source=True,  # Fetches from page source (30% start, up to 10 images)
        max_images_from_page=10
    )
    
    print(json.dumps(result, indent=2))