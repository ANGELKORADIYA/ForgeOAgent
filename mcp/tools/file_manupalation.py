import os

class FileManupulation:
    """Use This Class when file write and read must use this only"""
    
    def __init__(self):
        self.base_dir =  "/home/userpc/29/ForgeOAgent/logs/base_dir"
        os.makedirs(self.base_dir, exist_ok=True)

    def write_file(self,relative_path: str, data: str) -> str:
        """
        Write data to a file specified by self.base_dir and relative_path.
        Creates directories if they don't exist.
        
        Args:
            relative_path (str): Give relative path for saving files.
            data (str): data to be written in that path.
            relative_path and data must be given
        Returns:
            str: The full file path where data is written.
        
        Raises:
            Exception: If any unexpected error occurs during file operations.
        """
        try:
            # Construct full file path
            full_path = os.path.join(self.base_dir, relative_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write data to file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(data)
            
            return full_path
        
        except Exception as e:
            raise Exception(f"Failed to write to file {relative_path} in self.base_dir {self.base_dir}: {e}")

    def read_file(self,file_path: str) -> str:
        """
        Read data from a file, handling different exceptions.
        
        Args:
            file_path (str): Full path to the file to read.
        
        Returns:
            str: File contents as a string.
        
        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If permission is denied.
            Exception: For other unforeseen I/O errors.
        """
        try:
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
    base_dir = "/path/to/self.base_dir"
    relative_path = "subdir/example.txt"
    data = "This is sample data to write into the file."
    
    try:
        file_created = FileManupulation().write_file( relative_path, data)
        print(f"File successfully written to: {file_created}")
        
        content = FileManupulation().read_file(file_created)
        print("Read file content:")
        print(content)
    except Exception as err:
        print(f"Operation failed: {err}")