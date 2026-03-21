import os
import re


class ODOO_REGEX:
    """Find Code Reference for generating odoo code use this class"""

    def __init__(self):
        self.path = "/home/userpc/workspace/odoo_18/community"
    
    def code_generate_ref(
        self, 
        regex: str, 
        near_path: str = None,
        max_results: int = 10,
        full_code_count: int = 3,
        context_lines: int = 10
    ):
        """Search on the given path from env or args parser and find which file includes the given regex
        
        Use:
            For generating odoo code first use this function to reference from base than create odoo code
        
        Args:
            regex (str): The regular expression to search for.
            near_path (str, optional): Path filter for prioritization (e.g., "account_").
            max_results (int, optional): Maximum number of results to return. Defaults to 10.
            full_code_count (int, optional): Number of files to return full content. Defaults to 3.
            context_lines (int, optional): Lines before/after match for remaining results. Defaults to 10.
        
        Returns:
            dict: A dictionary containing the content of found files with metadata.
        """
        search_path = self.path
        found_files = []
        
        try:
            # First pass: collect all matching files with priority scoring
            for root, _, files in os.walk(search_path):
                if '.venv' in root:
                    continue
                    
                for file in files:
                    if not (file.endswith(".py") or file.endswith(".xml") or file.endswith(".js")):
                        continue
                    
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            if re.search(regex, content, re.IGNORECASE):
                                # Calculate priority score
                                priority = self._calculate_priority(file_path, near_path)
                                found_files.append({
                                    'path': file_path,
                                    'content': content,
                                    'priority': priority
                                })
                    except Exception as e:
                        pass
            
            # Sort by priority (higher is better)
            found_files.sort(key=lambda x: x['priority'], reverse=True)
            
            # Limit to max_results
            found_files = found_files[:max_results]
            
            # Build result dictionary
            result = {}
            for idx, file_info in enumerate(found_files):
                file_path = file_info['path']
                content = file_info['content']
                
                if idx < full_code_count:
                    # Return full code for first N files
                    result[file_path] = {
                        'content': content,
                        'full_code': True,
                        'priority': file_info['priority'],
                        'result_number': idx + 1
                    }
                else:
                    # Return context around matches for remaining files
                    context = self._extract_context(content, regex, context_lines)
                    result[file_path] = {
                        'content': context,
                        'full_code': False,
                        'priority': file_info['priority'],
                        'result_number': idx + 1
                    }
            
            return result
        
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_priority(self, file_path: str, near_path: str = None):
        """Calculate priority score for file path based on near_path match
        
        Args:
            file_path (str): The file path to score.
            near_path (str, optional): Path filter for prioritization.
        
        Returns:
            int: Priority score (higher is better).
        """
        if not near_path:
            return 0
        
        priority = 0
        path_lower = file_path.lower()
        near_lower = near_path.lower()
        
        # Exact folder name match gets highest priority
        path_parts = path_lower.split(os.sep)
        for part in path_parts:
            if part == near_lower:
                priority += 100
            elif near_lower in part:
                priority += 50
        
        # Partial match in full path
        if near_lower in path_lower:
            priority += 10
        
        # Closer to root gets slight boost
        depth = file_path.count(os.sep)
        priority -= depth * 0.1
        
        return priority
    
    def _extract_context(self, content: str, regex: str, context_lines: int = 10):
        """Extract lines around regex matches with context
        
        Args:
            content (str): File content.
            regex (str): Regular expression to search for.
            context_lines (int): Number of lines before and after match.
        
        Returns:
            str: Extracted context around matches.
        """
        lines = content.split('\n')
        matched_ranges = set()
        result_lines = []
        
        # Find all matching line numbers
        for i, line in enumerate(lines):
            if re.search(regex, line, re.IGNORECASE):
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                
                # Add this range to matched ranges
                for j in range(start, end):
                    matched_ranges.add(j)
        
        # Convert to sorted list and extract lines
        matched_ranges = sorted(matched_ranges)
        
        if not matched_ranges:
            return "No matches found"
        
        # Build context with line numbers and separators
        prev_line = -2
        for line_num in matched_ranges:
            if line_num > prev_line + 1:
                result_lines.append(f"\n... (lines {prev_line + 2}-{line_num}) ...\n")
            result_lines.append(f"{line_num + 1:4d}: {lines[line_num]}")
            prev_line = line_num
        
        return '\n'.join(result_lines)


if __name__ == "__main__":
    odoo_regex = ODOO_REGEX()
    
    # Example usage with prioritization
    results = odoo_regex.code_generate_ref(
        regex="account.account",
        near_path="account_account",
        max_results=10,
        full_code_count=3,
        context_lines=10
    )
    
    # Display results
    for file_path, info in results.items():
        if isinstance(info, dict):
            print(f"\n{'='*80}")
            print(f"File: {file_path}")
            print(f"Result #: {info['result_number']}")
            print(f"Priority: {info['priority']}")
            print(f"Full Code: {info['full_code']}")
            print(f"{'='*80}")
            if info['full_code']:
                print(info['content'][:500] + "..." if len(info['content']) > 500 else info['content'])
            else:
                print(info['content'])
        else:
            print(f"\nError: {info}")
