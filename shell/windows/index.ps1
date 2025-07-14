# PowerShell Prompt Processing Script
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName PresentationFramework

function Show-MessageBox {
    param(
        [string]$Message,
        [string]$Title = "Prompt Processor",
        [string]$Type = "Information"
    )
    
    $IconType = switch ($Type) {
        "Error" { [System.Windows.Forms.MessageBoxIcon]::Error }
        "Warning" { [System.Windows.Forms.MessageBoxIcon]::Warning }
        "Information" { [System.Windows.Forms.MessageBoxIcon]::Information }
        default { [System.Windows.Forms.MessageBoxIcon]::Information }
    }
    
    [System.Windows.Forms.MessageBox]::Show($Message, $Title, [System.Windows.Forms.MessageBoxButtons]::OK, $IconType)
}

try {
    # Get selected text from clipboard
    $selectedText = Get-Clipboard -Raw
    if (-not $selectedText) {
        Show-MessageBox -Message "Error: No text in clipboard" -Type "Error"
        exit 1
    }

    # Define Python and script paths
    $pythonBin = "python"
    $scriptPath = "..\..\main.py"

    # Get prompt types
    $promptTypesRaw = & $pythonBin $scriptPath -l 2>&1
    if ($LASTEXITCODE -ne 0) {
        Show-MessageBox -Message "Error: Failed to get prompt types`n$promptTypesRaw" -Type "Error"
        exit 1
    }

    # Process prompt types (remove _system_instruction suffix)
    $promptTypes = $promptTypesRaw -split "`n" | Where-Object { $_.Trim() -ne "" } | ForEach-Object { 
        $_.Replace("_system_instruction", "").Trim() 
    }

    if ($promptTypes.Count -eq 0) {
        Show-MessageBox -Message "Error: No prompt types found" -Type "Error"
        exit 1
    }

    # Show selection dialog
    $selectedType = $promptTypes | Out-GridView -Title "Select Prompt Type" -OutputMode Single
    if (-not $selectedType) {
        Show-MessageBox -Message "Cancelled: No prompt type selected" -Type "Information"
        exit 1
    }

    # Process the prompt
    $result = & $pythonBin $scriptPath -p $selectedType $selectedText 2>&1
    if ($LASTEXITCODE -ne 0) {
        Show-MessageBox -Message "Error: Failed to process prompt`n$result" -Type "Error"
        exit 1
    }

    # Copy result to clipboard
    $result | Set-Clipboard

    # Show success message
    Show-MessageBox -Message "Prompt processed and copied to clipboard successfully!" -Type "Information"
}
catch {
    Show-MessageBox -Message "Unexpected error: $($_.Exception.Message)" -Type "Error"
    exit 1
}