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
from urllib.parse import quote
import logging
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
  
    def extract_images_from_page_source(self, search_query: str, max_images: int = 10, start_percentage: float = 30.0) -> List[Dict]:
        """
        Fetch page source from Google Images and extract image data with source information.
        
        Returns:
            List of dictionaries containing:
            - image_data: base64 encoded image or image URL
            - image_title: title of the image from Google search
            - source_url: webpage link where the image is from
            - is_base64: boolean indicating if image_data is base64 or URL
        """
        try:
            search_url = f"https://www.google.com/search?q={quote(search_query)}&tbm=isch"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            logger.info(f"Fetching page source from: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            page_source = response.text
            logger.info(f"Page source fetched. Total length: {len(page_source)} characters")
            
            # Calculate start position
            start_pos = int(len(page_source) * (start_percentage / 100.0))
            page_section = page_source[start_pos:]
            
            soup = BeautifulSoup(page_section, 'html.parser')
            
            images_data = []
            seen_urls = set()
            
            # Find all anchor tags
            for a_tag in soup.find_all('a', href=True):
                href = a_tag.get('href', '')
                
                # Skip search links
                if href.startswith('/search?'):
                    continue
                
                # Find img tags within this anchor
                img_tags = a_tag.find_all('img', src=True)
                
                for img_tag in img_tags:
                    img_src = img_tag.get('src', '')
                    img_alt = img_tag.get('alt', 'No title available')
                    
                    # Create unique key to avoid duplicates
                    unique_key = f"{href}_{img_src[:50]}"
                    
                    if unique_key not in seen_urls:
                        seen_urls.add(unique_key)
                        
                        image_info = {
                            'image_title': img_alt,
                            'source_url': href,
                            'is_base64': False,
                            'image_data': None
                        }
                        
                        # Check if image src is base64
                        if img_src.startswith('data:'):
                            image_info['image_data'] = img_src
                            image_info['is_base64'] = True
                            logger.info(f"Found base64 image with title: {img_alt[:50]}...")
                        else:
                            # It's a URL, try to convert to base64
                            base64_image = self.fetch_image_as_base64(img_src)
                            if base64_image:
                                image_info['image_data'] = base64_image
                                image_info['is_base64'] = True
                                logger.info(f"Converted URL to base64 for: {img_alt[:50]}...")
                            else:
                                # Keep as URL if conversion fails
                                image_info['image_data'] = img_src
                                image_info['is_base64'] = False
                                logger.warning(f"Failed to convert, keeping URL for: {img_alt[:50]}...")
                        
                        images_data.append(image_info)
                        
                        # Stop if we've reached max_images
                        if len(images_data) >= max_images:
                            break
                
                if len(images_data) >= max_images:
                    break
            
            logger.info(f"Extracted {len(images_data)} images with source information")
            return images_data
            
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
        fetch_from_gemini: bool = False,
        max_images_from_page: int = 10
    ) -> Dict:
        """
        Get images for a specific title with optional description.
        
        Returns:
            Dictionary with title, images, source information, and base64 encoded images
        """
        search_title = f"Title: {title}"
        if description:
            search_title += f"\nDescription: {description}"
        search_title += "\n Give relevant images valid links for this topic from google search "
        page_source_images_data = self.extract_images_from_page_source(
            search_title, 
            max_images=max_images_from_page,
            start_percentage=30.0
        )
        result = {}
        # Store structured data
        result["page_source_images_data"] = page_source_images_data
        
        # Fetch images from page source if requested
        if fetch_from_gemini:
            try:
                gemini_response = self.client.search_content(prompt=search_title,system_instruction=self.system_prompt)
                gemini_response = json.loads(gemini_response.replace("```json","").replace("```",""))
                logger.info(f"Gemini response: {gemini_response}")
                
                # Initialize result
                result_gemini = {
                    "response": gemini_response.get("response", ""),
                    "main_title": gemini_response.get("main_title", ""),
                    "images_links": gemini_response.get("images_links", []),
                }
                
                # Convert remaining Gemini images to base64 if requested
                if convert_to_base64 and result_gemini.get("images_links",[]):
                    result_gemini["images_base64"] = []
                    result_gemini["failed_images"] = []
                    
                    for image_url in result_gemini["images_links"]:
                        base64_image = self.fetch_image_as_base64(image_url)
                        if base64_image:
                            result_gemini["images_base64"].append(base64_image)
                        else:
                            result_gemini["failed_images"].append(image_url)

                result["gemini_response"] = result_gemini
            except Exception as e:
                logger.error(f"Error fetching images from Gemini: {e}")
                result["gemini_response"] = {"error": str(e)}
        
        return result

# Standalone function for quick usage
def test_fetch_content_images(
    title: str,
    description: Optional[str] = None,
    api_keys: Optional[List[str]] = None,
    convert_to_base64: bool = True,
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
        fetch_from_gemini=fetch_from_page_source,
        max_images_from_page=max_images_from_page
    )
    
    return values

if __name__ == "__main__":
    # Example usage
    API_KEYS = ["xx"]
    title = "The Beauty of Nature"
    description = "Exploring the wonders of the natural world through stunning imagery."
    
    result = test_fetch_content_images(
        title=title,
        description=description,
        api_keys=API_KEYS,
        convert_to_base64=True,
        fetch_from_page_source=False,  # Fetches from page source (30% start, up to 10 images)
        max_images_from_page=1
    )
    
    print(json.dumps(result, indent=2))
    print(result.keys())