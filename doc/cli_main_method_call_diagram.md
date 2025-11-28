# Method Call Diagram for cli.py main()

This diagram shows the method call flow for the `main()` function and all CLI commands in [cli.py](file:///home/userpc/29/ForgeOAgent/forgeoagent/cli.py).

## Main Entry Point Flow

```mermaid
graph TD
    A[main] --> B[cli]
    B --> C{Command Selection}
    C -->|server| D[server command]
    C -->|start| E[start command]
    C -->|executors| F[executors command]
    C -->|inquirers| G[inquirers command]
    C -->|prompt| H[prompt command]
    C -->|execute| I[execute command]
    C -->|config| J[config command]
    C -->|shortcut| K[shortcut command]
```

## Server Command Flow

```mermaid
graph TD
    A[forgeagent server] --> B[server]
    B --> C[Import forgeoagent.web.api]
    B --> D[Import uvicorn]
    B --> E{--open-browser flag?}
    E -->|Yes| F[Create browser thread]
    F --> F1[open_browser_delayed]
    F1 --> F2[time.sleep]
    F2 --> F3[webbrowser.open]
    E -->|No| G[uvicorn.run]
    F --> G
    G --> H[Start FastAPI server]
```

## Start Command Flow

```mermaid
graph TD
    A[forgeagent start] --> B[start]
    B --> C[Locate start.py]
    C --> D{start.py exists?}
    D -->|No| E[Exit with error]
    D -->|Yes| F[subprocess.Popen]
    F --> G[Launch start.py with Python]
    G --> H[GUI Application starts]
```

## Executors Command Flow

```mermaid
graph TD
    A[forgeagent executors] --> B[executors]
    B --> C[print_available_executors]
    C --> D[AgentManager.__init__]
    D --> E[agent_manager.list_executors]
    E --> F[Print agent names]
```

## Inquirers Command Flow

```mermaid
graph TD
    A[forgeagent inquirers] --> B[inquirers]
    B --> C[auto_import_inquirers]
    C --> C1[os.listdir system_prompts]
    C1 --> C2[importlib.import_module]
    C2 --> C3[Load *_SYSTEM_INSTRUCTION constants]
    B --> D[print_available_inquirers]
    D --> E[Print system instruction names]
```

## Prompt Command Flow

```mermaid
graph TD
    A[forgeagent prompt TEXT -i INQUIRER] --> B[prompt]
    B --> C{API keys set?}
    C -->|No| D[Exit with error]
    C -->|Yes| E[Parse API keys]
    E --> F[auto_import_inquirers]
    F --> F1[Import system prompts]
    E --> G[inquirer_using_selected_system_instructions]
    G --> G1[Get system instruction from globals]
    G --> G2[GeminiAPIClient.__init__]
    G2 --> G3[main_agent.search_content]
    G3 --> G4[Print response]
```

## Execute Command Flow

```mermaid
graph TD
    A[forgeagent execute PROMPT -a AGENT] --> B[execute]
    B --> C{API keys set?}
    C -->|No| D[Exit with error]
    C -->|Yes| E[Parse API keys]
    E --> F[auto_import_inquirers]
    F --> G[create_master_executor]
    
    G --> G1[PyClassAnalyzer.analyze_dir - clients]
    G --> G2[PyClassAnalyzer.analyze_dir - MCP_TOOLS_DIR]
    G --> G3[Format system instruction]
    G --> G4[GeminiAPIClient.__init__]
    G4 --> G5[main_agent.generate_content]
    G5 --> G6{Imports needed?}
    G6 -->|Yes| G7[PIPInstallManager]
    G6 -->|No| G8[main_agent._execute_generated_code]
    G7 --> G8
    
    B --> H{--save flag?}
    H -->|Yes| I[save_last_executor]
    I --> I1[GeminiAPIClient._get_last_conversation_id]
    I1 --> I2[AgentManager.__init__]
    I2 --> I3[agent_manager.save_agent]
```

## Config Command Flow

```mermaid
graph TD
    A[forgeagent config] --> B[config]
    B --> C[os.getenv GEMINI_API_KEYS]
    B --> D[Path.home]
    B --> E[Print configuration info]
```

## Shortcut Command Flow

```mermaid
graph TD
    A[forgeagent shortcut] --> B[shortcut]
    B --> C{OS Platform?}
    C -->|Windows| D[Windows Flow]
    C -->|Linux/Other| E[Linux Flow]
    
    D --> D1[Locate create_shortcut.ps1]
    D1 --> D2{Script exists?}
    D2 -->|No| D3[Exit with error]
    D2 -->|Yes| D4[Try powershell]
    D4 --> D5{powershell found?}
    D5 -->|No| D6[Try pwsh]
    D5 -->|Yes| D7[subprocess.run PowerShell script]
    D6 --> D8{pwsh found?}
    D8 -->|Yes| D7
    D8 -->|No| D9[Exit with error]
    
    E --> E1[Locate start.sh]
    E1 --> E2[Print manual instructions]
```

## Alternative Entry Point

```mermaid
graph TD
    A[start_server_cmd] --> B[click.Context]
    B --> C[server.invoke]
    C --> D[server command flow]
```

## Command Summary Table

| Command | Primary Function | Key External Calls |
|---------|-----------------|-------------------|
| `server` | Start FastAPI server | `uvicorn.run()`, `webbrowser.open()` |
| `start` | Launch GUI | `subprocess.Popen()` |
| `executors` | List agents | `print_available_executors()` → `AgentManager.list_executors()` |
| `inquirers` | List system instructions | `auto_import_inquirers()`, `print_available_inquirers()` |
| `prompt` | Run inquirer | `inquirer_using_selected_system_instructions()` → `GeminiAPIClient.search_content()` |
| `execute` | Run executor | `create_master_executor()` → `GeminiAPIClient.generate_content()` |
| `config` | Show config | `os.getenv()`, `Path.home()` |
| `shortcut` | Create shortcut | `subprocess.run()` (Windows), print instructions (Linux) |

## Key External Dependencies

### From forgeoagent.controller.executor_controller
- `print_available_executors()` - Lists all saved agents
- `save_last_executor()` - Saves the last executor conversation
- `create_master_executor()` - Main executor creation and execution

### From forgeoagent.controller.inquirer_controller
- `print_available_inquirers()` - Lists system instructions
- `auto_import_inquirers()` - Auto-imports system prompts
- `inquirer_using_selected_system_instructions()` - Runs inquirer mode

### From forgeoagent.clients.gemini_engine
- `GeminiAPIClient` - Main API client class
- `GeminiAPIClient._get_last_conversation_id()` - Retrieves conversation ID

### From forgeoagent.core.managers
- `AgentManager` - Manages agent storage and retrieval
- `PIPInstallManager` - Handles package installation

### From forgeoagent.core
- `PyClassAnalyzer.analyze_dir()` - Analyzes Python classes in directories

### Third-party Libraries
- `click` - CLI framework for all commands
- `uvicorn` - ASGI server for FastAPI
- `subprocess` - Process management
- `webbrowser` - Browser launching
- `dotenv` - Environment variable loading

## CLI Command Structure

```mermaid
graph LR
    A[forgeagent] --> B[server]
    A --> C[start]
    A --> D[executors]
    A --> E[inquirers]
    A --> F[prompt]
    A --> G[execute]
    A --> H[config]
    A --> I[shortcut]
    
    B --> B1[--host]
    B --> B2[--port]
    B --> B3[--reload]
    B --> B4[--open-browser]
    
    F --> F1[TEXT argument]
    F --> F2[--inquirer/-i]
    F --> F3[--api-keys]
    
    G --> G1[PROMPT_TEXT argument]
    G --> G2[--agent/-a]
    G --> G3[--save/-s]
    G --> G4[--new]
    
    I --> I1[--target/-t]
    I --> I2[--name/-n]
    I --> I3[--hotkey/-k]
```

## Notes

> [!IMPORTANT]
> The `main()` function is the primary entry point registered as the `forgeagent` console script. It delegates to the Click CLI group which routes to individual command handlers.

> [!NOTE]
> There's also a `start_server_cmd()` entry point that can be used as a standalone command to start the server directly.

> [!TIP]
> All commands use Click decorators (`@cli.command()`) to register themselves with the CLI group, making the code modular and easy to extend.

> [!WARNING]
> The `execute` and `prompt` commands require `GEMINI_API_KEYS` environment variable to be set, otherwise they will exit with an error.
