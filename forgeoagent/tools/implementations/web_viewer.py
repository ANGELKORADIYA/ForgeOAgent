#!/usr/bin/env python3
"""
Web Viewer - Preview Server for AI-Generated HTML

A FastAPI-based preview server that renders HTML content on a local port.
Designed to be used by AI (Gemini) to display modified/generated HTML.

Usage:
    from forgeoagent.mcp.tools.web_viewer import WebViewer
    
    viewer = WebViewer()
    viewer.render(html_content)  # Set HTML to preview
    viewer.start(port=8888)      # Start server
    # Visit http://localhost:8888/preview
"""

import threading
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebViewer:
    """
    Preview server for rendering HTML/CSS/JS content on a local port.
    
    Designed for AI agents to display generated or modified HTML content.
    """
    
    def __init__(self):
        """Initialize the WebViewer."""
        self.current_html: Optional[str] = None
        self.current_title: str = "Web Viewer Preview"
        self._server_thread: Optional[threading.Thread] = None
        self._server_running: bool = False
        self._port: int = 8888
    
    def render(self, html_content: str, title: str = None) -> str:
        """
        Set HTML content to be displayed on the preview server.
        
        Args:
            html_content: The HTML content to render
            title: Optional title for the preview
            
        Returns:
            Preview URL path
        """
        self.current_html = html_content
        if title:
            self.current_title = title
        logger.info(f"📄 HTML content set for preview ({len(html_content)} chars)")
        return f"http://localhost:{self._port}/preview"
    
    def clear(self):
        """Clear the current HTML content."""
        self.current_html = None
        self.current_title = "Web Viewer Preview"
    
    def start(self, port: int = 8888, background: bool = False):
        """
        Start the preview server.
        
        Args:
            port: Port number to run the server on
            background: If True, run in background thread
        """
        self._port = port
        
        if background:
            self._server_thread = threading.Thread(
                target=self._run_server,
                args=(port,),
                daemon=True
            )
            self._server_thread.start()
            logger.info(f"🚀 Preview server started in background on http://localhost:{port}")
            logger.info(f"📄 View content at http://localhost:{port}/preview")
        else:
            self._run_server(port)
    
    def _run_server(self, port: int):
        """Internal method to run the FastAPI server."""
        try:
            from fastapi import FastAPI
            from fastapi.responses import HTMLResponse
            import uvicorn
        except ImportError:
            logger.error("FastAPI/uvicorn not installed. Run: pip install fastapi uvicorn")
            return
        
        app = FastAPI(title="Web Viewer")
        self._server_running = True
        
        @app.get("/", response_class=HTMLResponse)
        async def home():
            has_content = bool(self.current_html)
            return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Web Viewer</title>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ 
                        font-family: 'Segoe UI', system-ui, sans-serif;
                        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #e0e0e0;
                    }}
                    .container {{
                        text-align: center;
                        padding: 40px;
                        background: rgba(255, 255, 255, 0.05);
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                    }}
                    h1 {{ 
                        font-size: 2.5rem;
                        margin-bottom: 20px;
                        background: linear-gradient(90deg, #00d4ff, #7c3aed);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    }}
                    .status {{
                        display: inline-flex;
                        align-items: center;
                        gap: 10px;
                        background: rgba(16, 185, 129, 0.2);
                        padding: 10px 20px;
                        border-radius: 30px;
                        margin-bottom: 20px;
                    }}
                    .info {{ 
                        margin-top: 20px;
                        padding: 20px;
                        background: rgba(0, 0, 0, 0.3);
                        border-radius: 12px;
                    }}
                    code {{ background: rgba(124, 58, 237, 0.3); padding: 4px 10px; border-radius: 6px; }}
                    a {{ color: #00d4ff; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🌐 Web Viewer</h1>
                    <div class="status"><span>Server Running on Port {port}</span></div>
                    <div class="info">
                        <p>Use <code>viewer.render(html)</code> to set content</p>
                        <p style="margin-top: 10px;">Then visit <a href="/preview">/preview</a></p>
                        <p style="margin-top: 15px;">{'✅ Content ready - <a href="/preview">View Preview</a>' if has_content else '⏳ No content set yet'}</p>
                    </div>
                </div>
            </body>
            </html>
            """
        
        @app.get("/preview", response_class=HTMLResponse)
        async def preview():
            if self.current_html:
                return self.current_html
            return "<html><body><h1>No Content</h1><p>Use viewer.render(html) first</p></body></html>"
        
        @app.get("/health")
        async def health():
            return {"status": "ok", "has_content": bool(self.current_html)}
        
        logger.info(f"🚀 Web Viewer starting on http://localhost:{port}")
        
        config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="warning")
        server = uvicorn.Server(config)
        server.run()
    
    def stop(self):
        """Stop the preview server."""
        self._server_running = False


# Global instance for easy access
_viewer_instance: Optional[WebViewer] = None

def get_viewer() -> WebViewer:
    """Get or create a global WebViewer instance."""
    global _viewer_instance
    if _viewer_instance is None:
        _viewer_instance = WebViewer()
    return _viewer_instance

def render(html_content: str) -> str:
    """Quick function to render HTML content."""
    return get_viewer().render(html_content)

def start_viewer(port: int = 8888, background: bool = True):
    """Quick function to start the viewer server."""
    get_viewer().start(port=port, background=background)


if __name__ == "__main__":
    viewer = WebViewer()
    viewer.render("<html><body><h1>Hello Web Viewer!</h1></body></html>")
    viewer.start(port=8888)
