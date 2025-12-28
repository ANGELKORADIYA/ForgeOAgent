from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Any, Optional, List, Dict
import os
import base64
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

app = FastAPI()


class ContentImageResponse(BaseModel):
    success: bool
    page_source_images_data: Any = None
    gemini_response: Any = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "FastAPI Base64 Image Renderer"}


@app.get("/render-images", response_class=HTMLResponse)
async def render_images():
    api_password = os.getenv("API_PASSWORD")
    headers = {"X-API-Password": api_password}
    result = httpx.post(os.getenv("API_URL"), json={"title": "girnar"}, headers=headers).json()
    print(result)
    return generate_html_with_images(result["page_source_images_data"])

def generate_html_with_images(images_data: Any) -> str:
    """
    Generate HTML content with images (base64 or URL)
    
    Expected image_data format:
    [
        {
            'image_title': 'alt text',
            'source_url': 'https://example.com',
            'is_base64': False,
            'image_data': None or base64_string
        },
        ...
    ]
    """
    if not images_data:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>No Images</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
                .message { background: white; padding: 20px; border-radius: 8px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="message">
                <h2>No images available</h2>
            </div>
        </body>
        </html>
        """
    
    # Start building HTML
    html_parts = ["""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Gallery</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 40px 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            h1 {
                color: white;
                text-align: center;
                margin-bottom: 40px;
                font-size: 2.5rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            
            .gallery {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 30px;
                padding: 20px;
            }
            
            .image-card {
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                cursor: pointer;
            }
            
            .image-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.4);
            }
            
            .image-wrapper {
                width: 100%;
                height: 250px;
                overflow: hidden;
                background: #f0f0f0;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .image-wrapper img {
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.3s ease;
            }
            
            .image-card:hover .image-wrapper img {
                transform: scale(1.1);
            }
            
            .image-info {
                padding: 20px;
            }
            
            .image-title {
                font-size: 1.1rem;
                font-weight: 600;
                color: #333;
                margin-bottom: 10px;
                word-wrap: break-word;
            }
            
            .image-source {
                font-size: 0.85rem;
                color: #666;
                word-break: break-all;
                margin-bottom: 8px;
            }
            
            .badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            
            .badge-base64 {
                background: #667eea;
                color: white;
            }
            
            .badge-url {
                background: #48bb78;
                color: white;
            }
            
            .error-image {
                color: #999;
                font-size: 3rem;
            }
            
            @media (max-width: 768px) {
                h1 { font-size: 2rem; }
                .gallery { grid-template-columns: 1fr; gap: 20px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🖼️ Image Gallery</h1>
            <div class="gallery">
    """]
    
    # Process each image
    if isinstance(images_data, list):
        for idx, img_info in enumerate(images_data):
            if not isinstance(img_info, dict):
                continue
            
            title = img_info.get('image_title', f'Image {idx + 1}')
            source_url = img_info.get('source_url', '')
            is_base64 = img_info.get('is_base64', False)
            image_data = img_info.get('image_data')
            
            # Determine image source
            if is_base64 and image_data:
                # Handle base64 image
                # Check if it already has data URI prefix
                if image_data.startswith('data:'):
                    img_src = image_data
                else:
                    # Assume it's a JPEG if not specified
                    img_src = f"data:image/jpeg;base64,{image_data}"
                badge_class = "badge-base64"
                badge_text = "Base64"
            elif source_url:
                # Use URL
                img_src = source_url
                badge_class = "badge-url"
                badge_text = "URL"
            else:
                # No image available
                img_src = ""
                badge_class = "badge-url"
                badge_text = "No Image"
            
            # Build card HTML
            html_parts.append(f"""
                <div class="image-card">
                    <div class="image-wrapper">
                        {f'<img src="{img_src}" alt="{title}" loading="lazy">' if img_src else '<div class="error-image">🖼️</div>'}
                    </div>
                    <div class="image-info">
                        <div class="image-title">{title}</div>
                        {f'<div class="image-source">🔗 {source_url[:50]}{"..." if len(source_url) > 50 else ""}</div>' if source_url else ''}
                        <span class="badge {badge_class}">{badge_text}</span>
                    </div>
                </div>
            """)
    
    # Close HTML
    html_parts.append("""
            </div>
        </div>
    </body>
    </html>
    """)
    
    return "".join(html_parts)


if __name__ == "__main__":
    import uvicorn
    
    # Check environment variables
    if not os.getenv("API_URL"):
        print("⚠️  Warning: API_URL not set in environment variables")
    if not os.getenv("API_PASSWORD"):
        print("⚠️  Warning: API_PASSWORD not set in environment variables")
    
    print("🚀 Starting FastAPI server...")
    print("📝 Endpoints:")
    print("   GET  /render-images - Fetch and render images from API_URL")
    print("   POST /render-images-from-data - Render images from provided data")
    print("\n🔑 Required header: X-API-Password")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
