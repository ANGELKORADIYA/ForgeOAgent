# ForgeOAgent

ForgeOAgent is a powerful Python-based AI agent designed to enhance and automate various text-based and code-related tasks leveraging the Google Gemini API. It provides a structured way to interact with advanced generative models, offering functionalities for prompt improvement, code refinement, email generation, and more, all managed with an integrated security system.

## Description

This project serves as a flexible framework for building and managing AI agents that interact with the Google Gemini API. Its primary goal is to streamline common content generation and manipulation workflows through intelligent prompt engineering and secure API key management. It supports interactive command-line usage and can be extended with custom system instructions and agent configurations.

### `build_exe.py`
### Functionality
This Python script, `build_exe.py`, automates the process of converting a Python script named `main.py` into a standalone executable file using the `PyInstaller` tool. It achieves this by programmatically invoking `PyInstaller` via a subprocess call.

### Features
*   **One-file Executable**: Uses the `--onefile` option with PyInstaller to bundle all dependencies into a single executable file, simplifying distribution.
*   **Custom Executable Name**: Specifies the output executable name as `python_exe_converter` using the `--name` option.
*   **Automated PyInstaller Execution**: Leverages Python's `subprocess` module to run PyInstaller commands directly from the script.
*   **Error Handling**: Includes basic error handling to catch and report `subprocess.CalledProcessError` if the PyInstaller build fails.
*   **Cross-platform (PyInstaller dependent)**: While the script itself is Python, the generated executable's portability depends on PyInstaller's capabilities for the specific operating system it's run on.

### Uses
*   **Application Packaging**: To package a Python application (`main.py`) into an easily distributable executable for users who may not have Python installed.
*   **Simplified Deployment**: For deploying command-line tools or small applications by providing a single executable file rather than requiring users to set up a Python environment and install dependencies.
*   **Creating Portable Utilities**: To create a portable version of a Python script that can be run on different Windows, macOS, or Linux machines without needing a Python interpreter.

### `main.py`
### Functionality
This Python script serves as a command-line interface (CLI) for interacting with a Gemini API client, primarily for various AI-driven text and code processing tasks. It dynamically loads system instructions for different AI prompts (e.g., text enhancement, email generation, code refinement, regex), allows execution of these prompts, and provides utilities to list available prompt types or saved agents. It integrates a security monitoring system and manages API keys loaded from environment variables.

### Features
*   **Dynamic Prompt Loading**: Automatically identifies and loads system instructions for AI prompts based on naming conventions (e.g., `_SYSTEM_INSTRUCTION`).
*   **Prompt Enhancement/Generation**:
    *   `run_prompt_improvement`: A core function to send user input to the Gemini API with a specified system instruction, enabling tasks like text enhancement, email generation, or code refinement.
    *   Supports `new_content` flag for `GeminiAPIClient`.
*   **Agent Management Integration**: Interacts with an `AgentManager` to list and potentially utilize pre-saved AI agent configurations.
*   **Command-Line Argument Parsing**:
    *   `-l`: Lists available system instructions (default) or saved agents (with `--main`).
    *   `-p <type> <prompt>`: Executes a specific AI prompt type with the given user input, applying a corresponding system instruction.
    *   `--new`: Modifies the behavior of prompt execution, likely related to content generation mode.
    *   `--main`: Activates a "main" operational mode, which appears to delegate control to the `main` function of `gemini_client`, potentially for more complex agent interactions or a primary application flow.
*   **API Key Management**: Loads Gemini API keys securely from environment variables.
*   **Security Monitoring**: Initializes and stops a `SecurityManager`, indicating a built-in mechanism for security-related operations (though the specifics are abstracted).

### Uses
*   **AI-Powered Text Processing**: Users can quickly enhance text, generate emails, or refine existing code snippets by specifying the desired prompt type and input text via the command line.
*   **Developer Tool**: Useful for developers to test different AI prompts or integrate AI capabilities into their workflow, especially for tasks requiring text manipulation, code assistance, or content generation.
*   **Agent Interaction**: Can be used to list and interact with pre-configured AI agents for automated tasks or complex conversational flows.
*   **Experimentation with Gemini API**: Provides a straightforward CLI for experimenting with different Gemini API functionalities and custom system instructions without writing extensive boilerplate code for each interaction.
*   **Scripting and Automation**: Can be incorporated into larger scripts for automated content generation, code review, or data processing tasks using AI.

### `clients\gemini_client.py`
### Functionality
This Python code defines a robust client for interacting with the Google Gemini API, enabling the creation and execution of AI agents. It manages API keys, maintains conversation history, logs interactions, and dynamically executes Python code generated by the large language model. The `main` function orchestrates the agent's operation, allowing users to provide requests, install necessary Python packages, and save agents for future use.

### Features
*   **Gemini API Integration**: Provides a simplified interface for `google.genai` with configurable models, system instructions, safety settings, and output schemas.
*   **API Key Management**: Integrates with `GlobalAPIKeyManager` for dynamic API key rotation and retry logic in case of `Unauthenticated` or `ResourceExhausted` errors, enhancing reliability.
*   **Conversation Logging & History**: Automatically logs all API interactions (prompts, responses, errors) to `.jsonl` files, indexed by a conversation ID, and can load previous conversation history to maintain context.
*   **Reference Agent Context**: Allows feeding previous agent interactions from specified log folders (`.jsonl` files) as contextual information to the Gemini model, enabling more informed responses.
*   **Dynamic Code Generation & Execution**: Designed to receive Python code within JSON responses from the Gemini API and safely execute it within a controlled environment, providing access to essential modules and utilities.
*   **Package Installation**: Automatically detects required Python packages from the generated code's `imports` and uses `pip_install_manager` to install them before execution.
*   **Error Handling and Retries**: Implements comprehensive error handling for API calls (including specific Gemini API exceptions) and internal operations, with configurable retry attempts.
*   **Configurable Prompts and Schema**: Utilizes external configuration for system instructions, required output properties, and JSON response schema validation for structured outputs.
*   **Interactive Agent Management**: The `main` function supports interactive selection, creation, and saving of AI agents, facilitating reusability.

### Uses
*   **Building Conversational AI Agents**: Develop AI agents that can maintain context over multiple turns and generate executable actions.
*   **Automated Task Execution**: Create agents that receive natural language requests and respond by generating and running Python code to perform tasks (e.g., file operations, data processing, API calls).
*   **Prompt Engineering and Iteration**: Test and refine prompts by observing the agent's generated code and responses, with logging for easy review.
*   **Intelligent Automation Frameworks**: Serve as a core component for systems requiring dynamic, AI-driven automation based on complex instructions.
*   **Interactive Development Environment**: Act as an intelligent assistant that can understand user goals, write code, and execute it, accelerating development workflows.

### `core\managers\agent_manager.py`
### Functionality
The `AgentManager` class is designed to manage the saving, listing, and selection of conversational agents. It facilitates the persistence of agent interaction logs and metadata, primarily focusing on the last successful interaction of a "main" agent. It organizes saved agent data within a designated directory structure, making it easy to retrieve previously used agent configurations and their relevant conversation history.

### Features
*   **Agent Directory Management**: Automatically creates and manages a dedicated directory (`./agents` by default) for storing saved agent data.
*   **Selective Interaction Saving**: Saves only the last successful interaction of a main agent from a specified conversation log file (`.jsonl`).
*   **Metadata Storage**: Stores comprehensive metadata for each agent, including agent name, conversation ID, task IDs (though task log saving is commented out in the provided code), save timestamp, and associated log files.
*   **Agent Listing**: Provides a method to list all currently saved agents with their relevant metadata.
*   **Path Retrieval**: Offers a utility to retrieve the file system path for a specific saved agent's folder.
*   **Interactive Agent Selection**: Includes an interactive command-line interface for users to either select an existing agent or opt to create a new one, displaying detailed information about available agents.
*   **Error Handling**: Incorporates basic error handling for file operations and invalid user inputs during agent selection.

### Uses
*   **Session Management for AI Agents**: Allows AI applications to persist the state or key interactions of conversational agents, enabling users to resume or refer to past agent sessions.
*   **Debugging and Auditing**: By saving specific agent interactions, it can be used for debugging agent behavior or auditing conversation flows for quality assurance.
*   **Agent Versioning/Snapshots**: Could be extended to create snapshots of agent configurations or specific interaction points, useful for tracking agent evolution or A/B testing different agent designs.
*   **Demonstration and Portfolio**: Enables developers to easily showcase different trained or configured agents by loading them from saved states.
*   **User Experience Enhancement**: Provides a streamlined way for users of an AI application to pick up where they left off with a particular agent or to switch between different agent personalities/tasks.

### `core\managers\api_key_manager.py`
### Functionality
This Python class, `GlobalAPIKeyManager`, serves as a singleton for robustly managing a pool of API keys. Its core functionality involves providing a thread-safe mechanism to retrieve API keys, intelligently rotating through them, marking failed keys to prevent their immediate reuse, and automatically resetting their status daily. It also tracks usage statistics (requests and failures) for each key and provides a detailed status report.

### Features
*   **Singleton Pattern**: Ensures only one instance of the API key manager exists throughout the application, providing a centralized control point.
*   **Thread Safety**: Uses `threading.Lock` to protect shared resources (`_api_keys`, `_current_index`, `_failed_keys`, `_usage_stats`) from race conditions in multi-threaded environments.
*   **Intelligent Key Rotation**: When `get_current_key` is called, it rotates through the available API keys, automatically skipping any keys that have been marked as failed. If all keys fail, it raises an exception.
*   **Automatic Daily Reset**: The `_check_and_reset_daily` method automatically clears the list of failed keys and resets daily usage statistics at the start of a new day, allowing previously failed keys to be retried.
*   **Failure Tracking**: Keys can be explicitly marked as failed using `mark_key_failed`, which adds them to a set of unavailable keys and increments their failure count.
*   **Usage Statistics**: Tracks the number of requests and failures for each individual API key, providing insights into their performance.
*   **Manual Reset**: Provides a `force_reset_failed_keys` method for administrators or testing purposes to manually clear all failed key statuses.
*   **Comprehensive Status Reporting**: The `get_detailed_status` method returns a dictionary with various metrics, including total/active/failed key counts, current key in use, usage statistics, and last reset date.
*   **Input Validation**: Checks for empty API key lists during initialization.

### Uses
*   **Managing API Rate Limits**: Applications interacting with external APIs that impose rate limits can use this manager to distribute requests across multiple keys, preventing individual keys from hitting limits too quickly.
*   **Improving API Reliability**: In scenarios where external API keys might intermittently fail or become invalid, this manager automatically rotates to a working key, improving the overall reliability of API calls.
*   **Load Balancing**: Distributing API requests across a pool of keys to balance the load and prevent any single key from becoming a bottleneck.
*   **Monitoring API Key Health**: The usage statistics and detailed status report can be used to monitor the performance and health of individual API keys, helping identify problematic keys or services.
*   **Fault Tolerance**: Provides a layer of fault tolerance for applications heavily reliant on external services, ensuring that the failure of one API key does not bring down the entire system.
*   **Automated Testing**: Can be integrated into automated testing frameworks to simulate API key failures and test the application's resilience.

### `core\config_prompts.py`
### Functionality
This Python code primarily defines the core configurations, system instructions, and output schemas for various AI agents within an AI-powered system. It sets the behavioral guidelines, available tools, and expected output formats for a "Master Agent Creator," a general-purpose AI assistant, a web search agent, and a prompt enhancement agent.

### Features
*   **Master Agent Configuration**: Defines the `MAIN_AGENT_SYSTEM_INSTRUCTION` for an agent that breaks down user requests into executable Python code, listing available tools (like `GeminiAPIClient`, `os`, `json`, `pip_install_manager`) and strict safety constraints.
*   **Structured Output Definition**: Uses `google.genai.types.Schema` to specify the exact JSON output format required for the Master Agent (including `explanation`, `python` code, task `ids`, and `imports`).
*   **Default AI Assistant Settings**: Provides a `DEFAULT_SYSTEM_INSTRUCTION` for a general AI assistant, emphasizing safety, error handling, and privacy. It also defines its expected output structure.
*   **Safety Constraints Enforcement**: Explicitly lists core safety constraints that all agents must follow, such as preventing modification of system-critical files, validating paths, and respecting privacy.
*   **Model and Safety Defaults**: Sets `DEFAULT_MODEL` (`gemini-2.5-flash-preview-05-20`) and `DEFAULT_SAFETY_SETTINGS` to control content generation.
*   **Specialized Agent Instructions**: Includes dedicated system instructions for a `DEFAULT_SYSTEM_INSTRUCTION_SEARCH` (web search) and a `PROMPT_ENHANCER_SYSTEM_INSTRUCTION` (for refining user prompts).

### Uses
*   **Building Multi-Agent AI Systems**: Serves as a foundational configuration layer for orchestrating different AI agents, each with a specialized role (code generation, search, prompt engineering, general assistance).
*   **Automated Code Generation Platforms**: The Master Agent configuration is crucial for systems that automatically generate Python code based on natural language requests, ensuring safety and adherence to specified tools.
*   **AI-Driven Development Environments**: Can be integrated into environments where AI assists developers by generating code, providing information, or refining input prompts.
*   **Task Automation**: Used to define the operational rules and expected outputs for AI components in broader task automation or workflow management systems.
*   **Standardizing AI Agent Behavior**: Provides a centralized place to define consistent instructions, constraints, and output formats across various AI functionalities within an application.

### `core\managers\pip_install_manager.py`
### Functionality
This Python code provides a highly secure and robust mechanism for programmatically installing Python packages using `pip`. Its primary function, `pip_install_manager`, takes a list of package names and attempts to install them one by one. It integrates multiple layers of security validation for package names, preventing common vulnerabilities such as command injection, path traversal, and the use of dangerous pip options. The module handles errors gracefully, provides detailed feedback on successful and failed installations, and includes timeouts for each installation attempt.

### Features
*   **Comprehensive Security Validation**: Employs strict validation rules (`_is_package_name_safe`) for package names, including:
    *   Regular expression matching for standard PyPI naming conventions.
    *   Blocking dangerous characters (e.g., `;`, `&`, `|`).
    *   Prevention of command injection sequences (e.g., `rm `, `exec`, `../`).
    *   Blocking of sensitive pip-specific options (e.g., `--target`, `--editable`).
    *   Exclusion of URL-like patterns and local file paths.
    *   Blacklisting of critical or potentially malicious package names (`pip`, `os`).
    *   Enforcement of package name length limits and whitespace removal.
*   **Command Injection Prevention**: Utilizes `subprocess.run` with `shell=False` to ensure that package names are passed as direct arguments to `pip`, completely mitigating shell-related injection risks.
*   **Batch and Individual Validation**: Includes a preliminary batch validation (`_validate_packages_security`) and rigorous individual package name validation.
*   **Robust Error Handling**: Catches installation timeouts (`subprocess.TimeoutExpired`) and general exceptions, providing specific error messages for failed packages.
*   **Installation Timeout**: Each package installation is limited to a 5-minute timeout.
*   **Clear Status Reporting**: Returns a dictionary with a `status` (success, partial_success, security_error), lists of `installed` and `failed` packages, and a descriptive `message`.
*   **No Cache Directory**: Uses `--no-cache-dir` during pip installation to prevent excessive disk usage.
*   **User Feedback**: Prints progress and results to the console, making it easy to track the installation process.

### Uses
*   **Automated Deployment and CI/CD Pipelines**: Securely installing project dependencies in automated build, test, and deployment environments where untrusted inputs might be present.
*   **Dynamic Dependency Management**: Applications that need to download and install missing Python packages at runtime in a controlled and secure manner.
*   **Sandboxed Environments**: Providing a safer way to allow users or automated agents to install packages within virtual environments or containers where system integrity is critical.
*   **Interactive Shells/User-Facing Tools**: Building tools or platforms that allow users to specify packages for installation, ensuring that malicious or malformed package names are rejected.
*   **Educational Platforms**: Offering a secure `pip install` functionality within educational coding environments.
*   **Agent-Based Systems**: For agents that need to install libraries to complete tasks, ensuring they do so without introducing security vulnerabilities.

### `core\managers\security_manager.py`
### Functionality
This Python code defines a `SecurityManager` class responsible for monitoring an application's execution environment and terminating it under specific security or operational conditions. It primarily implements two mechanisms: a "kill switch" that watches for the presence of a specific file in designated locations, and a time-based execution limit. Both checks run in separate background threads, ensuring continuous monitoring without blocking the main application flow.

### Features
*   **Kill Switch Monitoring:** Continuously checks for the existence of a `.killswitch` file (or a specified custom filename) in multiple critical locations:
    *   Relative to the script's directory (project root).
    *   The user's Desktop directory (cross-platform).
    *   The system's temporary directory (`/tmp` on Unix-like, `C:\\Temp` on Windows).
*   **Execution Timeout:** Enforces a maximum duration for the application's runtime. If the specified `timeout_seconds` is exceeded, the application is terminated.
*   **Background Threading:** Utilizes `threading` to run both the kill switch monitoring and timeout enforcement concurrently in daemon threads, allowing the main application to proceed normally while being monitored.
*   **Cross-Platform Compatibility:** Uses `os` module functions (`os.path.abspath`, `os.path.join`, `os.path.expanduser`, `os.name`) to ensure file path resolution and directory access work correctly across different operating systems.
*   **Immediate Termination:** Employs `os._exit(1)` for immediate and forceful application termination, bypassing normal exit routines to ensure quick shutdown in critical scenarios.
*   **Configurable Parameters:** Allows customization of the kill switch file path and the timeout duration during initialization.
*   **Stop Monitoring Capability:** Provides a `stop_monitoring` method to gracefully signal the background threads to cease their operations, allowing for controlled shutdown of the security features if needed.

### Uses
*   **Sandbox Environments:** Limiting the execution time or providing an emergency stop for code running in a controlled or untrusted environment.
*   **Automated Testing/CI/CD:** Ensuring that long-running tests or build processes do not exceed allocated time slots, preventing resource exhaustion or deadlocks.
*   **Trial Software:** Implementing time-limited demonstrations or trial versions of applications.
*   **System Stability:** As a failsafe mechanism in critical applications where a quick, manual shutdown (via kill switch file) or an automatic timeout is necessary to prevent system instability or resource leaks.
*   **Preventing Infinite Loops:** For scripts or processes that might inadvertently enter an infinite loop, the timeout mechanism can ensure termination.

### `core\test_agent_manager.py`
### Functionality
This Python code provides a suite of unit tests for the `AgentManager` class. It specifically tests functionalities related to saving, listing, and retrieving paths for agents managed by the `AgentManager`. It sets up a controlled test environment by creating temporary directories for agents and logs, simulating agent conversation log files, and cleaning up these resources after tests run.

### Features
*   **Unit Testing Framework**: Utilizes Python's built-in `unittest` module for creating and running tests.
*   **Test Fixtures**: Employs `setUp` and `tearDown` methods to initialize and clean up the test environment (e.g., creating and removing temporary `agents` and `logs` directories).
*   **Mock Log Creation**: Includes a helper method `_create_log_file` to simulate the creation of `.jsonl` log files, essential for testing the `save_agent` functionality which depends on these logs.
*   **Path Management Simulation**: Temporarily renames the `logs` directory within the test methods to simulate how the `AgentManager` might interact with a `logs` directory at its expected location in a production environment.
*   **Assertion-Based Validation**: Uses various `unittest` assertions (`assertTrue`, `assertFalse`, `assertEqual`, `os.path.exists`) to verify the correct behavior and outcomes of `AgentManager` operations.

### Uses
*   **Quality Assurance**: Ensures the `AgentManager` class functions as expected by systematically testing its core methods.
*   **Regression Testing**: Helps identify if new code changes introduce bugs or break existing functionalities of the `AgentManager`.
*   **Development Support**: Aids developers in verifying the correctness of the `AgentManager` class during its development and refactoring phases.
*   **Code Reliability**: Contributes to the overall reliability and robustness of the `AgentManager` component by providing automated checks for its operations.

### `core\prompts\enhance_prompt.py`
### Functionality
This Python code defines two string constants that represent instructions for an AI language model, specifically designed for prompt engineering. `ENHANCE_PROMPT_SYSTEM_INSTRUCTION` provides a comprehensive, detailed set of guidelines for an AI to act as an expert prompt engineer, instructing it on how to optimize user prompts. `ENHANCE_PROMPT_USER_INSTRUCTION` serves as a simple prefix to initiate the prompt improvement task by providing the user's raw prompt to the AI.

### Features
*   **Comprehensive Prompt Optimization Framework**: The system instruction outlines a structured approach to prompt improvement, covering clarity, structure, context, output specifications, constraints, and enhancement strategies.
*   **Role-Playing Directive**: It explicitly instructs the AI to "Act as an expert prompt engineer," setting the persona for its task.
*   **Defined Principles and Protocol**: Specifies core principles for prompt optimization (e.g., improve, not complete; focus solely on optimization) and a strict response protocol (output only improved text, no commentary).
*   **Quality Assurance Checkpoints**: Includes a checklist for the AI to verify the quality of its improved prompts before finalizing.
*   **Graceful Degradation**: Provides an instruction to return the original input text if the AI cannot generate a meaningful improvement.
*   **Standardized User Input Format**: Offers a consistent way to wrap the user's prompt for the AI's processing.

### Uses
*   **Automated Prompt Engineering**: To power an AI-driven system or service that automatically enhances and refines user-submitted prompts for other AI language models.
*   **Developer Tools and APIs**: As core instructions within a larger application or API that offers prompt optimization as a feature.
*   **Internal AI Agent Configuration**: To configure a specialized AI agent or chatbot designed for prompt engineering tasks within an organization.
*   **Educational Resource**: The detailed `ENHANCE_PROMPT_SYSTEM_INSTRUCTION` can also serve as a valuable reference or training material for humans learning prompt engineering best practices.

### `start.py`
### Functionality
This Python script implements a sophisticated graphical user interface (GUI) using wxPython for the ForgeOAgent system. It provides a user-friendly way to interact with the Gemini API client, managing both simple prompt processing and complex agent-based operations through a clean, intuitive interface.

### Features
*   **Dual Processing Modes**:
    *   **Simple Mode**: For straightforward prompt processing using system instructions
    *   **Main Mode**: For complex agent-based operations and interactions
*   **Rich User Interface Components**:
    *   **Mode Selection**: Radio buttons to switch between Simple and Main modes
    *   **Prompt Type Selection**: Dropdown menu with dynamic loading of available prompt types
    *   **Context Input**: Text area for loading additional context from files or clipboard
    *   **User Input**: Multi-line text area for entering prompts
    *   **Processing Options**: Configurable settings like "Process as New Content"
*   **File and Clipboard Integration**:
    *   Load context from text files
    *   Get text directly from system clipboard
    *   Save results to clipboard
*   **Result Management**:
    *   Dedicated result dialog with copy-to-clipboard functionality
    *   Option to save results (in Main mode) for future reference
*   **Background Processing**:
    *   Asynchronous prompt processing using threading
    *   UI remains responsive during processing
*   **Error Handling**:
    *   Comprehensive error detection and user feedback
    *   Graceful handling of API key issues and processing failures
*   **Status Updates**:
    *   Status bar for real-time operation feedback
    *   Clear success/error messaging

### Uses
*   **Interactive AI Development**: Provides developers with a GUI tool for testing and refining AI prompts
*   **Content Enhancement**: Enables users to process and enhance text content through various AI-powered transformations
*   **Agent Development**: Facilitates the creation, testing, and saving of AI agents through a visual interface
*   **Prompt Engineering**: Offers a practical environment for developing and testing different prompt strategies
*   **Educational Tool**: Serves as a learning platform for understanding AI prompt processing and agent interactions
*   **Production Environment**: Can be used as a standalone application for production use of the ForgeOAgent system