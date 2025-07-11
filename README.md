# ForgeOAgent

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

> **Intelligent automation for everyone:** Use Gemini and custom agents to improve prompts, enhance text, refine code, generate emails, and automate tasks.

ForgeOAgent is a modular Python framework for building, managing, and running AI agents with advanced code processing capabilities. It automates code improvement, agent management, and client integration using Google Gemini and other APIs.

## 🚀 Features
- Assign shortcuts for instant agent access on any platform
- Save custom prompts to `core/prompts/` and import in `main.py`
- Gemini tasks and results are automatically logged for future reference
- Cross-platform shell support (Windows & Linux)
- Modular agent and client architecture for easy extension

## 📁 Directory Structure
- `main.py` — Entry point for running agents and workflows
- `agents/` — Agent modules and metadata
- `clients/` — API clients for external services (e.g., Gemini)
- `core/` — Core utilities for agent and API key management, configuration, and testing
- `logs/` — JSONL logs of agent activities and improvements
- `shell/` — Shell scripts for Linux and Windows environments

## 🛠️ Getting Started
1. **Clone the repository**
   ```sh
   git clone <repo-url>
   cd ForgeOAgent
   ```
2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure API keys**
   - Copy `.env.production` to `.env` and update your keys.
4. **Run the agent system**
   ```sh
   python main.py
   ```
   - List agents: `python main.py -l`
   - Run with prompt: `python main.py -p <prompt_name> "your prompt here"`
5. **Assign a shortcut for quick access**
   - **Linux:**
     1. Go to Settings > Keyboard Shortcuts > Add Shortcut.
     2. Set the name and script path (e.g., `shell/linux/index.sh`).
   - **Windows:**
     1. Right-click `shell/windows/index.vbs` and select "Send to Desktop (create shortcut)".
     2. On the desktop shortcut, right-click > Properties > set a shortcut key.

## 💡 Usage
- Create or modify agents in `core/prompts/`
- Integrate new clients in `clients/`
- Review logs in `logs/` for agent activity and improvements

### ⚡ Creating Custom Agents & Shortcuts
You can assign `.sh` (shell) or `.vbs` (VBScript) files to shortcuts for instant agent execution.

**To create your own agent:**
1. Add your custom prompt to `core/prompts/` (use the naming convention `*_SYSTEM_INSTRUCTION`).
2. Import your prompt in `main.py`.
3. Create a shortcut script (e.g., `.sh` or `.vbs`) to call the main agent with your prompt type.

Now you can run agents with custom instructions instantly by triggering your shortcut.

#### Example: Improving Code Files
- Recursively process files in a directory (skipping `.git` folders)
- Use Gemini agents to improve code or text based on file extension
- Improved files are saved in the current directory
- See `agents/temp_3/main_agent.jsonl` for a sample agent log and code

## 🤝 Contributing
Contributions are welcome! Please submit issues or pull requests for improvements or new features.

## 📄 License
MIT License