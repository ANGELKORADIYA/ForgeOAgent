#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Form, Request , status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
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
        AgentManager,
        create_master_executor
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


class SaveAgentRequest(BaseModel):
    agent_name: str
    conversation_id: Optional[str] = None


class ProcessResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None

class ContentImageRequest(BaseModel):
    title: str
    description: Optional[str] = None
    convert_to_base64: bool = True
    api_key: Optional[str] = None


class ContentImageResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    main_title: Optional[str] = None
    images_links: Optional[List[str]] = None
    images_base64: Optional[List[str]] = None
    failed_images: Optional[List[str]] = None
    error: Optional[str] = None

@app.post("/api/content-images-with-key", response_model=ContentImageResponse)
async def get_content_images_with_key(request: ContentImageRequest):
    """
    Get content with images using API key authentication.
    Fetches relevant images for a title/description, downloads them, and converts to base64.
    
    Args:
        request: ContentImageRequest containing title, description, and API key
        
    Returns:
        ContentImageResponse with title, images links, and base64 images
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
        # Create fetcher instance
        fetcher = ContentImageFetcher(
            api_keys=api_keys,
        )
        
        # Get content with images
        result = fetcher.get_title_and_images(
            title=request.title,
            description=request.description,
            convert_to_base64=request.convert_to_base64
        )
        
        return ContentImageResponse(
            success=True,
            response=result.get("response"),
            main_title=result.get("main_title"),
            images_links=result.get("images_links", []),
            images_base64=result.get("images_base64", []),
            failed_images=result.get("failed_images", [])
        )
    
    except Exception as e:
        return ContentImageResponse(
            success=False,
            error=str(e)    
        )


@app.post("/api/content-images", response_model=ContentImageResponse)
async def get_content_images(request: ContentImageRequest):
    """
    Get content with images using password authentication (via middleware).
    Uses API keys from environment variables.
    
    Args:
        request: ContentImageRequest containing title and description
        
    Returns:
        ContentImageResponse with title, images links, and base64 images
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
            api_keys=api_keys,
        )
        
        # Get content with images
        result = fetcher.get_title_and_images(
            title=request.title,
            description=request.description,
            convert_to_base64=request.convert_to_base64
        )
        
        return ContentImageResponse(
            success=True,
            response=result.get("response"),
            main_title=result.get("main_title"),
            images_links=result.get("images_links", []),
            images_base64=result.get("images_base64", []),
            failed_images=result.get("failed_images", [])
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
    api_keys: List[str]
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
            agent_manager = AgentManager()
            prompt_text_path = None
            
            if prompt_type and prompt_type != "None":
                try:
                    prompt_text_path = agent_manager.get_agent_path(prompt_type)
                except Exception:
                    prompt_text_path = None
            
            output, _ = capture_print_output(
                create_master_executor,
                api_keys,
                final_text,
                shell_enabled=True,
                selected_agent={"agent_name": prompt_type} if prompt_type != "None" else None,
                reference_agent_path=prompt_text_path,
                new_content=new_content
            )
            result = output.strip()
        else:
            # inquirer mode processing
            output, _ = capture_print_output(
                inquirer_using_selected_system_instructions,
                final_text,
                api_keys,
                prompt_type,
                new_content
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
            api_keys=api_keys
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
            api_keys=api_keys
        )
        
        return ProcessResponse(success=True, result=result)
    
    except Exception as e:
        return ProcessResponse(success=False, error=str(e))


@app.post("/api/save-agent")
async def save_agent(request: SaveAgentRequest):
    """Save an agent from conversation"""
    try:
        agent_manager = AgentManager()
        conversation_id = request.conversation_id
        
        if not conversation_id:
            conversation_id = GeminiAPIClient._get_last_conversation_id('executor')
        
        if not conversation_id:
            raise HTTPException(status_code=404, detail="No conversation found to save")
        
        agent_manager.save_agent(
            agent_name=request.agent_name,
            conversation_id=conversation_id
        )
        
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