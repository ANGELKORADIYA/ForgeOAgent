import os
import ast
import json
from typing import Dict, List, Any, Union, Optional
import importlib.util

class PyClassAnalyzer:
    @staticmethod
    def _get_annotation_type(annotation: Optional[ast.expr]) -> str:
        if annotation is None:
            return "any"
        try:
            return ast.unparse(annotation)  # Python 3.9+
        except Exception:
            return "any"

    @staticmethod
    def _analyze_class_def(class_def: ast.ClassDef) -> Dict[str, Union[List[Dict[str, str]], Dict[str, Dict[str, Any]]]]:
        result: Dict[str, Union[List[Dict[str, str]], Dict[str, Dict[str, Any]]]] = {
            "variables": [],
            "methods": {}
        }

        try:
            for node in class_def.body:
                # ✅ Skip methods starting with underscore
                if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    params: List[Dict[str, str]] = []
                    for arg in node.args.args:
                        param_name = arg.arg
                        param_type = PyClassAnalyzer._get_annotation_type(arg.annotation)
                        params.append({param_name: param_type})

                    doc: str = ast.get_docstring(node) or ""
                    return_type = PyClassAnalyzer._get_annotation_type(node.returns)

                    result["methods"][node.name] = {
                        "doc": doc,
                        "param": params,
                        "return_type": return_type
                    }

                # ✅ Skip class variables starting with underscore
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and not target.id.startswith("_"):
                            result["variables"].append({
                                target.id: ast.dump(node.value)
                            })
        except Exception as e:
            print(f"  [!] Error analyzing class {class_def.name}: {e}")
        return result

    @staticmethod
    def _analyze_file(file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source: str = f.read()
            tree: ast.AST = ast.parse(source, filename=file_path)
        except Exception as e:
            print(f"[!] Error parsing file {file_path}: {e}")
            return {}

        class_data: Dict[str, Any] = {}
        try:
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    class_data[node.name] = PyClassAnalyzer._analyze_class_def(node)
        except Exception as e:
            print(f"[!] Error walking AST in file {file_path}: {e}")
        return class_data

    @classmethod
    def analyze_dir(cls, target_dir: str,is_json:bool = False) -> Dict[str, Any]:
        final_output: Dict[str, Any] = {}

        if not os.path.isdir(target_dir):
            print(f"[!] Provided path is not a directory: {target_dir}")
            return {}

        for filename in os.listdir(target_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                file_path = os.path.join(target_dir, filename)

                if not os.path.isfile(file_path):
                    print(f"[!] Skipping non-file: {file_path}")
                    continue

                print(f"[+] Processing: {filename}")
                try:
                    class_data = cls._analyze_file(file_path)
                    if not class_data:
                        print(f"  [-] No classes found in {filename}")
                    else:
                        final_output.update(class_data)
                except Exception as e:
                    print(f"[!] Error processing {filename}: {e}")
        if is_json:
            return final_output
        return json.dumps(final_output, indent=4)

    @classmethod
    def get_all_classes(cls, target_dir: str) -> Dict[str, Any]:
        """
        Analyze all .py files in the target_dir and return a dict of {class_name: class_reference}.
        """
        class_map = {}
        analysis_result = cls.analyze_dir(target_dir, is_json=True)

        for class_name in analysis_result:
            for filename in os.listdir(target_dir):
                if not filename.endswith(".py") or filename.startswith("__"):
                    continue
                file_path = os.path.join(target_dir, filename)
                module_name = os.path.splitext(filename)[0]

                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if not spec or not spec.loader:
                        continue
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    if hasattr(module, class_name):
                        class_obj = getattr(module, class_name)
                        class_map[class_name] = class_obj
                        break  # Found the class, no need to check further files
                except Exception as e:
                    print(f"[!] Failed to load {class_name} from {filename}: {e}")

        return class_map
    