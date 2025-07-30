import subprocess
import sys
import re
from typing import Dict, List, Any


def PIPInstallManager(packages: List[str]) -> Dict[str, Any]:
    """
    Install packages using pip with comprehensive security and error handling.
    
    Security Features:
    - Package name validation (alphanumeric, hyphens, underscores, dots only)
    - Command injection prevention
    - No shell execution
    - Whitelist-based package validation
    - Length limits on package names
    - Special character filtering
    """
    if not packages:
        return {"status": "success", "message": "No packages to install", "installed": []}
    
    # Security validation
    security_result = _validate_packages_security(packages)
    if not security_result["valid"]:
        return {
            "status": "security_error",
            "message": f"Security validation failed: {security_result['reason']}",
            "invalid_packages": security_result["invalid_packages"],
            "installed": [],
            "failed": []
        }
    
    print(f"📦 Installing packages: {', '.join(packages)}")
    print("=" * 50)
    
    installed_packages = []
    failed_packages = []
    
    for package in packages:
        try:
            # Double-check individual package before installation
            if not _is_package_name_safe(package):
                failed_packages.append({
                    "package": package,
                    "error": "Package name failed security validation"
                })
                print(f"🚫 Blocked unsafe package: {package}")
                continue
            
            print(f"🔧 Installing {package}...")
            
            # Use subprocess with explicit arguments (no shell=True)
            # This prevents command injection
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package, "--no-cache-dir"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                shell=False   # Critical: Never use shell=True
            )
            
            if result.returncode == 0:
                installed_packages.append(package)
                print(f"✅ Successfully installed {package}")
            else:
                failed_packages.append({
                    "package": package,
                    "error": result.stderr.strip()
                })
                print(f"❌ Failed to install {package}: {result.stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            failed_packages.append({
                "package": package,
                "error": "Installation timeout (5 minutes exceeded)"
            })
            print(f"⏰ Installation timeout for {package}")
            
        except Exception as e:
            failed_packages.append({
                "package": package,
                "error": str(e)
            })
            print(f"❌ Error installing {package}: {str(e)}")
    
    print("=" * 50)
    
    if failed_packages:
        print(f"⚠️  Installation completed with errors")
        print(f"✅ Installed: {len(installed_packages)} packages")
        print(f"❌ Failed: {len(failed_packages)} packages")
        return {
            "status": "partial_success",
            "installed": installed_packages,
            "failed": failed_packages,
            "message": f"Installed {len(installed_packages)} packages, {len(failed_packages)} failed"
        }
    else:
        print(f"🎉 All packages installed successfully!")
        return {
            "status": "success",
            "installed": installed_packages,
            "failed": [],
            "message": f"Successfully installed all {len(installed_packages)} packages"
        }


def _validate_packages_security(packages: List[str]) -> Dict[str, Any]:
    """
    Comprehensive security validation for package names.
    
    Returns:
        Dict with 'valid' boolean, 'reason' string, and 'invalid_packages' list
    """
    if not isinstance(packages, list):
        return {
            "valid": False,
            "reason": "Packages must be provided as a list",
            "invalid_packages": []
        }
    
    if len(packages) > 50:  # Reasonable limit
        return {
            "valid": False,
            "reason": "Too many packages requested (max 50)",
            "invalid_packages": []
        }
    
    invalid_packages = []
    
    for package in packages:
        if not _is_package_name_safe(package):
            invalid_packages.append(package)
    
    if invalid_packages:
        return {
            "valid": False,
            "reason": "Invalid or potentially unsafe package names detected",
            "invalid_packages": invalid_packages
        }
    
    return {
        "valid": True,
        "reason": "All packages passed security validation",
        "invalid_packages": []
    }


def _is_package_name_safe(package_name: str) -> bool:
    """
    Validate if a package name is safe for installation.
    
    Security checks:
    1. Type and basic validation
    2. Length limits
    3. Character whitelist (only safe characters)
    4. Command injection prevention
    5. Path traversal prevention
    6. Special pip syntax blocking
    """
    # Type check
    if not isinstance(package_name, str):
        return False
    
    # Length check
    if len(package_name) < 1 or len(package_name) > 100:
        return False
    
    # Whitespace check
    if package_name != package_name.strip():
        return False
    
    # Valid package name pattern (PyPI standard)
    # Allows: letters, numbers, hyphens, underscores, dots
    # Must start with letter or number
    valid_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$'
    if not re.match(valid_pattern, package_name):
        return False
    
    # Block dangerous characters and sequences
    dangerous_chars = [
        ';', '&', '|', '`', '$', '(', ')', '<', '>', 
        '"', "'", '\\', '/', '\n', '\r', '\t'
    ]
    
    if any(char in package_name for char in dangerous_chars):
        return False
    
    # Block command injection attempts
    dangerous_sequences = [
        '--', '&&', '||', ';', '|', '`', '$(',
        'rm ', 'del ', 'format', 'exec', 'eval',
        '../', '..\\', '/etc', '/bin', '/usr',
        'C:\\', '\\System32', '__import__'
    ]
    
    package_lower = package_name.lower()
    if any(seq in package_lower for seq in dangerous_sequences):
        return False
    
    # Block pip-specific dangerous options
    pip_dangerous = [
        '--upgrade-strategy', '--force-reinstall', '--no-deps',
        '--target', '--user', '--root', '--prefix', '--src',
        '--editable', '-e', '--find-links', '-f', '--index-url',
        '--extra-index-url', '--trusted-host', '--process-dependency-links'
    ]
    
    if any(opt in package_lower for opt in pip_dangerous):
        return False
    
    # Block URL-like patterns (prevent installing from arbitrary URLs)
    url_patterns = [
        'http://', 'https://', 'ftp://', 'file://',
        'git+', 'hg+', 'svn+', 'bzr+'
    ]
    
    if any(pattern in package_lower for pattern in url_patterns):
        return False
    
    # Block local file paths
    if package_name.startswith('.') or package_name.startswith('/') or package_name.startswith('\\'):
        return False
    
    # Block known malicious or system-critical package names
    blocked_packages = [
        'pip', 'setuptools', 'wheel', 'python', 'sys', 'os',
        'subprocess', 'exec', 'eval', '__builtin__', '__builtins__'
    ]
    
    if package_lower in blocked_packages:
        return False
    
    return True