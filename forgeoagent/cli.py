#!/usr/bin/env python3
"""
ForgeOAgent CLI - Command line interface for ForgeOAgent
Entry points for pip console_scripts
"""
import os
import sys
import subprocess
import click
from pathlib import Path
from dotenv import load_dotenv

# Load environment first
load_dotenv()

# Ensure current directory is in path for relative imports
current_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))

# Import after path setup
from forgeoagent.clients.gemini_engine import GeminiAPIClient
from forgeoagent.controller.executor_controller import (
    print_available_executors,
    save_last_executor,
    create_master_executor
)
from forgeoagent.controller.inquirer_controller import (
    print_available_inquirers,
    auto_import_inquirers,
    inquirer_using_selected_system_instructions
)


@click.group()
def cli():
    """ForgeOAgent - AI Agent Framework powered by Gemini API"""
    pass


@cli.command()
@click.option('--host', default='127.0.0.1', help='Server host')
@click.option('--port', default=8000, type=int, help='Server port')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
@click.option('--open-browser', is_flag=True, help='Automatically open browser')
def server(host, port, reload, open_browser):
    """Start the ForgeOAgent FastAPI server"""
    click.echo(f"🚀 Starting ForgeOAgent server on {host}:{port}...")
    
    # Import api module
    from forgeoagent.web.api import app
    import uvicorn
    
    # Optional: open browser after slight delay
    if open_browser:
        def open_browser_delayed():
            import time
            import webbrowser
            time.sleep(2)
            webbrowser.open(f'http://{host}:{port}')
        
        import threading
        thread = threading.Thread(target=open_browser_delayed, daemon=True)
        thread.start()
    
    uvicorn.run(
        "forgeoagent.web.api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


@cli.command()
def start():
    """Launch the ForgeOAgent GUI application"""
    click.echo("🚀 Starting ForgeOAgent GUI...")
    
    import subprocess
    from pathlib import Path
    
    # Get the start.py path
    start_py = Path(__file__).parent / "start.py"
    
    if not start_py.exists():
        click.echo(f"❌ Error: start.py not found at {start_py}")
        sys.exit(1)
    
    try:
        subprocess.Popen([sys.executable, str(start_py)])
        click.echo("✅ GUI application launched successfully")
    except Exception as e:
        click.echo(f"❌ Error launching GUI: {e}", err=True)
        sys.exit(1)


@cli.command()
def executors():
    """List all available executors/agents"""
    click.echo("📋 Available Executors:")
    print_available_executors()


@cli.command()
def inquirers():
    """List all available inquirers (system instructions)"""
    click.echo("📋 Available Inquirers (System Instructions):")
    auto_import_inquirers()
    print_available_inquirers()


@cli.command()
@click.argument('text')
@click.option('--inquirer', '-i', required=True, help='Inquirer/system instruction to use')
@click.option('--api-keys', envvar='GEMINI_API_KEYS', help='Comma-separated Gemini API keys')
def prompt(text, inquirer, api_keys):
    """Run a prompt through the specified inquirer"""
    if not api_keys:
        click.echo("❌ Error: GEMINI_API_KEYS environment variable not set")
        sys.exit(1)
    
    api_key_list = [key.strip() for key in api_keys.split(",") if key.strip()]
    
    click.echo(f"🔍 Running inquirer: {inquirer}")
    
    auto_import_inquirers()
    inquirer_using_selected_system_instructions(text, api_key_list, inquirer)


@cli.command()
@click.argument('prompt_text')
@click.option('--agent', '-a', default='None', help='Agent/executor type')
@click.option('--save', '-s', help='Save result as agent with name')
@click.option('--new', is_flag=True, help='Create new agent')
def execute(prompt_text, agent, save, new):
    """Execute a prompt using the master executor"""
    api_keys = os.getenv("GEMINI_API_KEYS", "")
    if not api_keys:
        click.echo("❌ Error: GEMINI_API_KEYS environment variable not set")
        sys.exit(1)
    
    api_key_list = [key.strip() for key in api_keys.split(",") if key.strip()]
    
    click.echo(f"⚙️  Executing prompt...")
    
    auto_import_inquirers()
    
    try:
        create_master_executor(
            api_key_list,
            prompt_text,
            shell_enabled=True,
            selected_agent={"agent_name": agent},
            new_content=new
        )
        
        if save:
            click.echo(f"💾 Saving result as: {save}")
            save_last_executor(save)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def config():
    """Show ForgeOAgent configuration and environment"""
    click.echo("\n🔧 ForgeOAgent Configuration:")
    click.echo(f"  API Keys configured: {'✓' if os.getenv('GEMINI_API_KEYS') else '✗'}")
    click.echo(f"  Home directory: {Path.home()}")
    click.echo(f"  Config directory: {Path.home() / '.forgeagent'}")


@cli.command()
@click.option('--target', '-t', default='', help='Target file to point the shortcut to (optional)')
@click.option('--name', '-n', default='Start Script', help='Shortcut name')
@click.option('--hotkey', '-k', default='Ctrl+Alt+S', help='Hotkey to assign (Windows only)')
def shortcut(target, name, hotkey):
    """Create a desktop shortcut on Windows or print instructions for Linux

    On Windows this will invoke the PowerShell helper at shell/windows/create_shortcut.ps1.
    On Linux it prints instructions for creating a keyboard shortcut and the path to `start.sh` to paste into the launcher command.
    """
    repo_root = os.path.dirname(os.path.abspath(__file__))
    if os.name == 'nt' or sys.platform.startswith('win'):
        # Windows: call the PowerShell script we added
        ps1 = Path(repo_root + '/../shell/windows/create_shortcut.ps1').resolve()
        if not ps1.exists():
            click.echo(f"❌ PowerShell helper not found at {ps1}")
            sys.exit(1)

        cmd_base = []
        # try Windows PowerShell then pwsh
        tried = []
        for pw in ("powershell", "pwsh"):
            tried.append(pw)
            cmd = [pw, '-ExecutionPolicy', 'Bypass', '-File', str(ps1)]
            if target:
                cmd += ['-TargetFile', target]
            if name:
                cmd += ['-ShortcutName', name]
            if hotkey:
                cmd += ['-Hotkey', hotkey]

            try:
                click.echo(f"➡️ Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                if result.stdout:
                    click.echo(result.stdout.strip())
                if result.stderr:
                    click.echo(result.stderr.strip(), err=True)
                click.echo("✅ Shortcut creation completed.")
                return
            except FileNotFoundError:
                # powershell executable not found, try next
                continue
            except subprocess.CalledProcessError as e:
                click.echo(f"❌ PowerShell script failed: {e}\n{e.stderr}", err=True)
                sys.exit(1)

        click.echo(f"❌ Could not find PowerShell executable. Tried: {', '.join(tried)}")
        sys.exit(1)
    else:
        # Non-Windows: print instructions for manual creation
        linux_start = Path(repo_root + '/shell/linux/start.sh').resolve()


        click.echo(f"ℹ️ Start script path: {linux_start}")
        if linux_start.exists():
            start_path = str(linux_start.resolve())
        else:
            alt = repo_root + '/start.sh'
            start_path = str(alt.resolve()) if alt.exists() else '<path-to-start.sh>'

        click.echo("\n🔔 Create a keyboard shortcut (manual steps):")
        click.echo("  1) Open Settings > Keyboard (or Keyboard Shortcuts) -> Shortcuts")
        click.echo("  2) Create a new custom shortcut and assign the desired keybinding.")
        click.echo(f"  3) For the command/launcher field, paste the full path to the start script:\n     {start_path}")
        click.echo("  4) Save the shortcut. You can test it by pressing the assigned hotkey.")


def main():
    """Main entry point for 'forgeagent' command"""
    try:
        cli()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def start_server_cmd():
    """Standalone entry point for 'forgeagent-start' command"""
    import click
    ctx = click.Context(server)
    server.invoke(ctx)


if __name__ == '__main__':
    main()
