# ForgeOAgent

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

> **Intelligent automation for everyone:**  
> Use Gemini, OpenAI, Anthropic, or Ollama to power custom agents to improve prompts, enhance text, refine code, generate emails, and automate tasks safely.

ForgeOAgent is a modular Python framework for building, managing, and running AI agents with advanced code processing capabilities. It coordinates complex tasks using a state-machine orchestrator featuring secure auto-pausing for task approvals.

---

## 🚀 Key Features

- **Multi-Provider Support:** Easily switch between Gemini, OpenAI, Anthropic, and local Ollama.
- **Robust Execution Engine:** A safe, state-machine driven orchestrator that auto-pauses for human approval on high-risk filesystem and shell operations.
- **Flexible agent modes:**  
  - *Inquirer Mode*: Instant execution of system prompts for quick generation tasks.  
  - *Executor Mode*: Deep agent workflows that dynamically decompose tasks, use tools, and execute Python code.
- **Customizable prompts:** Easily add your own system instructions as Python modules in `forgeoagent/tools/system_prompts/`.
- **Fast Desktop Launcher:** A lightweight, spotlight-style GUI to instantly trigger tasks from your system tray.

---

## 📁 Project Structure

- `forgeoagent/cli/main.py` — Command-line interface for running agents and commands.
- `forgeoagent/gui/app.py` — Entry point for the fast, lightweight desktop launcher.
- `forgeoagent/web/main.py` — Fast API web server interface.
- `forgeoagent/providers/` — Adapter interfaces for Gemini, OpenAI, Anthropic, and Ollama.
- `forgeoagent/orchestration/` — Auto-pausing execution engine and state machine checkpoints.
- `forgeoagent/tools/` — Modular system prompts (`system_prompts/`) and external integrations (`implementations/`).
- `forgeoagent/config/settings.py` — Pydantic typed application settings.

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
   - Copy `.env.production` (or create `.env`) and add your respective `GEMINI_API_KEYS`, `OPENAI_API_KEY` etc.

4. **Run locally using Python**
   - Launching the new GUI:
     ```sh
     python forgeoagent/gui/app.py
     ```
   - Using the CLI:
     ```sh
     python forgeoagent/cli/main.py
     ```

5. **Building the Windows Executable (.exe)**
   - Run the PowerShell build script:
     ```powershell
     .\scripts\build_windows.ps1
     ```
   - The compiled app will be placed in the `dist/` directory.

---

## ⚠️ Troubleshooting: Windows Smart App Control (.exe Blocked)

When you compile ForgeOAgent using PyInstaller (via `build_windows.ps1`) and try to run the `.exe`, you might encounter a blue **Smart App Control** window stating:
> *"Smart App Control blocked an app that may be unsafe... because we can't confirm who wrote it."*

This is a common security feature on Windows 11 designed to block **unsigned executables** created by packaging tools like PyInstaller. Because the `.exe` doesn't have a publisher certificate, Windows treats it suspiciously.

### Solutions:
**Option 1: Run via Python (Recommended for Development)**
Avoid the `.exe` entirely and run the app straight from source using your python environment:
```sh
python forgeoagent/gui/app.py
```

**Option 2: Add a Folder Exclusion**
You can whitelist the folder where your `.exe` is located from Windows Security to bypass the check.
1. Open **Windows Security** > **Virus & threat protection**.
2. Click **Manage settings** under *Virus & threat protection settings*.
3. Scroll down to **Exclusions** and click **Add or remove exclusions**.
4. Click **Add an exclusion** -> **Folder** and select the `ForgeOAgent/dist` folder.

**Option 3: Disable Smart App Control (Not Recommended)**
You can turn off Smart App Control globally in Windows Security, but this lowers your system's overall protection against malware across the board.

*(Note: To permanently fix this warning for public distribution, the `.exe` must be cryptographically signed using a paid Code-Signing Certificate from a Trusted Certificate Authority).*

---

## ⚙️ Customization

- **Add new system prompts:** Place your custom prompt as a Python constant in `forgeoagent/tools/system_prompts/`.
- **Integrate new clients:** Add API adapters in `forgeoagent/providers/` and register them in `forgeoagent/providers/registry.py`.
- **Review logs:** OS-agnostic logs are securely stored in `%LOCALAPPDATA%/ForgeOAgent/logs/` on Windows.

---

## 🤝 Contributing

Contributions are welcome! Please submit issues or pull requests for improvements or new features.

---

## 📄 License

MIT License