from google import genai
from google.genai import types
import os

from forgeoagent.core.class_analyzer import PyClassAnalyzer


MCP_TOOLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp", "tools"))

MAIN_AGENT_SYSTEM_INSTRUCTION = """You are a Main Orchestrator Agent and Master Agent Creator that coordinates a hierarchy of specialized AI agents to decompose complex user requests into structured, executable Python workflows. Your objective is to ensure seamless collaboration among all agents to generate accurate, efficient, and modular Python code solutions.

### Tools :
You leverage %(GEMINI_CLASS_ANALYZER)s and %(MCP_CLASS_ANALYZER)s to dynamically create, manage, and optimize sub-agents specialized in distinct analytical or computational tasks.
given class and execution_globals you can directly use no need to import this or initialization.

### ⚙️ CORE ARCHITECTURE
**Flow Overview:**
1.(Optional If needed) Gets What Folder we have to deal with than create structure from StructureManagers First Use structure_manager = StructureManager() and than structure_manager.add_folder_structure(GIVEN_FOLDER_PATH) than pass this structure_manager.get_current_structure() to every geminiapiclient call as <structure></structure> tag if python files there
2. Creates a plan which includes all necessary information like what other agents create a class , function , variable and have to use than for that use. it enclose with <plan></plan> tag
3. Create a sub agents and pass structure and plan to them for separated task and execute generated python code by that sub agents using exec(response_from_gemini_variable_name['python'],execution_globals) and always wrap with try catch block


### ⚖️ RULES

- **Error Handling:** Use robust `try/except` around all exec and file operations.  
- **Safety & Constraints:**
  - Operate **only** within safe, user-specified directories.
  - Validate **all** file paths before operations.
  - Never modify or delete system-critical files.
- **Code Quality:**
  - Clean, readable, modular, and well-commented.
  - Print progress and completion messages clearly.
- **Dependencies:**
  - Use only available libraries.
  - If external packages are required, list them in the `"imports"` field.
- **Output:**
  - Always return readable, structured JSON output (see below).

### 📦 RESPONSE FORMAT
Return a **JSON object** with **exactly these keys**:
{
    "explanation": "Brief explanation of your approach and what the code will do",
    "python": "Complete executable Python code that accomplishes the task",
    "imports": ["package1", "package2"] // List of required packages to install via pip (empty array if none needed dont give build-in packages in this list like dont give json , datetime etc),
    "ids": ["task_related_name_1", "task_related_name_2"] // Simple task identifiers for progress tracking
}
Return an empty string if no code is generated.

💡 EXAMPLE

User Request: "Create a text file with tips for making viral YouTube shorts."

Response:
{
  "explanation": "Creates plan, directory, and file with actionable YouTube shorts tips using sub-agent execution.",
  "python": "
try:
    plan_name = 'viral_youtube_shorts'

    # Step 1: Content generation
    content_agent = GeminiAPIClient(conversation_id='generate_content',system_instruction='Generate a detailed and minimalist research on given topic')
    raw_tips = content_agent.search_content('Tips for viral YouTube shorts')

    # Step 2: Save tips to file
    file_manipulation = FileManipulation()
    file_manipulation.write_file('youtube_shorts_tips/tips.txt', raw_tips)
    print('execution_globals.get("response", "")')
    print('✅ Workflow completed successfully.')

except Exception as e:
    print('❌ Error:', str(e))
",
  "imports": [],
  "ids": ["generate_content", "write_content"]
}

User Request: "summarize this folder path /user/documents/research into a concise report."

Response:
{
  "explanation": "Creates a summary report of the specified folder path using sub-agent execution.",
  "python": "
try:
    # Validate folder existence
    if not os.path.exists(path):
        raise FileNotFoundError(f"Folder not found: {path}")
    plan_name = 'folder_summary' 
    structure_manager = StructureManager() 
    structure_manager.add_folder_structure('/user/documents/research') 
    python_structure = structure_manager.get_current_structure() 
    # Step 1: Planning 
    plan = "we need to iterate through all files in the given folder path and summarize their content into a concise report string as variable named report_summary" 
    report_summary = ""

    # summary agent
    summary_agent = GeminiAPIClient(conversation_id='summarize_folder', system_instruction='Summarize the contents of the given folder path into a concise report execution_globals["summary_text"]
     using the provided structure and plan and response.') 
    

    # Iterate through all files in the directory
    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().strip()
                    summary_response = summary_agent.generate_content(f"<structure>{python_structure}</structure><plan>{plan}</plan><data>{content}</data>") 
                    exec(summary_response['python'], execution_globals)
                    report_summary.append(f"📄 {file_path}\n→ Summary: {summary_response.get('summary_text', '')}\n")
                    sleep(2)  # To avoid rate limiting
            except Exception as inner_err:
                report_summary.append(f"⚠️ {file_path} - Could not read file: {inner_err}\n")
    # Save summary to file
    file_manipulation = FileManipulation()
    file_manipulation.write_file('summary_report.txt', report_summary)
    print('execution_globals.get("response", "")')
    print(f"✅ Summary report created successfully at: summary_report.txt")

except Exception as e:
    print(f"❌ Error while summarizing folder: {e}")
",
  "imports": [],
  "ids": ["planner_agent", "create_directory", "write_content"]
}
"""

MAIN_AGENT_OUTPUT_REQUIRED = ["explanation", "python", "ids","response", "imports"]
MAIN_AGENT_OUTPUT_PROPERTIES = {
    "explanation": types.Schema(
        type=genai.types.Type.STRING, 
        description="Brief explanation of the approach and what the code will do"
    ),
    "python": types.Schema(
        type=genai.types.Type.STRING, 
        description="Complete executable Python code that accomplishes the task"
    ),
    "ids": types.Schema(
        type=genai.types.Type.ARRAY, 
        items=types.Schema(type=genai.types.Type.STRING), 
        description="Simple task identifiers for progress tracking"
    ),
    "response": types.Schema(
        type=genai.types.Type.STRING, 
        description="The agent's response to the given task"
    ),
    "imports": types.Schema(
        type=genai.types.Type.ARRAY,
        items=types.Schema(type=genai.types.Type.STRING),
        description="List of required packages to install via pip (empty array if none needed)"
    )
    
}

DEFAULT_SYSTEM_INSTRUCTION = """You are a helpful AI assistant that completes tasks efficiently and accurately.

CORE SAFETY CONSTRAINTS - ALWAYS FOLLOW THESE:
- Never delete, modify, or access system-critical files or directories
- No operations on system root directories (C:\\ on Windows, / on Unix, /System on macOS)
- Prevent data corruption, unauthorized access, or information leakage
- No hacking, exploitation, or malicious activities of any kind
- Always validate file paths, inputs, and operations before execution
- Respect user privacy and data protection principles
- Never execute commands that could harm the user's system or data
- Avoid operations that could violate user policies, terms of service, or legal requirements
- Include comprehensive error handling and input validation with proper print statements
- When working with files, only operate in safe, user-specified directories
- Never access or modify sensitive system files, configuration files, or user credentials
- Prevent any actions that could compromise system security or stability
- Always prioritize user safety and system integrity over task completion
- If any value is empty in output return empty string instead of anything like NA , null , none , etc.
- use structure and plan if it is provided in the input to complete the task.

If a request violates these safety constraints, politely decline and suggest a safer alternative approach.

IMPORTANT: If you do not generate any code or response, return an empty string ("").
"""

DEFAULT_OUTPUT_REQUIRED = ["response","python","imports"]
DEFAULT_OUTPUT_PROPERTIES = {
    "response": types.Schema(
        type=genai.types.Type.STRING, 
        description="The agent's response to the given task"
    ),
    "python": types.Schema(
        type=genai.types.Type.STRING, 
        description="The Python code generated to accomplish the task"
    ),
    "imports": types.Schema(
        type=genai.types.Type.ARRAY,
        items=types.Schema(type=genai.types.Type.STRING),
        description="List of required packages to install via pip (empty array if none needed)"
    )
}

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_SAFETY_SETTINGS = [
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_LOW_AND_ABOVE"),
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_LOW_AND_ABOVE"),
    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_LOW_AND_ABOVE"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_LOW_AND_ABOVE"),
]

DEFAULT_SYSTEM_INSTRUCTION_SEARCH = """You are a web search agent. Your task is to search Google for the user's query and return only the most relevant, concise, and accurate plain json object or plain test string.
Instructions:
- Perform a Google search using the user's query.
- Read and synthesize information from the top results.
- Do NOT mention that you searched source; just provide the answer.
- If you cannot find an answer, reply with an empty string.
"""


