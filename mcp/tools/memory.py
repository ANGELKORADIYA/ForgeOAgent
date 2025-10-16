import os
import json
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import threading
import uuid

class MemoryManager:
    """
    Comprehensive memory management system for storing metadata, plans, and cross-agent communication
    """
    
    def __init__(self):
        self.memory_dir = Path(os.path.dirname(os.path.abspath(__file__))+"/../../logs/memory")
        self.lock = threading.Lock()
        self._ensure_directory_structure()
        
    def _ensure_directory_structure(self):
        """Create necessary directory structure"""
        directories = [
            self.memory_dir,
            self.memory_dir / "classes",
            self.memory_dir / "functions", 
            self.memory_dir / "variables",
            self.memory_dir / "metadata",
            self.memory_dir / "agents",
            self.memory_dir / "plans",
            self.memory_dir / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    # ================== CORE MEMORY OPERATIONS ==================
    
    def store_memory(self, category: str, key: str, data: Dict[str, Any]) -> bool:
        """Store memory data in specified category"""
        try:
            with self.lock:
                file_path = self.memory_dir / category / f"{key}.json"
                
                # Add timestamp and metadata
                memory_data = {
                    "id": str(uuid.uuid4()),
                    "key": key,
                    "category": category,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "data": data
                }
                
                with open(file_path, 'w') as f:
                    json.dump(memory_data, f, indent=2)
                
                self._log_operation("STORE", category, key)
                return True
                
        except Exception as e:
            self._log_error(f"Failed to store memory: {e}")
            return False
    
    def retrieve_memory(self, category: str, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve memory data from specified category"""
        try:
            file_path = self.memory_dir / category / f"{key}.json"
            
            if not file_path.exists():
                return None
                
            with open(file_path, 'r') as f:
                memory_data = json.load(f)
                
            self._log_operation("RETRIEVE", category, key)
            return memory_data
            
        except Exception as e:
            self._log_error(f"Failed to retrieve memory: {e}")
            return None
    
    def list_memories(self, category: str) -> List[str]:
        """List all memory keys in a category"""
        try:
            category_path = self.memory_dir / category
            if not category_path.exists():
                return []
                
            return [f.stem for f in category_path.glob("*.json")]
            
        except Exception as e:
            self._log_error(f"Failed to list memories: {e}")
            return []
    
    def delete_memory(self, category: str, key: str) -> bool:
        """Delete memory from specified category"""
        try:
            with self.lock:
                file_path = self.memory_dir / category / f"{key}.json"
                
                if file_path.exists():
                    file_path.unlink()
                    self._log_operation("DELETE", category, key)
                    return True
                return False
                
        except Exception as e:
            self._log_error(f"Failed to delete memory: {e}")
            return False
    
    # ================== CLASS STRUCTURE MEMORY ==================
    
    def store_class_structure(self, class_name: str, structure: Dict[str, Any]) -> bool:
        """Store class structure metadata"""
        class_data = {
            "name": class_name,
            "methods": structure.get("methods", []),
            "attributes": structure.get("attributes", []),
            "inheritance": structure.get("inheritance", []),
            "docstring": structure.get("docstring", ""),
            "file_path": structure.get("file_path", ""),
            "line_number": structure.get("line_number", 0)
        }
        
        return self.store_memory("classes", class_name, class_data)
    
    def get_class_structure(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve class structure metadata"""
        memory = self.retrieve_memory("classes", class_name)
        return memory["data"] if memory else None
    
    # ================== FUNCTION STRUCTURE MEMORY ==================
    
    def store_function_structure(self, function_name: str, structure: Dict[str, Any]) -> bool:
        """Store function structure metadata"""
        function_data = {
            "name": function_name,
            "parameters": structure.get("parameters", []),
            "return_type": structure.get("return_type", ""),
            "docstring": structure.get("docstring", ""),
            "decorators": structure.get("decorators", []),
            "file_path": structure.get("file_path", ""),
            "line_number": structure.get("line_number", 0),
            "complexity": structure.get("complexity", "low")
        }
        
        return self.store_memory("functions", function_name, function_data)
    
    def get_function_structure(self, function_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve function structure metadata"""
        memory = self.retrieve_memory("functions", function_name)
        return memory["data"] if memory else None
    
    # ================== VARIABLE MEMORY ==================
    
    def store_variable_info(self, variable_name: str, info: Dict[str, Any]) -> bool:
        """Store variable metadata"""
        variable_data = {
            "name": variable_name,
            "type": info.get("type", ""),
            "scope": info.get("scope", "local"),
            "value": info.get("value", None),
            "description": info.get("description", ""),
            "file_path": info.get("file_path", ""),
            "line_number": info.get("line_number", 0)
        }
        
        return self.store_memory("variables", variable_name, variable_data)
    
    def get_variable_info(self, variable_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve variable metadata"""
        memory = self.retrieve_memory("variables", variable_name)
        return memory["data"] if memory else None
    
    # ================== PLAN MANAGEMENT ==================
    
    def create_plan(self, plan_name: str, plan_data: Dict[str, Any]) -> bool:
        """Create or update a plan file"""
        try:
            plan_path = self.memory_dir / "plans" / f"{plan_name}.txt"
            
            # Create structured plan content
            plan_content = self._format_plan(plan_data)
            
            with open(plan_path, 'w') as f:
                f.write(plan_content)
            
            # Also store as JSON for programmatic access
            self.store_memory("plans", plan_name, plan_data)
            
            self._log_operation("CREATE_PLAN", "plans", plan_name)
            return True
            
        except Exception as e:
            self._log_error(f"Failed to create plan: {e}")
            return False
    
    def read_plan(self, plan_name: str = "plan") -> Optional[str]:
        """Read plan content from plan.txt or specified plan"""
        try:
            plan_path = self.memory_dir / "plans" / f"{plan_name}.txt"
            
            if not plan_path.exists():
                return None
                
            with open(plan_path, 'r') as f:
                content = f.read()
                
            self._log_operation("READ_PLAN", "plans", plan_name)
            return content
            
        except Exception as e:
            self._log_error(f"Failed to read plan: {e}")
            return None
    
    def update_plan_status(self, plan_name: str, task_id: str, status: str) -> bool:
        """Update status of specific task in plan"""
        try:
            plan_data = self.retrieve_memory("plans", plan_name)
            if not plan_data:
                return False
            
            # Update task status
            tasks = plan_data["data"].get("tasks", [])
            for task in tasks:
                if task.get("id") == task_id:
                    task["status"] = status
                    task["updated"] = datetime.datetime.now().isoformat()
                    break
            
            # Save updated plan
            self.store_memory("plans", plan_name, plan_data["data"])
            
            # Update text file
            plan_content = self._format_plan(plan_data["data"])
            plan_path = self.memory_dir / "plans" / f"{plan_name}.txt"
            with open(plan_path, 'w') as f:
                f.write(plan_content)
            
            return True
            
        except Exception as e:
            self._log_error(f"Failed to update plan status: {e}")
            return False
    
    # ================== CROSS-AGENT COMMUNICATION ==================
    
    def send_message_to_agent(self, from_agent: str, to_agent: str, message: Dict[str, Any]) -> bool:
        """Send message from one agent to another"""
        try:
            message_data = {
                "from": from_agent,
                "to": to_agent,
                "message": message,
                "timestamp": datetime.datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "status": "sent"
            }
            
            # Store in sender's outbox
            outbox_key = f"{from_agent}_to_{to_agent}_{message_data['id']}"
            self.store_memory("agents", f"outbox_{outbox_key}", message_data)
            
            # Store in receiver's inbox
            self.store_memory("agents", f"inbox_{to_agent}_{message_data['id']}", message_data)
            
            self._log_operation("SEND_MESSAGE", "agents", f"{from_agent} -> {to_agent}")
            return True
            
        except Exception as e:
            self._log_error(f"Failed to send message: {e}")
            return False
    
    def get_messages_for_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get all messages for specific agent"""
        try:
            agent_files = self.list_memories("agents")
            messages = []
            
            for file_name in agent_files:
                if f"inbox_{agent_name}_" in file_name:
                    message = self.retrieve_memory("agents", file_name)
                    if message:
                        messages.append(message["data"])
            
            # Sort by timestamp
            messages.sort(key=lambda x: x["timestamp"])
            
            return messages
            
        except Exception as e:
            self._log_error(f"Failed to get messages: {e}")
            return []
    
    def mark_message_read(self, agent_name: str, message_id: str) -> bool:
        """Mark message as read"""
        try:
            # Find and update message
            agent_files = self.list_memories("agents")
            
            for file_name in agent_files:
                if f"inbox_{agent_name}_" in file_name and message_id in file_name:
                    message = self.retrieve_memory("agents", file_name)
                    if message:
                        message["data"]["status"] = "read"
                        message["data"]["read_timestamp"] = datetime.datetime.now().isoformat()
                        self.store_memory("agents", file_name, message["data"])
                        return True
            
            return False
            
        except Exception as e:
            self._log_error(f"Failed to mark message read: {e}")
            return False
    
    # ================== UTILITY METHODS ==================
    
    def _format_plan(self, plan_data: Dict[str, Any]) -> str:
        """Format plan data into readable text"""
        content = []
        content.append(f"PLAN: {plan_data.get('name', 'Untitled')}")
        content.append(f"CREATED: {plan_data.get('created', datetime.datetime.now().isoformat())}")
        content.append(f"DESCRIPTION: {plan_data.get('description', '')}")
        content.append("\n" + "="*50 + "\n")
        
        tasks = plan_data.get('tasks', [])
        for i, task in enumerate(tasks, 1):
            status = task.get('status', 'pending').upper()
            content.append(f"{i}. [{status}] {task.get('title', '')}")
            if task.get('description'):
                content.append(f"   Description: {task['description']}")
            if task.get('dependencies'):
                content.append(f"   Dependencies: {', '.join(task['dependencies'])}")
            content.append("")
        
        return "\n".join(content)
    
    def _log_operation(self, operation: str, category: str, key: str):
        """Log memory operations"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "operation": operation,
            "category": category,
            "key": key
        }
        
        log_file = self.memory_dir / "logs" / f"operations_{datetime.date.today()}.json"
        
        # Append to daily log
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _log_error(self, error_message: str):
        """Log errors"""
        error_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "error": error_message
        }
        
        error_file = self.memory_dir / "logs" / f"errors_{datetime.date.today()}.json"
        
        errors = []
        if error_file.exists():
            try:
                with open(error_file, 'r') as f:
                    errors = json.load(f)
            except:
                errors = []
        
        errors.append(error_entry)
        
        with open(error_file, 'w') as f:
            json.dump(errors, f, indent=2)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        stats = {
            "total_memories": 0,
            "categories": {},
            "disk_usage": 0
        }
        
        for category in ["classes", "functions", "variables", "metadata", "agents", "plans"]:
            category_path = self.memory_dir / category
            if category_path.exists():
                files = list(category_path.glob("*.json"))
                stats["categories"][category] = len(files)
                stats["total_memories"] += len(files)
                
                # Calculate disk usage
                for file in files:
                    stats["disk_usage"] += file.stat().st_size
        return stats
    
    def cleanup_old_memories(self, days_old: int = 30) -> int:
        """Clean up memories older than specified days"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
        cleaned_count = 0
        
        for category in ["classes", "functions", "variables", "metadata", "agents", "plans"]:
            category_path = self.memory_dir / category
            if not category_path.exists():
                continue
                
            for file in category_path.glob("*.json"):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    
                    file_date = datetime.datetime.fromisoformat(data["timestamp"])
                    if file_date < cutoff_date:
                        file.unlink()
                        cleaned_count += 1
                        
                except Exception as e:
                    self._log_error(f"Failed to cleanup {file}: {e}")
        
        return cleaned_count


# ================== USAGE EXAMPLE ==================

def example_usage():
    """Example of how to use the MemoryManager"""
    
    # Initialize memory manager
    memory = MemoryManager()
    
    # Store class structure
    class_info = {
        "methods": ["__init__", "process_data", "save_results"],
        "attributes": ["data", "config", "results"],
        "inheritance": ["BaseProcessor"],
        "docstring": "Data processing class",
        "file_path": "/src/processor.py",
        "line_number": 15
    }
    memory.store_class_structure("DataProcessor", class_info)
    
    # Store function structure
    func_info = {
        "parameters": ["data: List[str]", "config: Dict"],
        "return_type": "bool",
        "docstring": "Process input data according to config",
        "decorators": ["@staticmethod"],
        "file_path": "/src/utils.py",
        "line_number": 42
    }
    memory.store_function_structure("process_data", func_info)
    
    # Create a plan
    plan = {
        "name": "Data Processing Pipeline",
        "description": "Process and analyze customer data",
        "created": datetime.datetime.now().isoformat(),
        "tasks": [
            {
                "id": "task_1",
                "title": "Load data from database",
                "description": "Connect and extract customer records",
                "status": "pending",
                "dependencies": []
            },
            {
                "id": "task_2", 
                "title": "Clean and validate data",
                "description": "Remove duplicates and validate formats",
                "status": "pending",
                "dependencies": ["task_1"]
            }
        ]
    }
    memory.create_plan("main_plan", plan)
    
    # Cross-agent communication
    message = {
        "type": "task_assignment",
        "task": "data_validation",
        "priority": "high",
        "details": "Validate customer email formats"
    }
    memory.send_message_to_agent("coordinator", "validator", message)
    
    # Read plan
    plan_content = memory.read_plan("main_plan")
    print("Current Plan:")
    print(plan_content)
    
    # Get memory stats
    stats = memory.get_memory_stats()
    print(f"\nMemory Stats: {stats}")

if __name__ == "__main__":
    example_usage()
