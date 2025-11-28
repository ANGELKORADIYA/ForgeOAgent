# Method Call Diagram for start.py

This diagram shows the method call flow for the main execution paths in [start.py](file:///home/userpc/29/ForgeOAgent/forgeoagent/start.py).

## Main Entry Point Flow

```mermaid
graph TD
    A[main] --> B[PromptProcessorApp.OnInit]
    B --> C[PromptProcessorFrame.__init__]
    C --> D[init_ui]
    C --> E[load_prompt_types]
    C --> F[auto_import_inquirers]
    
    D --> D1[Bind wx.EVT_BUTTON events]
    D --> D2[Bind wx.EVT_RADIOBUTTON events]
    
    E --> E1[capture_print_output]
    E1 --> E2[print_available_executors]
    E1 --> E3[print_available_inquirers]
```

## User Interaction Flow - Process Button

```mermaid
graph TD
    A[User clicks Process button] --> B[on_process]
    B --> B1{Validate inputs}
    B1 -->|Invalid| B2[Show error dialog]
    B1 -->|Valid| B3[Create background thread]
    B3 --> C[process_in_background]
    
    C --> C1{Check mode}
    C1 -->|Executor Mode| D[Executor Processing]
    C1 -->|Inquirer Mode| E[Inquirer Processing]
    
    D --> D1[AgentManager.__init__]
    D --> D2[agent_manager.get_agent_path]
    D --> D3[capture_print_output]
    D3 --> D4[create_master_executor]
    D --> D5[wx.CallAfter - show_result]
    
    E --> E1[capture_print_output]
    E1 --> E2[inquirer_using_selected_system_instructions]
    E --> E3[wx.CallAfter - show_result]
    
    D5 --> F[show_result]
    E3 --> F
    F --> G[ResultDialog.__init__]
    G --> H[ResultDialog.init_ui]
    
    C --> C2{Exception?}
    C2 -->|Yes| I[wx.CallAfter - show_error]
    C2 -->|No| J[wx.CallAfter - reset_ui]
```

## Mode Change Flow

```mermaid
graph TD
    A[User changes mode radio button] --> B[on_mode_change]
    B --> C[load_prompt_types]
    C --> D[capture_print_output]
    D --> E{Check mode}
    E -->|Executor| F[print_available_executors]
    E -->|Inquirer| G[print_available_inquirers]
    F --> H[Update prompt_choice control]
    G --> H
```

## File/Clipboard Operations Flow

```mermaid
graph TD
    A1[User clicks Load File] --> B1[on_load_file]
    B1 --> B2[wx.FileDialog.ShowModal]
    B2 --> B3[Read file content]
    B3 --> B4[context_text.SetValue]
    
    A2[User clicks Get Clipboard] --> C1[on_get_clipboard]
    C1 --> C2[wx.TheClipboard.Open]
    C2 --> C3[wx.TheClipboard.GetData]
    C3 --> C4[context_text.SetValue]
    
    A3[User clicks Clear] --> D1[on_clear_context]
    D1 --> D2[context_text.SetValue - empty]
    
    A4[User clicks Refresh Types] --> E1[on_refresh_types]
    E1 --> E2[load_prompt_types]
```

## Result Dialog Flow

```mermaid
graph TD
    A[ResultDialog.__init__] --> B[init_ui]
    B --> C[Create UI controls]
    C --> D[Bind button events]
    
    E1[User clicks Copy] --> F1[on_copy]
    F1 --> F2[wx.TheClipboard.Open]
    F2 --> F3[wx.TheClipboard.SetData]
    F3 --> F4[Show success message]
    
    E2[User clicks Save] --> G1[on_save]
    G1 --> G2[wx.TextEntryDialog]
    G2 --> G3[GeminiAPIClient._get_last_conversation_id]
    G3 --> G4[AgentManager.__init__]
    G4 --> G5[agent_manager.save_agent]
    G5 --> G6[Show success message]
    
    E3[User clicks Close] --> H1[on_close]
    H1 --> H2[EndModal]
```

## Helper Method: capture_print_output

```mermaid
graph TD
    A[capture_print_output called] --> B[Redirect sys.stdout to StringIO]
    B --> C[Execute passed function with args]
    C --> D{Exception?}
    D -->|Yes| E[Capture output and raise exception]
    D -->|No| F[Return output and result]
    E --> G[Restore sys.stdout]
    F --> G
```

## Key Method Categories

### Initialization Methods
- `main()` - Entry point
- `PromptProcessorApp.OnInit()` - App initialization
- `PromptProcessorFrame.__init__()` - Main frame setup
- `PromptProcessorFrame.init_ui()` - UI component creation
- `ResultDialog.__init__()` - Result dialog setup
- `ResultDialog.init_ui()` - Result dialog UI creation

### Event Handlers
- `on_process()` - Main processing trigger
- `on_mode_change()` - Mode radio button handler
- `on_refresh_types()` - Refresh button handler
- `on_load_file()` - Load file button handler
- `on_get_clipboard()` - Clipboard button handler
- `on_clear_context()` - Clear button handler
- `on_copy()` - Copy to clipboard handler
- `on_save()` - Save result handler
- `on_close()` - Close dialog handler

### Processing Methods
- `process_in_background()` - Background thread processing
- `capture_print_output()` - Utility to capture stdout
- `load_prompt_types()` - Load available prompt types

### UI Update Methods
- `show_result()` - Display processing result
- `show_error()` - Display error message
- `reset_ui()` - Reset UI state after processing

### External Dependencies (from main.py)
- `inquirer_using_selected_system_instructions()` - Inquirer mode processing
- `print_available_inquirers()` - Get available inquirers
- `print_available_executors()` - Get available executors
- `auto_import_inquirers()` - Auto-import system prompts
- `create_master_executor()` - Executor mode processing
- `GeminiAPIClient._get_last_conversation_id()` - Get conversation ID
- `AgentManager.get_agent_path()` - Get agent file path
- `AgentManager.save_agent()` - Save agent result

## Notes

> [!NOTE]
> The file doesn't contain a function explicitly named `action`. The main action flow starts from the `on_process()` event handler when the user clicks the "Process" button.

> [!IMPORTANT]
> Processing happens in a background thread (`process_in_background`) to keep the UI responsive. Results are passed back to the main thread using `wx.CallAfter()`.

> [!TIP]
> The `capture_print_output()` utility method is used extensively to capture stdout from functions that use print statements, allowing the GUI to display their output.
