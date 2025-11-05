import os
import json
from typing import Dict, List, Any , Optional
from datetime import datetime

class AgentManager:
    """Manages saving and loading of agents."""
    
    def __init__(self, agents_dir: str = f"{os.path.join(os.path.dirname(__file__))}/../../mcp/main_agent_context_previous_conversation"):
        self.agents_dir = agents_dir
        os.makedirs(agents_dir, exist_ok=True)
    
    def save_agent(self, agent_name: str, conversation_id: str, task_ids: List[str] = None) -> bool:
        """Save an agent's conversation history for future reference (only last main agent interaction)."""
        try:
            agent_folder = os.path.join(self.agents_dir, agent_name)
            os.makedirs(agent_folder, exist_ok=True)
            
            # Read the log file and get only the last main agent interaction
            log_file = f"{self.agents_dir}/../../logs/executor/{conversation_id}.jsonl"
            if os.path.exists(log_file):
                last_interaction = None
                
                with open(log_file, 'r', encoding='utf-8') as src:
                    for line in src:
                        try:
                            data = json.loads(line)
                            if data.get('type') == 'interaction' and data.get('success'):
                                last_interaction = data
                        except:
                            continue
                
                if last_interaction:
                    # Save only the last successful interaction to main_agent.jsonl
                    agent_log_file = os.path.join(agent_folder, "main_agent.jsonl")
                    with open(agent_log_file, 'w', encoding='utf-8') as dst:
                        # Write metadata first
                        metadata = {
                            "type": "metadata",
                            "agent_name": agent_name,
                            "conversation_id": conversation_id,
                            "saved_at": datetime.now().isoformat(),
                            "model": "gemini-1.5-flash"
                        }
                        dst.write(json.dumps(metadata, ensure_ascii=False) + "\n")
                        
                        # Write the last interaction
                        dst.write(json.dumps(last_interaction, ensure_ascii=False) + "\n")
                    
                    # Also save individual task agent logs if they exist
                    task_logs_saved = []
                    # if task_ids:
                    #     for task_id in task_ids:
                    #         task_log_file = f"logs/{task_id}.jsonl"
                    #         if os.path.exists(task_log_file):
                    #             # Copy task agent log to agent folder
                    #             task_agent_file = os.path.join(agent_folder, f"{task_id}.jsonl")
                    #             with open(task_log_file, 'r', encoding='utf-8') as src_task:
                    #                 with open(task_agent_file, 'w', encoding='utf-8') as dst_task:
                    #                     for line in src_task:
                    #                         dst_task.write(line)
                    #             task_logs_saved.append(f"{task_id}.jsonl")
                    
                    # Create agent metadata
                    metadata = {
                        "agent_name": agent_name,
                        "conversation_id": conversation_id,
                        "task_ids": task_ids or [],
                        "saved_at": datetime.now().isoformat(),
                        "log_file": "main_agent.jsonl",
                        "task_log_files": task_logs_saved
                    }
                    
                    metadata_file = os.path.join(agent_folder, "metadata.json")
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ Agent '{agent_name}' saved successfully!")
                    print(f"   - Main agent log: main_agent.jsonl")
                    if task_logs_saved:
                        print(f"   - Task agent logs: {', '.join(task_logs_saved)}")
                    return True
                else:
                    print(f"❌ No successful interaction found in log file: {log_file}")
                    return False
            else:
                print(f"❌ Log file not found: {log_file}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to save agent '{agent_name}': {str(e)}")
            return False
    
    def list_executors(self) -> List[Dict[str, Any]]:
        """List all available saved agents."""
        agents = []
        try:
            for agent_name in os.listdir(self.agents_dir):
                agent_folder = os.path.join(self.agents_dir, agent_name)
                if os.path.isdir(agent_folder):
                    metadata_file = os.path.join(agent_folder, "metadata.json")
                    if os.path.exists(metadata_file):
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            agents.append(metadata)
            return agents
        except Exception as e:
            print(f"❌ Failed to list agents: {str(e)}")
            return []
    
    def get_agent_path(self, agent_name: str) -> Optional[str]:
        """Get the path to an agent's folder."""
        agent_folder = os.path.join(self.agents_dir, agent_name)
        if os.path.exists(agent_folder):
            return agent_folder
        return None

    def select_agent_or_create_new(self) -> tuple:
        """Interactive agent selection or creation."""
        agents = self.list_executors()
        
        print("\n🤖 Available Agents:")
        print("=" * 50)
        print("0. Create New Agent")
        
        if agents:
            for i, agent in enumerate(agents, 1):
                print(f"{i}. {agent['agent_name']}")
                print(f"   - Conversation ID: {agent['conversation_id']}")
                print(f"   - Task IDs: {agent.get('task_ids', [])}")
                print(f"   - Task Logs: {agent.get('task_log_files', [])}")
                print(f"   - Saved: {agent['saved_at']}")
                print("-" * 30)
        else:
            print("   No saved agents found.")
        
        print("=" * 50)
        
        try:
            choice = input("Select an agent (number): ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                print("📝 Creating new agent...")
                return None, None
            elif 1 <= choice_num <= len(agents):
                selected_agent = agents[choice_num - 1]
                agent_path = self.get_agent_path(selected_agent['agent_name'])
                print(f"✅ Selected agent: {selected_agent['agent_name']}")
                print(f"   - Will load main agent + {len(selected_agent.get('task_log_files', []))} task agents")
                return selected_agent, agent_path
            else:
                print("❌ Invalid selection. Creating new agent...")
                return None, None
                
        except (ValueError, KeyboardInterrupt):
            print("❌ Invalid input. Creating new agent...")
            return None, None