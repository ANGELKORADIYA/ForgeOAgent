#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Form, Request , status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List , Any
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from io import StringIO
from contextlib import redirect_stdout
import asyncio
from fastapi import BackgroundTasks
import time
import secrets

from forgeoagent.web.services.content_fetcher import ContentImageFetcher, fetch_content_images

# Add the parent directories to sys.path
current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

try:
    from forgeoagent.main import (
        inquirer_using_selected_system_instructions,
        print_available_inquirers,
        print_available_executors,
        auto_import_inquirers,
        GeminiAPIClient,
        create_master_executor,
        save_last_executor
    )
    load_dotenv()
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(title="Prompt Processor API", version="1.0.0")

app.mount("/static", StaticFiles(directory=f"{current_dir}/static"), name="static")

def _delayed_exit(delay: float = 0.5):
        """Sleep for `delay` seconds and then exit the process."""
        import time, os, signal
        time.sleep(delay)
        # try a graceful termination first
        try:
                os.kill(os.getpid(), signal.SIGTERM)
        except Exception:
                try:
                        os._exit(0)
                except Exception:
                        pass
 
@app.get('/exit')
async def exit_server(background_tasks: BackgroundTasks):
        """Endpoint to shutdown the server process. Protected by middleware.
 
        This schedules a background task that will call SIGTERM shortly after
        returning the HTTP response. Use with care.
        """
        background_tasks.add_task(_delayed_exit, 0.5)
        return JSONResponse(content={"status": "shutting_down"})
 
@app.middleware("http")
async def dos_protection(request: Request, call_next):
    """Simple in-memory DoS protection middleware.
 
    Features:
    - Token-bucket rate limiting per client IP (config via env vars)
      * X_RATE_LIMIT_RPM (requests per minute, default 120)
      * X_RATE_LIMIT_BURST (token bucket capacity, default = RPM)
    - Maximum request size check using Content-Length header
      * X_MAX_REQUEST_SIZE (bytes, default 5MB)
 
    Notes:
    - This is an in-process, non-persistent limiter. For production deploys
      behind multiple workers or machines, use a shared store (Redis).
    - We check Content-Length header to avoid buffering large uploads; if
      clients send chunked requests without a Content-Length header they may
      bypass this check.
    """
    # Configuration
    if request.url.path in ["/exit"]:
        response = await call_next(request)
        return response
    try:
        rpm = int(os.getenv("X_RATE_LIMIT_RPM", "120"))
    except ValueError:
        rpm = 120
    try:
        burst = int(os.getenv("X_RATE_LIMIT_BURST", str(rpm)))
    except ValueError:
        burst = rpm
    try:
        max_size = int(os.getenv("X_MAX_REQUEST_SIZE", str(5 * 1024 * 1024)))
    except ValueError:
        max_size = 5 * 1024 * 1024
 
    refill_per_sec = rpm / 60.0
 
    # Initialize store on first run
    if not hasattr(dos_protection, "_store"):
        dos_protection._store = {}
        dos_protection._lock = asyncio.Lock()
 
    client = request.client.host if request.client else "unknown"
    now = time.time()
 
    async with dos_protection._lock:
        entry = dos_protection._store.get(client)
        if not entry:
            entry = {"tokens": float(burst), "last": now}
            dos_protection._store[client] = entry
 
        # refill tokens
        elapsed = now - entry["last"]
        if elapsed > 0:
            entry["tokens"] = min(float(burst), entry["tokens"] + elapsed * refill_per_sec)
            entry["last"] = now
 
        if entry["tokens"] < 1.0:
            # Not enough tokens => rate limit
            retry_after = 1 if refill_per_sec <= 0 else int(max(1, (1.0 - entry["tokens"]) / refill_per_sec))
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Slow down."},
                headers={"Retry-After": str(retry_after)}
            )
 
        # consume a token
        entry["tokens"] -= 1.0
 
    # Quick Content-Length based size check
    cl = request.headers.get("content-length")
    if cl:
        try:
            if int(cl) > max_size:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Payload too large"}
                )
        except ValueError:
            # ignore malformed header
            pass
 
    # Continue to next middleware / endpoint
    response = await call_next(request)
    return response
 
 
@app.middleware("http")
async def verify_api_password(request: Request, call_next):
    """Middleware to verify password for all requests"""
    # Get password from header
    password = request.headers.get("X-API-Password")
    
    # Handle executor mode authentication
    if request.url.path == "/api/process-with-key":
        # Get request body
        try:
            body = await request.json()
            if body.get("mode") != "executor":
                # For executor mode, require password even with API key
                response = await call_next(request)
                return response
        except:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid request body"}
            )
            
    # Allow these paths without password
    if request.url.path in ["/exit","/process-form","/api/prompt-types","/api/agents","/","/health","/api/system-instructions","/favicon.ico","/static/style.css","/static/script.js","/static/logo.png"]:
        response = await call_next(request)
        return response
    # Read configured API password from environment
    api_password = os.getenv("X_API_PASSWORD")
 
    # If server is misconfigured (no password set), return explicit 500
    if not api_password:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Server misconfiguration: X_API_PASSWORD environment variable not set."}
        )
 
    # Validate provided password against configured value
    if not password or not secrets.compare_digest(password, api_password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or missing API password. Include 'X-API-Password' header."}
        )
 
    response = await call_next(request)
    return response

# Initialize templates (optional, for serving HTML form)
templates = Jinja2Templates(directory=f"{current_dir}/templates")


# Auto-import system prompts on startup
try:
    auto_import_inquirers()
except Exception as e:
    print(f"Error importing system prompts: {e}")


# Pydantic models
class PromptRequest(BaseModel):
    prompt_text: str
    prompt_type: str
    context: Optional[str] = None
    mode: str = "inquirer"  # inquirer or executor
    new_content: bool = True
    api_key: Optional[str] = None
    user_system_instruction: Optional[str] = None  # Custom system instruction to append


class SaveAgentRequest(BaseModel):
    agent_name: str


class ProcessResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None

class ContentImageRequest(BaseModel):
    title: str
    description: Optional[str] = None
    convert_to_base64: bool = True
    api_key: Optional[str] = None
    gemini_enabled: bool = False
    max_images_from_page: int = 5


class ContentImageResponse(BaseModel):
    success: bool
    page_source_images_data: Any = None
    gemini_response: Any = None
    browser_images_data: Any = None
    all_images_data: Any = None
    all_images_links: Any = None
    error: Optional[str] = None

@app.post("/api/content-images-with-key", response_model=ContentImageResponse)
async def get_content_images_with_key(request: ContentImageRequest):
    """
    Get content with images using API key authentication.
    Fetches relevant images for a title/description, downloads them, and converts to base64.
    
    Args:
        request: ContentImageRequest containing title, description, and API key
        
    Returns:
        ContentImageResponse 
    """
    
    # Parse API keys - can be comma-separated
    api_keys = (
        [request.api_key] 
        if "," not in request.api_key 
        else [key.strip() for key in request.api_key.split(",") if key.strip()]
    ) if request.api_key else []
    
    if not request.api_key and request.gemini_enabled:
        raise HTTPException(status_code=400, detail="API key is required")
    
    try:
        # Create fetcher instance
        fetcher = ContentImageFetcher(
            gemini_api_keys=api_keys,
        )
        
        # Get content with images
        result = fetcher.fetch_images_for_content(
            content_title=request.title,
            content_description=request.description,
            convert_to_base64=request.convert_to_base64,
            use_gemini_api=request.gemini_enabled,
            max_images_per_source=request.max_images_from_page
        )
        
        return ContentImageResponse(
            success=True,
            page_source_images_data=result.get("images_data") if result.get("extraction_method") == "page_source" else None,
            gemini_response=result.get("gemini_response"),
            browser_images_data=result.get("images_data") if result.get("extraction_method") == "browser" else None,
            all_images_data=result.get("all_images_data"),
            all_images_links=result.get("all_images_links"),
        )
    
    except Exception as e:
        return ContentImageResponse(
            success=False,
            error=str(e),
        )


@app.post("/api/content-images", response_model=ContentImageResponse)
async def get_content_images(request: ContentImageRequest):
    """
    Get content with images using password authentication (via middleware).
    Uses API keys from environment variables.
    
    Args:
        request: ContentImageRequest containing title and description
        
    Returns:
        ContentImageResponse 
    """
    # Get API keys from environment
    api_keys = []
    gemini_keys = os.getenv("GEMINI_API_KEYS")
    if gemini_keys:
        api_keys = [key.strip() for key in gemini_keys.split(",") if key.strip()]
    
    if not api_keys:
        raise HTTPException(status_code=500, detail="No API keys configured")
    
    try:
        # Create fetcher instance
        fetcher = ContentImageFetcher(
            gemini_api_keys=api_keys,
        )
        
        # Get content with images
        result = fetcher.fetch_images_for_content(
            content_title=request.title,
            content_description=request.description,
            convert_to_base64=request.convert_to_base64,
            use_gemini_api=request.gemini_enabled,
            max_images_per_source=request.max_images_from_page
        )
        
        return ContentImageResponse(
            success=True,
            page_source_images_data=result.get("images_data") if result.get("extraction_method") == "page_source" else None,
            gemini_response=result.get("gemini_response"),
            browser_images_data=result.get("images_data") if result.get("extraction_method") == "browser" else None,
            all_images_data=result.get("all_images_data"),
            all_images_links=result.get("all_images_links"),
        )
    
    except Exception as e:
        return ContentImageResponse(
            success=False,
            error=str(e)
        )

# Helper function to capture print output
def capture_print_output(func, *args, **kwargs):
    """Capture print output from a function"""
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        result = func(*args, **kwargs)
        output = captured_output.getvalue()
        return output, result
    except Exception as e:
        output = captured_output.getvalue()
        raise Exception(f"Function error: {str(e)}\nOutput: {output}")
    finally:
        sys.stdout = old_stdout


# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main HTML form"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/prompt-types")
async def get_prompt_types(mode: str = "inquirer"):
    """Get available prompt types based on mode"""
    try:
        if mode == "executor":
            output, _ = capture_print_output(print_available_executors)
            lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
            prompt_types = [line for line in lines if line != "No agents found." and line]
        else:
            output, _ = capture_print_output(print_available_inquirers)
            lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
            prompt_types = []
            for line in lines:
                if "_SYSTEM_INSTRUCTION" in line:
                    clean_type = line.replace("_SYSTEM_INSTRUCTION", "")
                    prompt_types.append(clean_type)
        
        return JSONResponse(content={
            "success": True,
            "prompt_types": prompt_types,
            "count": len(prompt_types)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load prompt types: {str(e)}")

async def process_prompt_common(
    prompt_text: str,
    mode: str,
    prompt_type: str,
    context: Optional[str],
    new_content: bool,
    api_keys: List[str],
    user_system_instruction: Optional[str] = None
) -> str:
    """
    Common prompt processing logic used by both endpoints
    
    Args:
        prompt_text: The prompt text to process
        mode: Processing mode ('inquirer' or 'executor')
        prompt_type: Type of prompt to use
        context: Optional context to include
        new_content: Whether to process as new content
        api_keys: List of API keys to use
        user_system_instruction: Optional custom system instruction to append
    
    Returns:
        Processed result string
    
    Raises:
        HTTPException: If processing fails
    """
    if not api_keys:
        raise HTTPException(status_code=500, detail="No API keys configured")
    
    if not prompt_text.strip():
        raise HTTPException(status_code=400, detail="Prompt text is required")
    
    try:
        # Prepare final text with context if provided
        final_text = prompt_text
        if context:
            final_text = f"{prompt_text}\n<context>{context}</context>"
        
        result = ""
        
        if mode == "executor":
            # executor mode processing
            output, _ = capture_print_output(
                create_master_executor,
                api_keys,
                final_text,
                shell_enabled=True,
                selected_agent={"agent_name": prompt_type} if prompt_type != "None" else None,
                reference_agent_path=prompt_type if prompt_type != "None" else None,
                new_content=new_content,
                # EXTRA : For Executor mode not there
                # user_system_instruction=user_system_instruction
            )
            result = output.strip()
        else:
            # inquirer mode processing
            output, _ = capture_print_output(
                inquirer_using_selected_system_instructions,
                final_text,
                api_keys,
                prompt_type,
                new_content,
                user_system_instruction
            )
            result = output.strip()
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.post("/api/process-with-key", response_model=ProcessResponse)
async def process_prompt_with_key(request: PromptRequest):
    """
    Process a prompt using API key authentication
    No password middleware check applied to this endpoint
    """
    if not request.api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    # Parse API keys - can be comma-separated
    api_keys = (
        [request.api_key] 
        if "," not in request.api_key 
        else [key.strip() for key in request.api_key.split(",") if key.strip()]
    )
    
    try:
        result = await process_prompt_common(
            prompt_text=request.prompt_text,
            mode=request.mode,
            prompt_type=request.prompt_type,
            context=request.context,
            new_content=request.new_content,
            api_keys=api_keys,
            user_system_instruction=request.user_system_instruction
        )
        
        return ProcessResponse(success=True, result=result)
    
    except Exception as e:
        return ProcessResponse(success=False, error=str(e))


@app.post("/api/process", response_model=ProcessResponse)
async def process_prompt(request: PromptRequest):
    """
    Process a prompt using password authentication (via middleware)
    Uses API keys from environment variables
    """
    # Get API keys from environment
    api_keys = []
    gemini_keys = os.getenv("GEMINI_API_KEYS")
    if gemini_keys:
        api_keys = [key.strip() for key in gemini_keys.split(",") if key.strip()]
    
    try:
        result = await process_prompt_common(
            prompt_text=request.prompt_text,
            mode=request.mode,
            prompt_type=request.prompt_type,
            context=request.context,
            new_content=request.new_content,
            api_keys=api_keys,
            user_system_instruction=request.user_system_instruction
        )
        
        return ProcessResponse(success=True, result=result)
    
    except Exception as e:
        return ProcessResponse(success=False, error=str(e))


@app.post("/api/save-agent")
async def save_agent(request: SaveAgentRequest):
    """Save an agent from conversation"""
    try:
        conversation_id = save_last_executor(request.agent_name)
        if not conversation_id:
            raise HTTPException(status_code=404, detail="No conversation found to save")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Agent saved as: {request.agent_name}"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save agent: {str(e)}")


@app.get("/api/agents")
async def list_executors():
    """List all available agents"""
    try:
        output, _ = capture_print_output(print_available_executors)
        lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
        agents = [line for line in lines if line != "No agents found." and line]
        
        return JSONResponse(content={
            "success": True,
            "agents": agents,
            "count": len(agents)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system-instructions")
async def list_system_instructions():
    """List all available system instructions"""
    try:
        output, _ = capture_print_output(print_available_inquirers)
        lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
        instructions = []
        for line in lines:
            if "_SYSTEM_INSTRUCTION" in line:
                clean_type = line.replace("_SYSTEM_INSTRUCTION", "")
                instructions.append(clean_type)
        
        return JSONResponse(content={
            "success": True,
            "system_instructions": instructions,
            "count": len(instructions)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)