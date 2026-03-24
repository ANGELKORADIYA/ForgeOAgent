import subprocess
import os
import sys

def build():
    """Build the ForgeOAgent executable using PyInstaller."""
    
    # Root directory of the project
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)
    
    # Entry point wrapper
    entry_point = "forgeoagent/start.py"  
    
    # Icon path
    icon_path = os.path.join("forgeoagent", "web", "static", "favicon.ico")
    if not os.path.exists(icon_path):
        icon_path = None # Fallback if icon is missing
    
    # Base command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=ForgeOAgent",
    ]
    
    if icon_path:
        cmd.append(f"--icon={icon_path}")
    
    # Add data files (format: source;destination)
    # mcp and web are essential for system prompts and the web interface
    cmd.extend([
        "--add-data=forgeoagent/mcp;forgeoagent/mcp",
        "--add-data=forgeoagent/web;forgeoagent/web",
    ])
    
    # Hidden imports for dynamic package discovery
    # auto_import_inquirers imports from forgeoagent.mcp.system_prompts.*
    # We should ensure these are collected
    cmd.extend([
        "--collect-all=forgeoagent",
    ])
    
    # Add the entry point
    cmd.append(entry_point)
    
    print(f"🚀 Starting build with command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output
        for line in process.stdout:
            print(line, end="")
            
        process.wait()
        
        if process.returncode == 0:
            print("\n✅ Build successful! Check the 'dist' folder for ForgeOAgent.exe")
        else:
            print(f"\n❌ Build failed with exit code {process.returncode}")
            
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    build()
