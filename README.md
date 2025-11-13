# ForgeOAgent

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

> **Intelligent automation for everyone:**  
> Use Gemini and custom agents to improve prompts, enhance text, refine code, generate emails, and automate tasks.

ForgeOAgent is a modular Python framework for building, managing, and running AI agents with advanced code processing capabilities. It automates code improvement, agent management, and client integration using Google Gemini and other APIs.

---

## 🚀 Key Features

- **Cross-platform shell support:** Works on Windows & Linux.
- **Flexible agent modes:**  
	- *Inquirer Mode*: Use system prompts for quick tasks.  
	- *Executor Mode*: Advanced workflows, agent management, and context-aware automation.
- **Customizable prompts:** Easily add your own system instructions for new agent behaviors in `mcp/system_prompts/`
- **Persistent chat history:** Optionally load recent conversations for better context and accuracy.
- **Automatic tool integration:** Place Python classes in `mcp/tools` to auto-expose new agent capabilities.
- **Comprehensive logging:** All agent activities and improvements are logged for review.

---

## 📁 Project Structure

- `start.py` — GUI entry point for the agent system.
- `main.py` — Command-line entry point for running agents and workflows.
- `agents/` — Agent modules and metadata.
- `clients/` — API clients for external services (e.g., Gemini).
- `core/` — Core utilities for agent management, API keys, configuration, and more.
- `logs/` — JSONL logs of agent activities and improvements.
- `shell/` — Shell scripts for Linux and Windows environments.
- `mcp/` — System prompts, agent context, and tools for modular extension.


> UseFul :
- GeminiAPIClient().generate_content
- GeminiAPIClient().search_content
- from forgeoagent.controller.executor_controller import create_master_executor

> use :

- from forgeoagent.controller.executor_controller import print_available_executors , save_last_executor
- from forgeoagent.controller.inquirer_controller import inquirer_using_selected_system_instructions , print_available_inquirers , auto_import_inquirers

---

## 🛠️ Getting Started

1. **Clone the repository**
	 ```sh
	 git clone https://github.com/ANGELKORADIYA/ForgeOAgent.git
	 cd ForgeOAgent
	 ```

2. **Install dependencies**
	 ```sh
	 pip install -r requirements.txt
	 ```

3. **Configure API keys**
	 - Copy `.env.production` to `.env` and add your Gemini API keys.

4. **Run the agent system**
	 ```sh
	 python main.py
	 ```
	 - List available system prompts:  
		 `python main.py -l`
	 - Run with a specific prompt:  
		 `python main.py -p <prompt_type> "your prompt here"`
	 - Use main mode (with agent context):  
		 `python main.py "your prompt here" --main`

5. **Assign a shortcut for quick access**
	 - **Linux:**  
		 Add a keyboard shortcut to run `shell/linux/start.sh`.
	 - **Windows:**  
		 Create a desktop shortcut to `shell/windows/start.vbs`.

---

## 💡 Usage Examples

- **Quick prompt improvement:**  
	Use Inquirer Mode to enhance text, code, or emails with a single command.
- **Context-aware automation:**  
	Use Executor Mode to leverage previous conversations and agent context for more complex tasks.


---

## ⚙️ Customization

- **Add new system prompts:**  
	Place your custom prompt as a Python constant in `mcp/system_prompts/` (naming: `*_SYSTEM_INSTRUCTION`).
- **Integrate new clients:**  
	Add API clients in `clients/`.
- **Review logs:**  
	Check `logs/` for detailed agent activity and improvements.
- **Main Agent Reuse:**
   Save Result
---

## 🧩 Creating Custom Agents & Shortcuts

1. **Add your prompt:**  
	 Create a new file in `mcp/system_prompts/` and define a constant ending with `_SYSTEM_INSTRUCTION`.
2. **Create a shortcut script:**  
	 Use `.sh` (Linux) or `.vbs` (Windows) to call the agent with your prompt type.

Now you can trigger your custom agent instantly via your shortcut.

---

## 📝 Example: Improving Code Files

- Recursively process files in a directory (skipping `.git`).
- Use Gemini agents to improve code or text based on file extension.
- Improved files are saved in the current directory.
- See `agents/temp_3/main_agent.jsonl` for a sample agent log and code.

---

## 🤝 Contributing

Contributions are welcome! Please submit issues or pull requests for improvements or new features.

---

## 📄 License

MIT License