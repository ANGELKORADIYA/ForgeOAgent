import os
import json
import ast
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

class StructureManager:
    """
    Simple structure management system for storing folder/file structure metadata
    """
    
    def __init__(self):
        """
        Initialize StructureManager with a single JSON files
        """
        memory_file = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.json")
        self.memory_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "../../logs/structures"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_file = self.memory_dir / memory_file
        self.structure = self._load_structure()
    
    def _load_structure(self) -> Dict[str, Any]:
        """Load existing structure from file or create new one"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading structure: {e}")
                return {}
        else:
            return {}
    
    def _save_structure(self) -> bool:
        """Save current structure to file"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.structure, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving structure: {e}")
            return False
    
    def parse_python_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a Python file and extract metadata
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary with imports, variables, functions, and classes
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            metadata = {
                "imports": {},
                "variables": [],
                "functions": {},
                "classes": {}
            }
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        metadata["imports"][alias.name] = None
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        metadata["imports"][alias.name] = module
            
            # Extract top-level nodes
            for node in tree.body:
                # Variables (assignments)
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            metadata["variables"].append(target.id)
                
                # Functions
                elif isinstance(node, ast.FunctionDef):
                    func_data = self._parse_function(node)
                    metadata["functions"][node.name] = func_data
                
                # Classes
                elif isinstance(node, ast.ClassDef):
                    class_data = self._parse_class(node)
                    metadata["classes"][node.name] = class_data
            
            return metadata
            
        except Exception as e:
            print(f"Error parsing Python file {file_path}: {e}")
            return {
                "imports": {},
                "variables": [],
                "functions": {},
                "classes": {}
            }
    
    def _parse_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Parse a function definition"""
        func_data = {
            "args": [],
            "return_type": "None",
            "doc": ast.get_docstring(node) or "",
            "description": ""  # Placeholder for API call response
        }
        
        # Parse arguments
        for arg in node.args.args:
            arg_info = {"name": arg.arg}
            if arg.annotation:
                arg_info["type"] = ast.unparse(arg.annotation)
            else:
                arg_info["type"] = "Any"
            func_data["args"].append(arg_info)
        
        # Parse return type
        if node.returns:
            func_data["return_type"] = ast.unparse(node.returns)
        
        return func_data
    
    def _parse_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Parse a class definition"""
        class_data = {
            "doc": ast.get_docstring(node) or "",
            "self_variables": [],
            "self_functions": {}
        }
        
        # Parse class body
        for item in node.body:
            # Methods
            if isinstance(item, ast.FunctionDef):
                method_data = self._parse_function(item)
                class_data["self_functions"][item.name] = method_data
            
            # Assignments (self.variable)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == "self":
                            var_name = f"self.{target.attr}"
                            if var_name not in class_data["self_variables"]:
                                class_data["self_variables"].append(var_name)
        
        # Also check __init__ for self variables
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                for stmt in ast.walk(item):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Attribute):
                                if isinstance(target.value, ast.Name) and target.value.id == "self":
                                    var_name = f"self.{target.attr}"
                                    if var_name not in class_data["self_variables"]:
                                        class_data["self_variables"].append(var_name)
        
        return class_data
    
    def _scan_folder(self, folder_path: Path) -> Dict[str, Any]:
        """
        Recursively scan a folder and build structure
        
        Args:
            folder_path: Path object of the folder to scan
            
        Returns:
            Dictionary with folders and files
        """
        structure = {
            "folders": {},
            "files": {}
        }
        
        try:
            # List all items in the folder
            for item in folder_path.iterdir():
                if item.name in ('__pycache__', '.venv','logs','.git','.vscode'):
                    continue
                if item.is_dir():
                    # Recursively scan subdirectories
                    structure["folders"][item.name] = self._scan_folder(item)
                
                elif item.is_file():
                    if item.suffix == ".py":
                        # Parse Python files
                        structure["files"][item.name] = self.parse_python_file(item)
                    else:
                        # For non-Python files, just store empty metadata
                        structure["files"][item.name] = {}
            
            return structure
            
        except Exception as e:
            print(f"Error scanning folder {folder_path}: {e}")
            return structure
    
    def add_folder_structure(self, folder_path: str) -> bool:
        """
        Scan a folder and add its complete structure to memory
        
        Args:
            folder_path: Absolute path to the folder to scan
            
        Returns:
            bool: Success status
        """
        try:
            path = Path(folder_path).resolve()
            
            if not path.exists():
                print(f"Path does not exist: {folder_path}")
                return False
            
            if not path.is_dir():
                print(f"Path is not a directory: {folder_path}")
                return False
            
            # Get absolute path as string
            abs_path = str(path)
            
            # Scan the folder
            folder_structure = self._scan_folder(path)
            
            # Store with absolute path as key
            self.structure[abs_path] = folder_structure
            
            return self._save_structure()
            
        except Exception as e:
            print(f"Error adding folder structure: {e}")
            return False
    
    def get_all_stored_paths(self) -> List[str]:
        """Get list of all stored folder paths"""
        return list(self.structure.keys())
    
    def clear_structure(self) -> bool:
        """Clear all stored structure"""
        self.structure = {}
        return self._save_structure()
    
    def _export_structure(self, output_file: str) -> bool:
        """
        Export structure to a different file
        
        Args:
            output_file: Path to export file
            
        Returns:
            bool: Success status
        """
        try:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.structure, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting structure: {e}")
            return False

    def get_current_structure(self) -> Dict[str, Any]:
        """Get the current structure"""
        return self.structure

if __name__ == "__main__":
    memory_manager = StructureManager()
    memory_manager.add_folder_structure("/home/userpc/Desktop/29/ForgeOAgent/controller")
