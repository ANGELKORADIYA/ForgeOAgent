import sys
from io import StringIO

# Helper function to capture print output
def capture_print_output(func, *args, **kwargs):
    """Capture print output from a function"""
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        result = func(*args, **kwargs)
        output = captured_output.getvalue()
        return output, result
    except Exception as e:
        output = captured_output.getvalue()
        raise Exception(f"Function error: {str(e)}\nOutput: {output}")
    finally:
        sys.stdout = old_stdout