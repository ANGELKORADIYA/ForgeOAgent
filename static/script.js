let currentMode = 'simple';

/**
 * Initialize the application on page load
 */
window.addEventListener('DOMContentLoaded', function() {
    loadPromptTypes();
    
    // Add event listeners for mode radio buttons
    document.querySelectorAll('input[name="mode"]').forEach(function(radio) {
        radio.addEventListener('change', function(e) {
            currentMode = e.target.value;
            loadPromptTypes();
        });
    });
    
    // Initialize auth method
    toggleAuthMethod();
    
    // Add form submit event listener
    document.getElementById('promptForm').addEventListener('submit', handleFormSubmit);
});

/**
 * Load available prompt types from the API
 */
function loadPromptTypes() {
    const select = document.getElementById('promptType');
    select.innerHTML = '<option value="">Loading...</option>';
    const headers = {};
    
    fetch('/api/prompt-types?mode=' + currentMode, { headers: headers })
        .then(function(response) { 
            return response.json(); 
        })
        .then(function(data) {
            if (data.success) {
                select.innerHTML = '';
                if (data.prompt_types.length === 0) {
                    select.innerHTML = '<option value="">No types available</option>';
                } else {
                    data.prompt_types.forEach(function(type) {
                        const option = document.createElement('option');
                        option.value = type;
                        option.textContent = type;
                        select.appendChild(option);
                    });
                }
                showStatus('Loaded ' + data.count + ' prompt types', 'success');
            } else {
                select.innerHTML = '<option value="">Error loading types</option>';
                showStatus('Failed to load prompt types', 'error');
            }
        })
        .catch(function(error) {
            select.innerHTML = '<option value="">Error loading types</option>';
            showStatus('Error: ' + error.message, 'error');
        });
}

/**
 * Handle form submission
 * @param {Event} e - The submit event
 */
function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const authMethod = formData.get('auth_method');
    const data = {
        mode: formData.get('mode'),
        prompt_type: formData.get('prompt_type'),
        prompt_text: formData.get('prompt_text'),
        context: formData.get('context') || '',
        new_content: formData.get('new_content') === 'on'
    };
    
    // Determine authentication credentials based on selected method
    const apiKey = authMethod === 'api_key' ? formData.get('api_key') : null;
    const apiPassword = authMethod === 'password' ? formData.get('api_password') : null;
    
    // Show loading state
    document.getElementById('loading').classList.add('show');
    document.querySelector('.btn-primary').disabled = true;
    hideStatus();

    // Determine endpoint based on authentication method
    const endpoint = apiKey ? '/api/process-with-key' : '/api/process';
    
    // Prepare headers
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (apiPassword) {
        headers['X-API-PASSWORD'] = apiPassword;
    }
    if (apiKey) {
        data['api_key'] = apiKey;
    }
    
    // Make API request
    fetch(endpoint, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(data)
    })
    .then(function(response) { 
        return response.json();
    })
    .then(function(result) {
        if (result.success && result.result) {
            showResult(result.result, data.prompt_type, data.mode);
        } else {
            showStatus('Error: ' + (result.detail || result.error || 'Unknown error'), 'error');
        }
    })
    .catch(function(error) {
        showStatus('Error: ' + error.message, 'error');
    })
    .finally(function() {
        document.getElementById('loading').classList.remove('show');
        document.querySelector('.btn-primary').disabled = false;
    });
}

/**
 * Show the processing result in a new window
 * @param {string} result - The processed result
 * @param {string} promptType - The type of prompt used
 * @param {string} mode - The processing mode used
 */
function showResult(result, promptType, mode) {
    showResultInline(result, promptType, mode);
    // Try to open popup first+
    const resultWindow = window.open('', '_blank');
    
    // Check if popup was blocked
    if (!resultWindow || resultWindow.closed || typeof resultWindow.closed === 'undefined') {
        // Popup was blocked, show in current window
        showResultInCurrentWindow(result, promptType, mode);
        return;
    }
    
    const escapedResult = escapeHtml(result);
    
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Result - ${escapeHtml(promptType)}</title>
    <style>
        body {
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            max-width: 1000px;
            margin: 0 auto;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .metadata {
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .result-box {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: "Courier New", monospace;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        button:hover {
            background: #5568d3;
        }
        button.secondary {
            background: #e0e0e0;
            color: #333;
        }
        button.secondary:hover {
            background: #d0d0d0;
        }
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4caf50;
            color: white;
            padding: 15px 20px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            display: none;
            animation: slideIn 0.3s ease;
        }
        .notification.show {
            display: block;
        }
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    </style>
</head>
<body>
    <h1>📄 Result - ${escapeHtml(promptType)}</h1>
    <div class="metadata">Mode: <strong>${escapeHtml(mode)}</strong> | Generated: <strong>${new Date().toLocaleString()}</strong></div>
    <div class="result-box" id="resultBox">${escapedResult}</div>
    <div class="button-group">
        <button onclick="copyToClipboard()">📋 Copy to Clipboard</button>
        <button onclick="downloadResult()" class="secondary">💾 Download</button>
        <button onclick="window.close()" class="secondary">✖ Close</button>
    </div>
    <div class="notification" id="notification">Copied to clipboard!</div>
    <script>
        function copyToClipboard() {
            const text = document.getElementById("resultBox").textContent;
            navigator.clipboard.writeText(text).then(function() {
                const notification = document.getElementById('notification');
                notification.classList.add('show');
                setTimeout(function() {
                    notification.classList.remove('show');
                }, 2000);
            }).catch(function(err) {
                alert('Failed to copy: ' + err);
            });
        }
        
        function downloadResult() {
            const text = document.getElementById("resultBox").textContent;
            const blob = new Blob([text], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'result_${Date.now()}.txt';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        }
    </script>
</body>
</html>`;
    
    resultWindow.document.write(html);
}

/**
 * Escape HTML special characters
 * @param {string} text - The text to escape
 * @returns {string} The escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show a status message
 * @param {string} message - The message to display
 * @param {string} type - The type of message (info, error, success)
 */
function showStatus(message, type) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = 'status show ' + (type || 'info');
    setTimeout(function() { 
        hideStatus(); 
    }, 50000);
}

/**
 * Hide the status message
 */
function hideStatus() {
    document.getElementById('status').classList.remove('show');
}

/**
 * Show result inline on the same page (fallback for popup blockers)
 * @param {string} result - The processed result
 * @param {string} promptType - The type of prompt used
 * @param {string} mode - The processing mode used
 */
function showResultInline(result, promptType, mode) {
    // Remove existing result container if present
    const existingResult = document.getElementById('inlineResult');
    if (existingResult) {
        existingResult.remove();
    }
    
    const container = document.querySelector('.container');
    const resultDiv = document.createElement('div');
    resultDiv.id = 'inlineResult';
    resultDiv.className = 'inline-result';
    
    resultDiv.innerHTML = `
        <div class="result-header">
            <h2>📄 Result - ${escapeHtml(promptType)}</h2>
            <div class="result-metadata">
                Mode: <strong>${escapeHtml(mode)}</strong> | 
                Generated: <strong>${new Date().toLocaleString()}</strong>
            </div>
        </div>
        <div class="result-box" id="inlineResultBox">${escapeHtml(result)}</div>
        <div class="result-actions">
            <button onclick="copyInlineResult()" class="btn-primary btn-small">📋 Copy</button>
            <button onclick="downloadInlineResult()" class="btn-secondary btn-small">💾 Download</button>
            <button onclick="openInNewTab()" class="btn-secondary btn-small">🔗 Open in New Tab</button>
            <button onclick="closeInlineResult()" class="btn-secondary btn-small">✖ Close</button>
        </div>
    `;
    
    container.appendChild(resultDiv);
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Copy inline result to clipboard
 */
function copyInlineResult() {
    const text = document.getElementById('inlineResultBox').textContent;
    navigator.clipboard.writeText(text).then(function() {
        showStatus('Copied to clipboard!', 'success');
    }).catch(function(err) {
        showStatus('Failed to copy: ' + err.message, 'error');
    });
}

/**
 * Download inline result as text file
 */
function downloadInlineResult() {
    const text = document.getElementById('inlineResultBox').textContent;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'result_' + Date.now() + '.txt';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    showStatus('Downloaded successfully!', 'success');
}

/**
 * Try to open result in new tab (user gesture required)
 */
function openInNewTab() {
    const text = document.getElementById('inlineResultBox').textContent;
    const newWindow = window.open('', '_blank');
    
    if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
        showStatus('Please allow popups for this site to open in new tab', 'error');
        return;
    }
    
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Result</title>
    <style>
        body {
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            max-width: 1000px;
            margin: 0 auto;
            background: #f5f5f5;
        }
        pre {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: "Courier New", monospace;
        }
    </style>
</head>
<body>
    <pre>${escapeHtml(text)}</pre>
</body>
</html>`;
    
    newWindow.document.write(html);
}

/**
 * Close inline result display
 */
function closeInlineResult() {
    const resultDiv = document.getElementById('inlineResult');
    if (resultDiv) {
        resultDiv.remove();
    }
}

/**
 * Toggle between authentication methods
 */
function toggleAuthMethod() {
    const authMethod = document.querySelector('input[name="auth_method"]:checked').value;
    const passwordSection = document.getElementById('passwordSection');
    const apiKeySection = document.getElementById('apiKeySection');
    const passwordInput = document.getElementById('apiPassword');
    const apiKeyInput = document.getElementById('apiKey');
    
    if (authMethod === 'api_key') {
        apiKeySection.style.display = 'block';
        passwordSection.style.display = 'none';
        apiKeyInput.required = true;
        passwordInput.required = false;
        passwordInput.value = ''; // Clear password when switching
    } else {
        passwordSection.style.display = 'block';
        apiKeySection.style.display = 'none';
        passwordInput.required = true;
        apiKeyInput.required = false;
        apiKeyInput.value = ''; // Clear API key when switching
    }
}