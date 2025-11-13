import os

class FileManipulation:
    """Use This Class when file write and read must use this only"""
    
    def __init__(self):
        self.base_dir =  f"{os.path.dirname(os.path.abspath(__file__))}/../../logs/base_dir"
        os.makedirs(self.base_dir, exist_ok=True)

    def write_file(self,path: str, data: str) -> str:
        """
        Write data to specified path and data must passed as seperated string
        Args:
            path : either absolute path or relative path. relative path store in  
            data : what u want to store
        """
        try:
            # Construct full file path
            full_path = os.path.join(self.base_dir, path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write data to file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(data)
            
            return full_path
        
        except Exception as e:
            raise Exception(f"Failed to write to file {path} in self.base_dir {self.base_dir}: {e}")

    def read_file(self, file_path: str) -> str:
        """
        Read data from a file, automatically resolving relative paths against self.base_dir.

        Args:
            file_path (str): Path to the file to read. Can be absolute or relative.

        Returns:
            str: File contents as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If permission is denied.
            Exception: For other unforeseen I/O errors.
        """
        try:
            # If path is not absolute, join with base_dir
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.base_dir, file_path)

            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied when reading file: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {e}")


# Example usage:
if __name__ == "__main__":
    relative_path = "subdir/example.txt"
    data = "This is sample data to write into the file.\n   hello\tf"
    
    try:
        file_created = FileManipulation().write_file( relative_path, data)
        print(f"File successfully written to: {file_created}")
        content = FileManipulation().read_file(file_created)
        print("Read file content:")
        print(content)

    except Exception as err:
        print(f"Operation failed: {err}")